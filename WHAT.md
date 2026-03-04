# Project Hand-off: AmideFit-Py

**Data:** 2026-02-24
**Status:** Wersja Beta 0.9 (Feature Complete)
**Ostatni sukces:** Implementacja pełnego cyklu pracy: Fitowanie -> Eksport Excel -> Zapis/Odczyt Projektu (JSON).

---

## 1. Zrealizowane Funkcjonalności
* **Core Logic:**
    * Silnik fitujący oparty na `lmfit` (Levenberg-Marquardt).
    * Modelowanie matematyczne: Gauss (z architekturą gotową pod Voigta).
    * Obsługa więzów (Constraints): Blokowanie pozycji/szerokości/pola.
* **Data Management:**
    * Import: `.csv`, `.dpt`, `.txt` (inteligentny parser).
    * Eksport: Raport `.xlsx` (Arkusz danych widmowych + Arkusz parametrów z przeliczonym FWHM i Height).
    * Persystencja: Zapis i odczyt stanu projektu (`.json`), w tym danych binarnych i konfiguracji pików.
* **GUI & Workflow:**
    * Interfejs: CustomTkinter (Dark Mode).
    * Preprocessing: Przycinanie (Crop), Linia Bazowa (Linear).
    * Interaktywność: Klikanie na wykresie, edycja parametrów w tabeli, Undo/Redo.

## 2. TODO (Roadmap to v1.0)
* **Refaktoryzacja (PRIORYTET):** Podział monolitycznego pliku `main.py` na moduły:
    * `main.py` (Entry point).
    * `gui.py` (Klasa interfejsu).
    * `logic.py` (Przetwarzanie danych i fitowanie).
    * `config.py` (Stałe i konfiguracja).
* **Polishing (Opcjonalne):**
    * Dodanie wyboru typu piku (Gauss/Voigt) w GUI.
    * Wygładzanie Savitzky-Golay (podgląd).
    * Druga pochodna (pomoc w szukaniu pików).



# Project Hand-off: AmideFit-Py

**Data:** 2026-02-24
**Status:** Wersja RC1 (Release Candidate 1) - Modularna
**Ostatni sukces:** Pełna refaktoryzacja kodu do architektury MVC. Wydzielenie logiki (`modules/logic.py`), GUI (`modules/gui.py`) i konfiguracji (`modules/config.py`).

---

## 1. Architektura Projektu
* **Struktura katalogów:**
    * `main.py` - Punkt startowy (Launcher).
    * `modules/` - Pakiet z kodem źródłowym.
        * `logic.py` - Klasa `AmideLogic` (Matematyka, Dane, Lmfit).
        * `gui.py` - Klasa `AmideFitApp` (CustomTkinter, Matplotlib).
        * `config.py` - Stałe konfiguracyjne.
    * `requirements.txt` - Lista zależności.

## 2. Zrealizowane Funkcjonalności
* **Analiza:** Fitowanie (Levenberg-Marquardt), Obsługa pików (Gauss), Więzy (Locking).
* **Workflow:** Import (`.csv`, `.dpt`), Preprocessing (Crop, Linear Baseline), Eksport (`.xlsx`), Zapis Stanu (`.json`).
* **UI:** Nowoczesny Dark Mode, interaktywny wykres, historia Undo/Redo.

## 3. TODO (Plan na v1.1)
* **Wybór kształtu piku:** Dodać w GUI (ComboBox) możliwość wyboru profilu Voigta (logika w `logic.py` jest już na to gotowa).
* **Wspomaganie decyzji:** Implementacja podglądu drugiej pochodnej (2nd derivative) do znajdowania ukrytych pasm.
* **Wygładzanie:** Filtr Savitzky-Golay.


# Project Hand-off: AmideFit-Py

