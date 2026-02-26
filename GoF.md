# Interpretacja Jakości Dopasowania (Goodness-of-Fit)

W programie AmideFit stosujemy trzy główne wskaźniki oceny jakości dopasowania modelu do danych eksperymentalnych. Poniżej znajduje się wyjaśnienie ich znaczenia oraz wskazówki interpretacyjne.

## 1. Chi-square ($\chi^2$) - Test Chi-kwadrat
Jest to suma kwadratów różnic między danymi a modelem, ważona niepewnością pomiaru (jeśli jest znana).

* **Matematyka:** $\chi^2 = \sum \frac{(y_{obs} - y_{calc})^2}{\sigma^2}$
* **Interpretacja:**
    * Im mniejsza wartość, tym lepiej.
    * Wartość ta zależy od liczby punktów pomiarowych i skali sygnału (absorbancji). Trudno porównywać $\chi^2$ między różnymi widmami, ale jest doskonała do porównywania różnych modeli (np. 3 piki vs 4 piki) dla *tego samego* widma.

## 2. Reduced Chi-square ($\chi^2_\nu$)
To $\chi^2$ podzielone przez liczbę stopni swobody (liczba punktów minus liczba zmiennych parametrów).

* **Interpretacja:** Jest to najbardziej rygorystyczna miara w statystyce.
    * W idealnym świecie dążymy do wartości $\chi^2_\nu \approx 1$.
    * Jeśli $\chi^2_\nu \gg 1$: Model nie opisuje danych wystarczająco dobrze (potrzeba więcej pików lub inny kształt).
    * Jeśli $\chi^2_\nu < 1$: Możliwe "overfitting" (zbyt dopasowanie) – model fituje szum zamiast sygnału.

## 3. $R^2$ (Współczynnik Determinacji)
Określa, jaki procent zmienności danych jest wyjaśniony przez model.

* **Interpretacja:** Najbardziej intuicyjny wskaźnik dla studentów.
    * **$R^2 = 1.000$**: Idealne dopasowanie (niemożliwe w eksperymencie).
    * **$R^2 > 0.995$**: Bardzo dobre dopasowanie (pożądane w analizie amidu I).
    * **$R^2 < 0.980$**: Dopasowanie podejrzane. Prawdopodobnie brakuje składowej w modelu lub linia bazowa jest źle dobrana.

## 4. RMSE (Root Mean Square Error)
Średni błąd kwadratowy (pierwiastek). Mówi nam, o ile średnio (w jednostkach Absorbancji) myli się nasz model w każdym punkcie.

* **Interpretacja:**
    * Jeśli RMSE = 0.002, oznacza to, że średnio nasza czerwona linia (Fit) mija się z niebieską (Exp) o 0.002 jednostki absorbancji.
    * Wartość ta powinna być zbliżona do poziomu szumów urządzenia.

---
**Co robić, gdy Fit jest zły?**
1.  Sprawdź **Residua** (żółta linia pod wykresem). Jeśli widzisz tam systematyczny kształt (np. "falkę"), oznacza to, że w tym miejscu brakuje piku.
2.  Zmień algorytm optymalizacji (np. na Nelder-Mead).
3.  Zwolnij lub zablokuj parametry (np. szerokość pików).