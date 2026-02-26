# Product Requirements Document (PRD): AmideFit-Py

**Wersja:** 1.0  
**Data:** 2026-02-23  
**Odbiorca:** Zespół deweloperski (Piotr & Gemini)  
**Cel:** Stworzenie lekkiej, interaktywnej aplikacji w Pythonie do dekonwolucji widm FTIR (szczególnie pasma amidowego I) z naciskiem na kontrolę nad procesem fitowania i raportowania.

---

## 1. Wprowadzenie i Kontekst
Celem projektu jest zastąpienie ciężkiego oprogramowania komercyjnego (OPUS) oraz ogólnego (Fityk) narzędziem skrojonym pod konkretny workflow analizy struktury drugorzędowej białek. Aplikacja ma łączyć łatwość obsługi (GUI) z rygorem naukowym (pełna kontrola parametrów, statystyka).

**Kluczowe założenia:**
* Stack technologiczny: **Python 3.x + CustomTkinter (GUI) + Matplotlib (Wykresy) + Lmfit (Silnik obliczeniowy)**.
* Przejrzystość danych: Użytkownik musi widzieć residua i mieć wpływ na każdy etap obróbki.
* Parametryzacja: Funkcje pików definiowane przez **Pole Powierzchni (Area)**, a nie wysokość.

---

## 2. Wymagania Funkcjonalne

### 2.1. Import Danych (Data Ingestion)
* **Formaty:**
    * `.csv` / `.txt` (generyczne dane tekstowe).
    * `.dpt` (format zrzutowy z Bruker OPUS).
    * `.spc` (binarny format Thermo/Galactic - przy użyciu biblioteki `spc` lub `spectrochempy`).
* **Inteligentny Parser:**
    * Automatyczna detekcja separatora kolumn (przecinek, średnik, tabulator, spacja).
    * Automatyczna detekcja separatora dziesiętnego (kropka vs przecinek).
    * Standaryzacja wewnętrzna do `numpy.array` (float64).

### 2.2. Preprocessing (Obróbka wstępna)
* **Przycinanie (Trimming):** Możliwość wycięcia interesującego zakresu (np. 1750-1550 cm⁻¹ dla Amide I).
* **Offset:** Zerowanie widma względem wybranego punktu (interakcja: kliknięcie LPM na wykresie lub wpisanie wartości Y).
* **Linia Bazowa (Baseline Correction):**
    * Metoda 1: Liniowa (wskazanie 2 punktów na krańcach zakresu).
    * Metoda 2: Algorytmiczna (Asymmetric Least Squares - AsLS lub gumka "Rubberband").
    * Odejmowanie linii bazowej od widma przed fitowaniem.
* **Wygładzanie (Opcjonalnie):** Savitzky-Golay (z podglądem na żywo, aby nie "zgubić" informacji).

### 2.3. Detekcja i Definicja Pików
* **Wspomaganie decyzji:**
    * Wyświetlanie drugiej pochodnej (2nd derivative) na żądanie (overlay) w celu identyfikacji ukrytych pasm.
* **Dodawanie pików:**
    * Ręczne (kliknięcie na wykresie w miejscu maksimum).
    * Zdefiniowanie typu funkcji per pik: **Gauss** lub **Voigt** (Pseudo-Voigt).
* **Parametryzacja funkcji:**
    * Model matematyczny musi przyjmować `Amplitude` jako **Pole Powierzchni (Area)**.
    * Pozostałe parametry: `Center` (położenie), `Sigma`/`Gamma` (szerokość).

### 2.4. Fitowanie (Fitting Engine)
* **Interaktywność:** Możliwość ręcznego przesuwania wierzchołków pików ("drag & drop" lub suwaki) w celu ustalenia `initial guess`.
* **Algorytm:** Levenberg-Marquardt (metoda najmniejszych kwadratów).
* **Więzy (Constraints):**
    * Możliwość blokowania parametrów (np. ustalona pozycja piku).
    * Możliwość ustalania zakresów (np. szerokość > 0).

### 2.5. Wizualizacja i Ocena
* **Wykres główny:** Widmo surowe, widmo po preprocessingu, suma dopasowanych pików, poszczególne piki składowe.
* **Wykres rezydualny:** Wykres pod spodem pokazujący `(Dane - Model)`.
* **Wskaźniki jakości (Goodness of Fit):**
    * R² (Współczynnik determinacji).
    * Chi-square ($\chi^2$).
    * RMSE.

### 2.6. Eksport i Zapis Stanu
* **Raport Excel (.xlsx):**
    * Arkusz 1: Dane wykresów (X, Y_org, Y_preproc, Y_sum, Y_peak1, Y_peak2...).
    * Arkusz 2: Parametry pików (Pozycja, Pole, % Pola całkowitego, Szerokość, Wysokość) + Wskaźniki błędów.
* **Zapis Stanu (.json):**
    * Zapis pełnej konfiguracji: ścieżka do pliku źródłowego, parametry preprocessingu (punkty linii bazowej), lista pików z ich parametrami i statusami (zablokowany/wolny).
    * Umożliwia "Wczytaj parametry" do nowego widma.

---

## 3. Interfejs Użytkownika (UI/UX)
* **Framework:** CustomTkinter.
* **Motyw:** Systemowy (Dark/Light) lub "Scientific Dark" dla mniejszego zmęczenia oczu.
* **Responsywność:** Skalowalne okno, panel boczny o stałej szerokości.

## 4. Plan Implementacji (Milestones)

1.  **M1: Skeleton & Loader:** GUI layout, ładowanie plików, prosty wykres (Matplotlib).
2.  **M2: Preprocessing:** Implementacja linii bazowej i przycinania.
3.  **M3: Peak Logic:** Implementacja modeli matematycznych (Area-based) i ręcznego dodawania pików.
4.  **M4: Fitting Engine:** Podpięcie `lmfit`, optymalizacja, wykres residuów.
5.  **M5: Export & Polish:** Generowanie Excela, JSON, poprawki UX.

---

## 5. Uwagi Techniczne dla Dewelopera
* **Parsowanie liczb:** Użyć regex lub `pandas.read_csv` z detekcją separatora, następnie `str.replace(',', '.')`.
* **Matematyka:**
    * Dla Gaussa: $Area = Height \cdot \sigma \cdot \sqrt{2\pi}$. Model musi przeliczać to w locie, jeśli `scipy/lmfit` używa wysokości jako domyślnej amplitudy.
* **Biblioteki:** `NumPy`, `Pandas`, `Matplotlib`, `SciPy`, `Lmfit`, `OpenPyXL`.