**Data:** 2026-02-25
**Status:** Wersja RC2 (Education Ready)
**Ostatni sukces:** Wdrożenie narzędzi analitycznych (GoF, Offset), wyboru algorytmów i modeli (Voigt/Lorentz) oraz zabezpieczeń przed błędami fitowania.

---

## 1. Zrealizowane Funkcjonalności (v1.1)
* **Zaawansowane Modele:**
    * Obsługa 4 kształtów pików: Gaussian, Lorentzian, Voigt, PseudoVoigt.
    * Dynamiczny panel parametrów (obsługa dodatkowych zmiennych: `gamma` i `fraction`).
* **Analiza i Statystyka:**
    * Wskaźniki jakości dopasowania (Goodness-of-Fit): $R^2$, RMSE, $\chi^2$ (wyświetlane na żywo nad wykresem).
    * Dokumentacja interpretacji wyników dla studentów (`GOF.md`).
* **Narzędzia:**
    * **Offset:** Interaktywne zerowanie widma w wybranym punkcie (kliknięcie na wykresie).
    * **Algorytmy:** Możliwość zmiany silnika optymalizacji (Levenberg-Marquardt, Nelder-Mead, Powell) w przypadku trudności ze zbieżnością.
* **User Experience:**
    * Inteligentna obsługa błędów fitowania z sugestiami rozwiązania problemu (np. "Zmień metodę na Nelder-Mead").

## 2. Architektura
* Podział na moduły: `logic` (Model), `gui` (View/Controller), `config`.
* Pełna separacja logiki obliczeniowej od interfejsu (MVC).

## 3. TODO (Roadmap to v1.2 & v2.0)
* **Custom Shapes (Monte Carlo):** Import własnych kształtów z plików (CSV/SPC) i fitowanie ich wkładu (skalowanie) – *Priorytet badawczy Piotra*.
* **Wspomaganie decyzji:** Podgląd drugiej pochodnej (2nd derivative) do wykrywania ukrytych pasm.
* **Wygładzanie:** Filtr Savitzky-Golay.


# Project Hand-off: AmideFit-Py

**Data:** 2026-02-25
**Status:** Wersja v1.2 (Education Release)
**Ostatni sukces:** Wdrożenie zaawansowanych narzędzi preprocessingu (Wygładzanie SG, Interpolacja) i analizy (2. Pochodna, Auto-struktury).

---

## 1. Zrealizowane Funkcjonalności
* **Preprocessing Suite (Obróbka):**
    * **Wygładzanie:** Filtr Savitzky-Golay z regulowanym oknem (usuwanie szumu).
    * **Interpolacja:** Cubic Spline (zagęszczanie punktów 2x dla gładszych krzywych).
    * **Standardowe:** Przycinanie (Crop), Offset (zerowanie), Linia Bazowa (Linear).
* **Analiza Widmowa:**
    * **2. Pochodna:** Wykres minimów wskazujący położenie ukrytych pasm (wspomaganie decyzji).
    * **Auto-Structure:** Automatyczne przypisywanie struktur drugorzędowych (Alpha/Beta/Coil) na podstawie pozycji piku.
* **Fitowanie:**
    * **Modele:** Gaussian, Lorentzian, Voigt, PseudoVoigt.
    * **Parametry:** Obsługa FWHM (zamiast samej Sigmy) w interfejsie.
    * **Algorytmy:** Levenberg-Marquardt, Nelder-Mead, Powell.
* **Raportowanie:**
    * Statystyki GoF ($R^2$, RMSE, $\chi^2$) na żywo.
    * Eksport do Excela z kolumnami Structure, Gamma, Fraction.

## 2. Architektura
* **MVC:** Podział na `modules/logic.py`, `modules/gui.py`, `modules/config.py`.
* **GUI:** CustomTkinter (Dark Mode), Matplotlib (Interaktywny).

## 3. TODO (Roadmap v2.0 - Research)
* **Custom Shapes (Monte Carlo):** Import własnych kształtów z plików (CSV/SPC) i fitowanie ich wkładu – *Funkcja eksperymentalna dla zaawansowanych badań*.


