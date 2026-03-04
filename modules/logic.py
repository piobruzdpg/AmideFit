# modules/logic.py
import numpy as np
import pandas as pd
from lmfit import Parameters
from lmfit.models import GaussianModel, VoigtModel, LorentzianModel, PseudoVoigtModel
import json
import random
from scipy.signal import savgol_filter
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.interpolate import CubicSpline

# [POPRAWKA] Importujemy nowe słowniki z config.py
from modules.config import DEFAULT_CONFIG, PEAK_COLORS, STRUCTURE_RANGES_H2O, STRUCTURE_RANGES_D2O

class AmideLogic:
    def __init__(self):
        # Stan danych
        self.x_data = None
        self.y_data = None
        self.filepath = None
        self.solvent = "H2O"
        # Piki
        self.peaks = []
        self.peak_counter = 0

        # Historia (Undo)
        self.history = []

        # Mapowanie modeli
        # PseudoVoigt = Suma Gaussa i Lorentza z wagą (fraction)
        self.MODEL_MAP = {
            'Gaussian': GaussianModel,
            'Lorentzian': LorentzianModel,
            'Voigt': VoigtModel,  # Splot (Convolution) G i L
            'PseudoVoigt': PseudoVoigtModel  # Suma ważona G i L
        }

    # --- ZARZĄDZANIE DANYMI ---

    def load_data(self, filepath):
        """Wczytuje i parsuje dane"""
        self.filepath = filepath
        df = self._parse_file_smart(filepath)
        df = df.sort_values(by=0)
        self.x_data = df[0].values
        self.y_data = df[1].values
        self.peaks = []
        self.peak_counter = 0
        self.history = []

    def _parse_file_smart(self, filepath):
        with open(filepath, 'r') as f:
            sample = "".join([f.readline() for _ in range(5)])
        sep = ';' if ';' in sample else ('\t' if '\t' in sample else ',')
        decimal = ',' if (sep == ';' or (',' in sample and '.' not in sample)) else '.'
        try:
            df = pd.read_csv(filepath, sep=sep, decimal=decimal, header=None, engine='c')
            if df.shape[1] > 2: df = df.iloc[:, :2]
            df = df.apply(pd.to_numeric, errors='coerce').dropna()
            return df
        except Exception as e:
            raise ValueError(f"Błąd parsowania: {str(e)}")

    def save_state_to_history(self):
        if self.x_data is not None:
            # Kopiujemy x, y oraz robimy głęboką kopię słowników pików
            peaks_copy = [p.copy() for p in self.peaks]
            # Zapisujemy tuple: (x, y, peaks, peak_counter)
            self.history.append((self.x_data.copy(), self.y_data.copy(), peaks_copy, self.peak_counter))

    def undo(self):
        if self.history:
            state = self.history.pop()
            self.x_data = state[0]
            self.y_data = state[1]

            # Zabezpieczenie na wypadek, gdybyśmy mieli w historii stare stany (tylko x, y)
            if len(state) > 2:
                self.peaks = state[2]
                self.peak_counter = state[3]

            return True
        return False

