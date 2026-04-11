# modules/bayes.py
import numpy as np
from lmfit import Parameters, Minimizer
import copy

try:
    import emcee
except ImportError:
    emcee = None


class BayesianFitter:
    def __init__(self, x_data, y_data, peaks, model_map):
        self.x = x_data
        self.y = y_data
        self.peaks = copy.deepcopy(peaks)  # Działamy na kopii, by nie psuć oryginału w razie błędu
        self.model_map = model_map
        self.params = Parameters()
        self.models = []

        self._build_model()

    def _build_model(self):
        """Buduje obiekty modeli i parametry, wymuszając granice (Priors) dla metod bayesowskich."""
        for p in self.peaks:
            prefix = f"{p['id']}_"
            ModelClass = self.model_map.get(p['type'])
            if not ModelClass:
                continue

            model = ModelClass(prefix=prefix)
            self.models.append(model)

            # Twarde ograniczenia (Priors) - MCMC i L-BFGS-B ich absolutnie wymagają!
            # Area nie może być ujemna, Sigma musi być większa od zera
            self.params.add(prefix + 'center', value=p['center'],
                            min=p['center'] - 50, max=p['center'] + 50,  # Ograniczamy "wędrówkę" piku
                            vary=not p.get('lock_center', False))

            self.params.add(prefix + 'sigma', value=p['sigma'],
                            min=1e-5, max=50.0,
                            vary=not p.get('lock_sigma', False))

            self.params.add(prefix + 'amplitude', value=p['area'],
                            min=1e-9, max=np.max(self.y) * 200,  # Pole musi być dodatnie
                            vary=not p.get('lock_area', False))

            if p['type'] == 'Voigt':
                self.params.add(prefix + 'gamma', value=p.get('gamma', p['sigma']),
                                min=1e-5, max=50.0, vary=not p.get('lock_extra', False))
            elif p['type'] == 'PseudoVoigt':
                self.params.add(prefix + 'fraction', value=p.get('fraction', 0.5),
                                min=0.0, max=1.0, vary=not p.get('lock_extra', False))

    def _eval_model(self, params):
        """Pomocnicza funkcja wyliczająca sumaryczne widmo z aktualnych parametrów"""
        total_y = np.zeros_like(self.y)
        for model in self.models:
            total_y += model.eval(params, x=self.x)
        return total_y

    def _calculate_stats(self, best_fit, method_name, nfev):
        """Liczy standardowe statystyki (GoF) dla wyników"""
        residuals = self.y - best_fit
        chisqr = np.sum(residuals ** 2)

        # R2
        ss_res = chisqr
        ss_tot = np.sum((self.y - np.mean(self.y)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # RMSE
        rmse = np.sqrt(np.mean(residuals ** 2))

        # Stopnie swobody
        nvarys = sum(1 for p in self.params.values() if p.vary)
        ndata = len(self.y)
        redchi = chisqr / max(1, (ndata - nvarys))

        return {
            'chisqr': chisqr,
            'redchi': redchi,
            'r2': r2,
            'rmse': rmse,
            'nfev': nfev,
            'method': method_name
        }

    def _update_peaks(self, best_values):
        """Zwraca zaktualizowaną listę pików po optymalizacji"""
        for p in self.peaks:
            prefix = f"{p['id']}_"
            if prefix + 'center' in best_values: p['center'] = best_values[prefix + 'center']
            if prefix + 'sigma' in best_values: p['sigma'] = best_values[prefix + 'sigma']
            if prefix + 'amplitude' in best_values: p['area'] = best_values[prefix + 'amplitude']

            if p['type'] == 'Voigt' and prefix + 'gamma' in best_values:
                p['gamma'] = best_values[prefix + 'gamma']
            if p['type'] == 'PseudoVoigt' and prefix + 'fraction' in best_values:
                p['fraction'] = best_values[prefix + 'fraction']
        return self.peaks

    # ==========================================
    # METODA 1: UPROSZCZONA (MAX ENTROPY)
    # ==========================================
    def run_maxent_simplified(self, alpha=0.05):
        """
        Minimalizuje funkcję celu Q = Chi^2 - alpha * Entropy
        Wymusza maksymalną entropię (gładkość) widma przy jednoczesnym dopasowaniu do danych.
        Algorytm L-BFGS-B dba o to, by pole powierzchni nie spadło poniżej zera.
        """

        def objective_function(params, x, data):
            model_y = np.zeros_like(data)
            for model in self.models:
                model_y += model.eval(params, x=x)

            # Klasyczny błąd dopasowania
            chisqr = np.sum((data - model_y) ** 2)

            # Entropia (np. Skilling-Bryan lub Shannon)
            # Zabezpieczamy wartości przed logarytmem z zera lub liczb ujemnych
            safe_y = np.clip(model_y, 1e-12, None)
            entropy = -np.sum(safe_y * np.log(safe_y))

            # Funkcja celu: minimalizujemy błąd ORAZ karzemy za brak entropii (Brzytwa Ockhama)
            # Im większe alpha, tym silniej program wygładza widmo
            Q = chisqr - (alpha * entropy)
            return Q

        # Tworzymy minimizer, mówiąc mu, że funkcja zwraca jeden SCALAR, a nie tablicę residuów
        minimizer = Minimizer(objective_function, self.params, fcn_args=(self.x, self.y))

        # Używamy L-BFGS-B z biblioteki SciPy, ponieważ świetnie radzi sobie z twardymi granicami (Bounds)
        result = minimizer.minimize(method='lbfgsb')

        if not result.success:
            raise RuntimeError(f"MaxEnt (L-BFGS-B) nie zbiegł: {result.message}")

        best_fit = self._eval_model(result.params)
        stats = self._calculate_stats(best_fit, 'MaxEnt (Uproszczona)', result.nfev)
        updated_peaks = self._update_peaks(result.params.valuesdict())

        return stats, updated_peaks

    # ==========================================
    # METODA 2: PEŁNY MCMC BAYES
    # ==========================================
    def run_mcmc_full(self):
        """
        Wnioskowanie Bayesowskie używające łańcuchów Markowa (MCMC) za pomocą 'emcee'.
        Bada przestrzeń parametrów w poszukiwaniu rozkładu prawdopodobieństwa.
        """
        if emcee is None:
            raise ImportError(
                "Aby użyć metody MCMC Bayes, musisz zainstalować pakiet 'emcee'.\nWpisz w terminalu: pip install emcee")

        # 1. KROK WSTĘPNY: Szybki fit klasykiem, aby dać MCMC dobry punkt startowy.
        # Jeśli MCMC zacznie w losowym miejscu, "wypalanie" (burn-in) zajmie wieki.
        def residual(params, x, data):
            return data - self._eval_model(params)

        pre_minimizer = Minimizer(residual, self.params, fcn_args=(self.x, self.y))
        pre_result = pre_minimizer.minimize(method='leastsq')

        # 2. GŁÓWNY KROK: MCMC
        # Używamy zoptymalizowanych parametrów startowych
        mcmc_minimizer = Minimizer(residual, pre_result.params, fcn_args=(self.x, self.y))

        # Parametry MCMC:
        # steps - liczba kroków "spaceru"
        # burn - ile początkowych kroków odrzucamy (zanim algorytm ustabilizuje się wokół minimum)
        # thin - bierzemy co n-tą próbkę, żeby zmniejszyć autokorelację
        result = mcmc_minimizer.minimize(method='emcee', steps=30000, burn=5000, thin=100, is_weighted=False, progress=False)

        # MCMC podaje najbardziej prawdopodobne wartości (mediany z rozkładu)
        best_fit = self._eval_model(result.params)

        # Ponieważ MCMC to próbkowanie, "liczba iteracji" (nfev) to po prostu steps
        stats = self._calculate_stats(best_fit, 'MCMC Bayes (Pełna)', 1500)
        updated_peaks = self._update_peaks(result.params.valuesdict())

        return stats, updated_peaks