# Project Hand-off: AmideFit-Py

**Data:** 2026-02-25
**Status:** Wersja v1.3 (UX & Interactive)
**Ostatni sukces:** Wdrożenie interaktywnych kontrolek "Draggable Value" (zaciągnij, aby zmienić) z podglądem dopasowania na żywo.

---

## 1. Zrealizowane Funkcjonalności
* **User Experience (UX):**
    * **Draggable Inputs:** Pola numeryczne działające jak suwaki (Final Cut Pro style). Przeciąganie myszą zmienia wartość parametru.
    * **Live Preview:** Zmiana parametrów piku (Center, Sigma, Area) natychmiast odświeża wykres i residua.
    * **Inteligentna obsługa błędów:** Sugestie rozwiązań w przypadku niepowodzenia fitowania.
* **Analiza i Preprocessing:**
    * **Preprocessing:** Wygładzanie Savitzky-Golay, Interpolacja (Splajn), Offset, Crop.
    * **Wspomaganie decyzji:** 2. Pochodna (wykrywanie ukrytych pasm), Auto-przypisywanie struktur drugorzędowych.
* **Fitowanie:**
    * **Modele:** Gaussian, Lorentzian, Voigt, PseudoVoigt (z obsługą gamma/fraction).
    * **Algorytmy:** Levenberg-Marquardt, Nelder-Mead, Powell.
    * **Metryki:** Pełny panel GoF ($R^2$, RMSE, $\chi^2$).

## 2. Architektura (MVC + Widgets)
* `modules/logic.py`: Model danych, obliczenia matematyczne (`scipy`, `lmfit`).
* `modules/gui.py`: Główny kontroler widoku.
* `modules/config.py`: Stałe i konfiguracja (zakresy struktur, kolory).
* `modules/custom_widgets.py`: Niestandardowe elementy interfejsu (`DraggableEntry`).

## 3. TODO (Plan na jutro - v1.4)
* **Zaawansowana Linia Bazowa:** Implementacja algorytmów kontekstowych (np. Asymmetric Least Squares lub Rubberband), aby poprawnie oddzielić pasmo amidowe I od "ogona" amidu II bez wprowadzania sztucznych wielomianów.
* **Wykorzystanie pików innego fitowania:** zapisanie nie tylko samego projektu, ale także samych pików, które można wykorzystać jako startowe piki do fitowania innego pasma.
* **Przygotowanie skryptu:** Zamknięcie venv i plików projektu do jednej paczki, którą będzie można uruchomić na komputerze z Windows
* **Deep Research dotyczący położenia pasm amidu I:** 

## 4. Roadmap (Research v2.0)
* **Custom Shapes (Monte Carlo):** Import własnych kształtów z plików (CSV/SPC) i fitowanie ich wkładu.


# Project Hand-off: AmideFit-Py

**Data:** 2026-02-26
**Status:** Wersja v1.4 (Pre-deployment / Fine-tuning UX)
**Ostatni sukces:** Wdrożenie zaawansowanej linii bazowej (AsLS), narzędzia do importu pików (szablonowania) z innych projektów, interaktywnego Zoomu oraz pełna reorganizacja lewego panelu pod kątem ergonomii na dużych ekranach.

---

## 1. Zrealizowane Funkcjonalności (v1.4)
* **Zaawansowany Preprocessing:**
    * **Linia Bazowa AsLS:** Zaimplementowano algorytm *Asymmetric Least Squares Smoothing* (Eilers & Boelens) oparty na macierzach rzadkich (`scipy.sparse`). Idealnie oddziela pasmo Amidu I od nachodzących ogonów (np. Amidu II) bez konieczności ręcznego wybierania punktów. Rozwiązano problemy z osobliwością macierzy i typowaniem `float64`.