# --- OBRÓBKA DANYCH ---
    # [NOWE] Wygładzanie Savitzky-Golay (Destrukcyjne - zmienia dane)
    def apply_smoothing(self, window_length):
        """Aplikuje filtr SG do danych"""
        if self.y_data is None: return

        # Logika Undo
        self.save_state_to_history()

        # Walidacja okna
        poly = DEFAULT_CONFIG['savgol_polyorder']  # 3
        try:
            window_length = int(window_length)
        except:
            window_length = 11

        if window_length % 2 == 0: window_length += 1  # Musi być nieparzyste
        if window_length <= poly: window_length = poly + 2

        # Aplikacja filtra
        try:
            self.y_data = savgol_filter(self.y_data, window_length=window_length, polyorder=poly)
            return True
        except Exception as e:
            print(f"Błąd wygładzania: {e}")
            return False

    # [NOWE] Interpolacja (Zagęszczanie)
    def apply_interpolation(self, factor=2):
        """Zwiększa rozdzielczość widma metodą Cubic Spline"""
        if self.x_data is None: return

        self.save_state_to_history()

        try:
            # 1. Tworzymy nową oś X (gęstszą)
            # Zachowujemy zakres (min, max), ale zwiększamy liczbę punktów
            num_points = len(self.x_data)
            new_num_points = int(num_points * factor) - (factor - 1)  # Żeby idealnie trafiało w krańce

            new_x = np.linspace(self.x_data.min(), self.x_data.max(), new_num_points)

            # Ważne: CubicSpline wymaga rosnącego X.
            # Nasze X w FTIR często maleje (np. 1700 -> 1600).
            # Musimy posortować do obliczeń, a potem ewentualnie odwrócić.

            if self.x_data[0] > self.x_data[-1]:  # Jeśli malejące (typowe IR)
                x_sorted = self.x_data[::-1]
                y_sorted = self.y_data[::-1]
            else:
                x_sorted = self.x_data
                y_sorted = self.y_data

            # 2. Budujemy Splajn
            cs = CubicSpline(x_sorted, y_sorted)

            # 3. Wyliczamy nowe Y
            # Sortujemy new_x rosnąco do obliczenia, potem odwracamy jeśli trzeba
            new_x_sorted = np.sort(new_x)
            new_y_sorted = cs(new_x_sorted)

            # Przywracanie kolejności malejącej (jeśli była)
            if self.x_data[0] > self.x_data[-1]:
                self.x_data = new_x_sorted[::-1]
                self.y_data = new_y_sorted[::-1]
            else:
                self.x_data = new_x_sorted
                self.y_data = new_y_sorted

            return True, len(self.x_data)

        except Exception as e:
            print(f"Błąd interpolacji: {e}")
            return False, 0

    def apply_crop(self, x_start, x_end):
        self.save_state_to_history()
        mask = (self.x_data >= min(x_start, x_end)) & (self.x_data <= max(x_start, x_end))
        if not any(mask): return False
        self.x_data = self.x_data[mask]
        self.y_data = self.y_data[mask]
        return True

    def apply_linear_baseline(self, x1, y1, x2, y2):
        self.save_state_to_history()
        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1
        baseline = m * self.x_data + c
        self.y_data = self.y_data - baseline

        # [NOWE] Wygładzanie Savitzky-Golay (Destrukcyjne - zmienia dane)
        def apply_smoothing(self, window_length):
            """Aplikuje filtr SG do danych"""
            if self.y_data is None: return

            # Logika Undo
            self.save_state_to_history()

            # Walidacja okna
            poly = DEFAULT_CONFIG['savgol_polyorder']  # 3
            try:
                window_length = int(window_length)
            except:
                window_length = 11

            if window_length % 2 == 0: window_length += 1  # Musi być nieparzyste
            if window_length <= poly: window_length = poly + 2

            # Aplikacja filtra
            try:
                self.y_data = savgol_filter(self.y_data, window_length=window_length, polyorder=poly)
                return True
            except Exception as e:
                print(f"Błąd wygładzania: {e}")
                return False

        # [NOWE] Interpolacja (Zagęszczanie)
        def apply_interpolation(self, factor=2):
            """Zwiększa rozdzielczość widma metodą Cubic Spline"""
            if self.x_data is None: return

            self.save_state_to_history()

            try:
                # 1. Tworzymy nową oś X (gęstszą)
                # Zachowujemy zakres (min, max), ale zwiększamy liczbę punktów
                num_points = len(self.x_data)
                new_num_points = int(num_points * factor) - (factor - 1)  # Żeby idealnie trafiało w krańce

                new_x = np.linspace(self.x_data.min(), self.x_data.max(), new_num_points)

                # Ważne: CubicSpline wymaga rosnącego X.
                # Nasze X w FTIR często maleje (np. 1700 -> 1600).
                # Musimy posortować do obliczeń, a potem ewentualnie odwrócić.

                if self.x_data[0] > self.x_data[-1]:  # Jeśli malejące (typowe IR)
                    x_sorted = self.x_data[::-1]
                    y_sorted = self.y_data[::-1]
                else:
                    x_sorted = self.x_data
                    y_sorted = self.y_data

                # 2. Budujemy Splajn
                cs = CubicSpline(x_sorted, y_sorted)

                # 3. Wyliczamy nowe Y
                # Sortujemy new_x rosnąco do obliczenia, potem odwracamy jeśli trzeba
                new_x_sorted = np.sort(new_x)
                new_y_sorted = cs(new_x_sorted)

                # Przywracanie kolejności malejącej (jeśli była)
                if self.x_data[0] > self.x_data[-1]:
                    self.x_data = new_x_sorted[::-1]
                    self.y_data = new_y_sorted[::-1]
                else:
                    self.x_data = new_x_sorted
                    self.y_data = new_y_sorted

                return True, len(self.x_data)

            except Exception as e:
                print(f"Błąd interpolacji: {e}")
                return False, 0

    # --- ZARZĄDZANIE PIKAMI ---

    def add_peak(self, x, y, model_type="Gaussian"):
        self.save_state_to_history()
        self.peak_counter += 1

        sigma = DEFAULT_CONFIG['initial_sigma']
        if model_type == 'Lorentzian':
            area = y * sigma * np.pi
        else:
            area = y * sigma * np.sqrt(2 * np.pi)

            # Automatyczne przypisanie struktury
        struct_guess = self._guess_structure(x)

        new_peak = {
            'id': f"p{self.peak_counter}",
            'type': model_type,
            'structure': struct_guess,  # <--- NOWE POLE
            'center': x,
            'sigma': sigma,
            'area': area,
            'color': random.choice(PEAK_COLORS),
            'lock_center': False, 'lock_sigma': False, 'lock_area': False,
            'gamma': sigma, 'fraction': 0.5, 'lock_extra': False
        }
        self.peaks.append(new_peak)
        return new_peak['id']

    def import_peaks_from_project(self, filepath):
        """
        Wczytuje listę pików z pliku JSON i dodaje je do obecnego projektu.
        Zachowuje obecne dane spektralne (x_data, y_data).
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)

            imported_peaks = state.get("peaks", [])

            if not imported_peaks:
                return 0  # Brak pików w pliku

            # Musimy nadać nowe ID, żeby nie było konfliktów
            for p in imported_peaks:
                self.peak_counter += 1
                # Zachowujemy parametry fizyczne, ale zmieniamy ID
                p['id'] = f"p{self.peak_counter}"
                # Opcjonalnie: Resetujemy kolor, żeby odróżnić, lub zostawiamy stary
                # p['color'] = random.choice(PEAK_COLORS)

                # Dodajemy do listy
                self.peaks.append(p)

            return len(imported_peaks)

        except Exception as e:
            raise ValueError(f"Błąd importu pików: {str(e)}")

    def delete_peak(self, index):
        if 0 <= index < len(self.peaks):
            del self.peaks[index]

    def update_peak_param(self, index, key, value):
        self.peaks[index][key] = value
        # --- NOWE: Aktualizacja struktury, gdy ręcznie wpiszesz lub przeciągniesz pozycję ---
        if key == 'center':
            self.peaks[index]['structure'] = self._guess_structure(value)

    def toggle_peak_lock(self, index, key):
        self.peaks[index][key] = not self.peaks[index].get(key, False)
        return self.peaks[index][key]

    # --- SILNIK FITUJĄCY ---

    def apply_offset(self, x_target):
        """Przesuwa widmo w osi Y tak, aby w punkcie x_target wartość wynosiła 0"""
        self.save_state_to_history()

        # Znajdź najbliższy indeks dla wartości x_target
        idx = (np.abs(self.x_data - x_target)).argmin()
        y_shift = self.y_data[idx]

        self.y_data = self.y_data - y_shift
        return y_shift  # Zwracamy wartość przesunięcia dla info

    # [POPRAWIONE v3 - FINAL] Linia Bazowa AsLS (Asymmetric Least Squares Smoothing)
    def apply_asls_baseline(self, lam=100000, p=0.001, niter=10):
        """
        Algorytm Eilersa & Boelensa (Wersja v3 - Czysta).
        - Wymusza float64 dla danych wejściowych.
        - Wymusza float64 dla macierzy różnicowej (usuwa FutureWarning).
        """
        if self.y_data is None: return False

        self.save_state_to_history()

        # 1. Konwersja danych na float64 (dla pewności solvera)
        y = self.y_data.astype(np.float64)
        L = len(y)

        # 2. Tworzenie macierzy różnicowej (2. rzędu)
        # Dodano dtype=np.float64, aby uniknąć warningu o rzutowaniu int->float
        D = sparse.diags([1, -2, 1], [0, 1, 2], shape=(L - 2, L), format='csc', dtype=np.float64)

        # 3. Obliczenie macierzy kary (D^T * D)
        D_sq = D.T.dot(D)

        # Wagi początkowe (wszystkie 1)
        w = np.ones(L)
        baseline = np.zeros_like(y)

        for i in range(niter):
            # Tworzenie macierzy wag
            W = sparse.spdiags(w, 0, L, L)

            # Równanie systemowe
            Z = W + lam * D_sq

            try:
                # Rozwiązanie układu równań
                baseline = spsolve(Z, w * y)
            except Exception as e:
                print(f"Błąd solvera w iteracji {i}: {e}")
                return False

            # Aktualizacja wag
            w = p * (y > baseline) + (1 - p) * (y < baseline)

        # Odjęcie obliczonej linii od sygnału
        self.y_data = y - baseline
        return True

    # [ZMODYFIKOWANE] Silnik Fitujący z obsługą metod i GoF
    def run_optimization(self, method='leastsq'):
        """
        Uruchamia fitowanie wybraną metodą.
        Dostępne metody lmfit: 'leastsq' (Levenberg-Marquardt), 'nelder', 'powell', 'cobyla'.
        """
        if not self.peaks or self.x_data is None:
            raise ValueError("Brak danych lub pików do fitowania.")
        self.save_state_to_history()
        composite_model = None
        params = Parameters()

        # Budowanie modelu (bez zmian)
        for p in self.peaks:
            prefix = f"{p['id']}_"
            ModelClass = self.MODEL_MAP.get(p['type'], GaussianModel)
            model = ModelClass(prefix=prefix)

            if composite_model is None:
                composite_model = model
            else:
                composite_model += model

            # Parametry (bez zmian)
            model.set_param_hint(prefix + 'center', value=p['center'], vary=not p.get('lock_center', False))
            model.set_param_hint(prefix + 'sigma', value=p['sigma'], min=1e-5, vary=not p.get('lock_sigma', False))
            model.set_param_hint(prefix + 'amplitude', value=p['area'], min=0, vary=not p.get('lock_area', False))

            if p['type'] == 'Voigt':
                model.set_param_hint(prefix + 'gamma', value=p.get('gamma', p['sigma']), min=1e-5,
                                     vary=not p.get('lock_extra', False))
            elif p['type'] == 'PseudoVoigt':
                model.set_param_hint(prefix + 'fraction', value=p.get('fraction', 0.5), min=0, max=1,
                                     vary=not p.get('lock_extra', False))

            params.update(model.make_params())

        # Uruchomienie Fitowania z wybraną metodą
        # method: 'leastsq' (Domyślny LM), 'nelder' (Nelder-Mead - robust), 'powell'
        try:
            result = composite_model.fit(self.y_data, params, x=self.x_data, method=method)
        except Exception as e:
            raise RuntimeError(f"Błąd krytyczny algorytmu {method}:\n{str(e)}")

        if not result.success:
            # Czasem lmfit nie rzuca wyjątku, ale zwraca success=False
            raise RuntimeError(f"Algorytm nie zbiegł do rozwiązania.\nPowód: {result.message}")

        # Aktualizacja wyników
        self._update_peaks_from_result(result)

        # Obliczanie statystyk GoF (Goodness of Fit)
        r2 = self._calculate_r2(self.y_data, result.best_fit)
        rmse = np.sqrt(np.mean((self.y_data - result.best_fit) ** 2))

        stats = {
            'chisqr': result.chisqr,
            'redchi': result.redchi,
            'r2': r2,
            'rmse': rmse,
            'nfev': result.nfev,  # Liczba iteracji
            'method': method
        }
        return stats

    def _calculate_r2(self, y_true, y_pred):
        """Pomocnicze obliczanie R^2"""
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - (ss_res / ss_tot)

    def _update_peaks_from_result(self, result):
        bv = result.best_values
        for p in self.peaks:
            prefix = f"{p['id']}_"

            if prefix + 'center' in bv: p['center'] = bv[prefix + 'center']
            if prefix + 'sigma' in bv: p['sigma'] = bv[prefix + 'sigma']
            if prefix + 'amplitude' in bv: p['area'] = bv[prefix + 'amplitude']

            # Pobieranie parametrów extra
            if p['type'] == 'Voigt' and prefix + 'gamma' in bv:
                p['gamma'] = bv[prefix + 'gamma']
            if p['type'] == 'PseudoVoigt' and prefix + 'fraction' in bv:
                p['fraction'] = bv[prefix + 'fraction']
            # --- NOWE: Ponowne przypisanie struktury po zmianie pozycji przez solver ---
            p['structure'] = self._guess_structure(p['center'])

    # --- WYLICZANIE KRZYWYCH ---

    def calculate_model_curves(self):
        if self.x_data is None: return None

        total_y = np.zeros_like(self.y_data)
        components = []

        for p in self.peaks:
            ModelClass = self.MODEL_MAP.get(p['type'], GaussianModel)
            model = ModelClass()

            # Budowanie parametrów lokalnych
            safe_sigma = max(p['sigma'], 1e-5)
            params = model.make_params(amplitude=p['area'], center=p['center'], sigma=safe_sigma)

            if p['type'] == 'Voigt':
                params.add('gamma', value=p.get('gamma', safe_sigma))
            elif p['type'] == 'PseudoVoigt':
                params.add('fraction', value=p.get('fraction', 0.5))

            y_c = model.eval(params, x=self.x_data)
            total_y += y_c
            components.append({'y': y_c, 'color': p['color'], 'id': p['id']})

        residuals = self.y_data - total_y if self.peaks else np.zeros_like(self.y_data)

        return {
            'total': total_y,
            'components': components,
            'residuals': residuals
        }

    # --- PERSYSTENCJA ---

    def get_project_state(self):
        return {
            "version": "1.1",
            "filepath": self.filepath,
            "x_data": self.x_data.tolist() if self.x_data is not None else [],
            "y_data": self.y_data.tolist() if self.y_data is not None else [],
            "peaks": self.peaks,
            "peak_counter": self.peak_counter
        }

    def load_project_state(self, state):
        self.filepath = state.get("filepath", "")
        self.x_data = np.array(state["x_data"])
        self.y_data = np.array(state["y_data"])
        self.peaks = state.get("peaks", [])
        self.peak_counter = state.get("peak_counter", 0)

    def prepare_export_dataframes(self):
        curves = self.calculate_model_curves()
        if not curves: return None, None

        # 1. Dane
        data_dict = {"Wavenumber": self.x_data, "Absorbance_Raw": self.y_data}
        for comp in curves['components']:
            data_dict[f"Peak_{comp['id']}"] = comp['y']
        data_dict["Fit_Sum"] = curves['total']
        data_dict["Residuals"] = curves['residuals']
        df_curves = pd.DataFrame(data_dict)

        # 2. Parametry
        total_area_all = sum(p['area'] for p in self.peaks)

        # --- NOWE: Obliczenie sumy pól tylko dla właściwych struktur Amidu I ---
        valid_area_amide = sum(
            p['area'] for p in self.peaks
            if 1600 <= p['center'] <= 1700 and p.get('structure', '') not in ["Side Chains", "Other", "Inny"]
        )

        param_rows = []
        for p in self.peaks:
            fwhm_factor = 2.0 if p['type'] == 'Lorentzian' else 2.35482
            fwhm = fwhm_factor * p['sigma']

            if p['type'] == 'Lorentzian':
                height = p['area'] / (max(p['sigma'], 1e-5) * np.pi)
            else:
                height = p['area'] / (max(p['sigma'], 1e-5) * np.sqrt(2 * np.pi))

            # Procenty całkowite (stare)
            perc_total = (p['area'] / total_area_all * 100) if total_area_all > 0 else 0

            # --- NOWE: Procenty wewnątrz pasma Amidu I (zgodne z wykresem) ---
            struct_full = p.get('structure', 'Other')
            if 1600 <= p['center'] <= 1700 and struct_full not in ["Side Chains", "Other", "Inny"]:
                perc_amide = (p['area'] / valid_area_amide * 100) if valid_area_amide > 0 else 0
            else:
                perc_amide = 0.0

            row = {
                "Peak ID": p['id'],
                "Structure": struct_full,
                "Type": p['type'],
                "Position": p['center'],
                "Height": height,
                "FWHM": fwhm,
                "Area": p['area'],
                "% Area (Total)": perc_total,
                "% Area (Amide I)": perc_amide
            }
            if 'gamma' in p: row['Gamma'] = p['gamma']
            if 'fraction' in p: row['Fraction'] = p['fraction']

            param_rows.append(row)

        df_params = pd.DataFrame(param_rows)
        return df_curves, df_params

    def get_second_derivative(self, window_length):
        """Zwraca x i y drugiej pochodnej (z odwróconym znakiem dla wygody widm IR)"""
        if self.y_data is None: return None, None

        # Walidacja okna (musi być nieparzyste i > polyorder)
        poly = DEFAULT_CONFIG['savgol_polyorder']
        try:
            window_length = int(window_length)
        except:
            window_length = 11

        if window_length % 2 == 0:
            window_length += 1  # Auto-korekta na nieparzystą

        if window_length <= poly:
            window_length = poly + 2 if (poly + 2) % 2 != 0 else poly + 3

        # Obliczenie pochodnej (deriv=2).
        # Mnożymy przez -1, żeby minima 2. pochodnej stały się maksimami (łatwiej szukać pików wizualnie)
        y_deriv = savgol_filter(self.y_data, window_length=window_length, polyorder=poly, deriv=2)

        return self.x_data, y_deriv

    def set_solvent(self, solvent_type):
        """Ustawia typ rozpuszczalnika (H2O lub D2O)"""
        if solvent_type in ["H2O", "D2O"]:
            self.solvent = solvent_type

# [ZMODYFIKOWANE] Zgadywanie struktury zależne od rozpuszczalnika
    # [ZMODYFIKOWANE] Zgadywanie struktury zależne od rozpuszczalnika
    def _guess_structure(self, center):
        """Przypisuje strukturę na podstawie położenia i wybranego rozpuszczalnika"""

        # Wybór odpowiedniej listy w zależności od stanu przełącznika
        ranges_to_use = STRUCTURE_RANGES_H2O if self.solvent == "H2O" else STRUCTURE_RANGES_D2O

        for (start, end, name) in ranges_to_use:
            if start <= center <= end:
                return name
        return "Inny"

    def convert_sigma_to_fwhm(self, sigma, model_type):
        """Przelicza Sigmę na FWHM zależnie od modelu"""
        factor = 2.0 if model_type == 'Lorentzian' else 2.35482
        return sigma * factor

    def update_peak_fwhm(self, index, fwhm_value):
        """Aktualizuje Sigmę na podstawie wpisanego FWHM"""
        model_type = self.peaks[index]['type']
        factor = 2.0 if model_type == 'Lorentzian' else 2.35482

        # Sigma = FWHM / factor
        new_sigma = fwhm_value / factor
        self.peaks[index]['sigma'] = new_sigma