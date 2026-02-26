# Metody Optymalizacji (Fitowania) w AmideFit-Py

Proces dopasowania krzywych (fitowania) to w rzeczywistości matematyczny problem minimalizacji błędu. Naszym celem jest znalezienie takich parametrów pików (pozycji, szerokości, pola), dla których różnica między widmem eksperymentalnym a modelem (czyli suma kwadratów residuów) jest jak najmniejsza.

W programie dostępne są trzy potężne algorytmy optymalizacyjne z biblioteki `SciPy/Lmfit`. Każdy z nich ma inne zastosowanie.

## 1. Levenberg-Marquardt (Domyślny)
Najpopularniejszy algorytm w spektroskopii. Działa w oparciu o gradienty (pochodne). 
* **Jak działa:** Łączy dwie metody. Z dala od minimum zachowuje się jak metoda najszybszego spadku (szybko zbiega w dół), a blisko minimum przełącza się na metodę Gaussa-Newtona (precyzyjnie trafia w sam dołek).
* **Kiedy używać:** W 90% przypadków. Jest bardzo szybki i wydajny przy dobrze rozdzielonych pikach i poprawnym zgadnięciu początkowym (initial guess).
* **Kiedy zawodzi:** Gdy piki silnie na siebie zachodzą lub model jest zbyt skomplikowany (np. same profile Voigta). Algorytm łatwo "utyka" w lokalnych minimach i może zgłosić błąd (np. niemożność odwrócenia macierzy).

## 2. Nelder-Mead (Metoda Simplexu)
Solidny algorytm bezgradientowy (nie liczy pochodnych, a jedynie porównuje wartości funkcji).
* **Jak działa:** Wyobraź sobie "amebę" (simplex) rozpiętą na parametrach, która pełza po powierzchni błędu, kurcząc się i rozciągając, aż "wpadnie" do najgłębszego dołka.
* **Kiedy używać:** Gdy metoda Levenberga-Marquardta wyrzuca błędy (np. ujemne sigmy, błąd maxfev). Nelder-Mead jest niezwykle odporny (robust) na trudne dane eksperymentalne, zaszumione widma i złe punkty startowe.
* **Kiedy zawodzi:** Jest znacznie wolniejszy niż LM. Z powodu braku precyzyjnego wyliczania gradientów, dopasowanie może być minimalnie mniej dokładne ("płytsze" osiągnięcie minimum). Zazwyczaj jednak różnica dla ludzkiego oka jest niedostrzegalna.

## 3. Powell
Kolejna metoda bezgradientowa (optymalizacja kierunkowa).
* **Jak działa:** Szuka minimum po kolei wzdłuż wektorów bazowych każdego z parametrów osobno (metoda poszukiwań kierunkowych), a następnie aktualizuje te kierunki w oparciu o znalezione minima.
* **Kiedy używać:** Świetna alternatywa, gdy model ma parametry o bardzo różnych rzędach wielkości lub silnie skorelowane (np. gdy zmiana szerokości jednego piku jest rekompensowana wzrostem drugiego). 
* **Praktyka:** Jeśli LM odrzucił fit, a Nelder-Mead dał "płaski" i nieładny wynik – użyj Powella.

### 💡 Workflow dla studenta:
1. Ustaw parametry ręcznie (suwakami) tak blisko, jak potrafisz.
2. Zawsze zaczynaj od **Levenberg-Marquardt**.
3. Jeśli wynik jest zły lub wyskoczył błąd, nie kasuj pików! Przełącz na **Nelder-Mead** i kliknij "Uruchom Fit" ponownie. Często uratuje to sytuację.