* **Workflow i Wydajność:**
    * **Szablonowanie (Import Pików):** Nowa opcja w menu "Plik", pozwalająca na wgranie wyfitowanych pików z jednego projektu (`.json`) na nowo wczytane widmo. Drastycznie przyspiesza analizę serii danych (np. temperaturowych czy stężeniowych).
* **Interfejs Użytkownika (UX):**
    * **Smart Zoom:** Wdrożono narzędzie powiększania obszaru (`RectangleSelector`) pod lewym przyciskiem myszy, z zabezpieczeniem wymuszającym zachowanie malejącego kierunku osi X (specyfika FTIR). Szybki reset widoku pod prawym przyciskiem myszy.
    * **Reorganizacja Panelu:** Uporządkowanie narzędzi w logiczny, pionowy stos (stack), poprawa czytelności i usunięcie mylących/nieaktywnych etykiet skrótów klawiszowych.

## 2. Architektura
* `modules/logic.py`: Rozbudowa o logikę AsLS (optymalizacja dla dużych macierzy) oraz bezpieczne kopiowanie słowników pików przy imporcie.
* `modules/gui.py`: Kompleksowy refaktor sekcji lewego panelu; wdrożenie interaktywnych widżetów matplotlib (`RectangleSelector`) z ominięciem problemów z utratą "focusu" okna.

## 3. TODO (Roadmap to v1.5 / Deployment)
* **Testowanie (Real-World Data):** Praca z aplikacją "na żywym organizmie" przed zajęciami ze studentami w celu wyłapania drobnych niedogodności UX.
* **Deep Research (Amide I):** Przegląd aktualnej literatury dotyczącej dokładnego położenia i interpretacji pasm struktury drugorzędowej w rejonie amidu I.
* **Deployment dla Labu:** Zamknięcie folderu z wirtualnym środowiskiem (`.venv`) i plikami projektu w archiwum ZIP oraz stworzenie prostego skryptu uruchamiającego (np. `.bat` dla Windowsa), aby aplikacja działała jak "portable" na komputerach studenckich.
* **ToolTipy:** Podpowiedzi nad przyciskami dotyczace znaczenia i mozliwych operacji myszą.


# Project Hand-off: AmideFit-Py

**Data:** 2026-02-26
**Status:** Wersja v1.5 (Student Release / Final UI)
**Ostatni sukces:** Finalizacja interfejsu (Tooltips, Ustawienia), wdrożenie wbudowanej pomocy (pliki .md w GUI) oraz precyzyjne sterowanie myszą z modyfikatorem Shift.

---

## 1. Zrealizowane Funkcjonalności (v1.5)
* **Wbudowana Baza Wiedzy:**
    * Menu "Pomoc" umożliwiające wyświetlanie plików Markdown (`PIK.md`, `FIT.md`, `PASMA.md`) bezpośrednio w oknie aplikacji, w formie czytelnych, przewijanych tekstów.
* **Ergonomia i UX (Gotowe na laby):**
    * **System Tooltipów:** Dymki z podpowiedziami nad wszystkimi przyciskami i kontrolkami (opóźnienie 0.5s), ułatwiające samodzielną pracę studentów.
    * **Precyzja Drag & Drop:** Dodano obsługę klawisza **Shift** podczas przeciągania wartości liczbowych (DraggableEntry), co spowalnia zmianę 10-krotnie, pozwalając na idealne wstrzelenie się w ułamki.
    * Zoptymalizowano bazową prędkość zmiany parametru `Area`, likwidując irytujące "skoki".
* **Środowisko i Chemometria:**
    * **Przełącznik Rozpuszczalnika (H₂O / D₂O):** Lewy panel pozwala teraz zadeklarować środowisko. Aplikacja dynamicznie przełącza się między dwoma precyzyjnymi słownikami zakresów dla Amidu I i Amidu I', poprawnie zgadując struktury nawet po przesunięciach izotopowych.
* **Personalizacja:**
    * Zmiana motywu (Jasny/Ciemny) w locie z poziomu menu.
    * Okienko "Ustawienia", pozwalające zmienić domyślne parametry sesji (np. startowa Sigma, domyślny kształt piku, wielkość okna SG).

## 2. Architektura
* `modules/custom_widgets.py`: Własna klasa `ToolTip` bez dodatkowych bibliotek, obsługa maski bitowej klawisza Shift w zdarzeniach myszy.
* `modules/config.py`: Rozdzielenie `STRUCTURE_RANGES` na osobne warianty hydratacyjne.

## 3. TODO (Roadmap to v2.0 - Research)
* **Custom Shapes (Monte Carlo):** Import własnych kształtów z plików (CSV/SPC) i fitowanie ich wkładu. Funkcja dedykowana wyłącznie pod zaawansowane badania naukowe, omijana w wersji dydaktycznej.
* **Wersja Portable:** Przygotowanie skryptu `.bat` i paczki `.zip` na komputery w pracowni studenckiej (Windows).


---

# Project Hand-off: AmideFit-Py

**Data:** 2026-03-04
**Status:** Wersja v1.6 (Final Polish / Lab Ready)
**Ostatni sukces:** Optymalizacja interfejsu pod kątem pracowni studenckiej (starsze monitory), rozbudowa systemu Undo o historię pików oraz wdrożenie funkcji ułatwiających raportowanie (procenty dla pasma Amidu I, eksport wykresów na białym tle).

---

## 1. Zrealizowane Funkcjonalności (v1.6)
* **Optymalizacja GUI (Pracownia):**
    * Wdrożono automatyczne skalowanie interfejsu (85%) dla ekranów o wysokości <= 768px (np. 720p).
    * Zamieniono lewy panel narzędziowy na przewijany (`CTkScrollableFrame`), co zapobiega ucinaniu przycisków na małych ekranach.
* **Dynamiczne Etykiety i Logika:**
    * Automatyczna aktualizacja przypisanej struktury drugorzędowej po każdym przesunięciu piku (Drag & Drop) oraz po zakończeniu fitowania algorytmem optymalizacyjnym.
    * Rozbudowany system Undo ("Cofnij"): Historia zapamiętuje teraz pełną listę i parametry dodanych pików, umożliwiając cofnięcie błędnego fitowania (np. gdy algorytm się "rozsypie").
* **Raportowanie i Eksport:**
    * **Procentowy udział struktur:** Etykiety na wykresie oraz plik `.xlsx` obliczają udziały procentowe z uwzględnieniem wyłącznie pików z zakresu Amidu I (1600-1700 cm⁻¹), ignorując łańcuchy boczne i inne pasma. W raporcie wyodrębniono kolumnę `% Area (Amide I)`.
    * **Smart Export PNG:** Zmodyfikowano domyślny zapis wykresu Matplotlib. Kliknięcie dyskietki tymczasowo odwraca kolory (białe tło, czarne czcionki i residua), generując plik idealny do druku bez zmiany ciemnego motywu (Dark Mode) w samej aplikacji.
    * **Nowa paleta kolorów:** Usunięto z palety barw jasne, znikające na białym tle kolory (żółty, jaskrawy zielony), zastępując je bardziej kontrastowymi odpowiednikami.

## 2. Architektura
* `modules/gui.py`: Przechwycenie zdarzeń zapisu Matplotlib (`custom_savefig`), integracja `CTkScrollableFrame`, modyfikacja rysowania etykiet tekstowych.
* `modules/logic.py`: Głębokie kopiowanie słowników pików do historii w metodzie `save_state_to_history`, rozbudowa eksportera DataFrame pod `.xlsx`.
* `modules/config.py`: Aktualizacja stałej `PEAK_COLORS` pod kątem czytelności i kontrastu na jasnym tle.