# Kształty Pików w Spektroskopii: Modele Matematyczne

Wybór odpowiedniego modelu matematycznego do dekonwolucji widm (np. FTIR pasma amidowego I) nie jest tylko kwestią "estetycznego dopasowania" do punktów pomiarowych. Kształt piku niesie ze sobą głęboką informację fizykochemiczną o badanym układzie.

W programie **AmideFit-Py** dostępne są cztery podstawowe modele: **Gaussian**, **Lorentzian**, **Voigt** oraz **Pseudo-Voigt**.

---

## 1. Gauss (Gaussian)
Model oparty na rozkładzie normalnym. Cechuje się "ostrym" wierzchołkiem i szybko opadającymi ramionami (wąskie ogony).

* **Pochodzenie fizyczne (Poszerzenie niejednorodne):** Wynika z przypadkowych, statystycznych fluktuacji w otoczeniu cząsteczki. W widmach ciał stałych i cieczy (oraz białek) odpowiada za różnice w mikrośrodowisku poszczególnych oscylatorów (np. różne kąty lub odległości w wiązaniach wodorowych dla tej samej podstruktury). Odpowiada również za poszerzenie aparaturowe (rozdzielczość spektrometru).
* **Parametry:**
    * `Center`: Położenie maksimum ($x_c$).
    * `Area`: Całkowite pole powierzchni pod krzywą (proporcjonalne do stężenia oscylatorów).
    * `Sigma` ($\sigma$): Odchylenie standardowe. W modelu Gaussa szerokość połówkowa wynosi $FWHM = 2.355 \cdot \sigma$.
* **Zastosowanie:** Doskonały punkt wyjścia dla większości widm IR układów skondensowanych, amorficznych układów polimerowych i elastycznych białek.

## 2. Lorentz (Lorentzian)
Model oparty na rozkładzie Cauchy'ego. W porównaniu do Gaussa jest "ostrzejszy" na samym szczycie, ale ma bardzo szerokie ramiona (długie ogony), które powoli dążą do zera.

* **Pochodzenie fizyczne (Poszerzenie jednorodne):** Wynika bezpośrednio z zasady nieoznaczoności Heisenberga i skończonego czasu życia stanu wzbudzonego (naturalna szerokość linii). Poszerzenie to dominuje w gazach (zderzenia) oraz w układach o bardzo wysokim stopniu uporządkowania krystalicznego. W widmach białek pojawia się często przy silnym sprzężeniu dipolowym (np. sztywne agregaty amyloidowe).
* **Parametry:**
    * `Center` i `Area`: Jak wyżej.
    * `Sigma`: Tutaj jest równoznaczna z parametrem $\gamma$ (połowa szerokości połówkowej). $FWHM = 2 \cdot \sigma$.
* **Zastosowanie:** Rzadko stosowany jako samodzielny model do widm cieczy i roztworów, ponieważ jego szerokie ogony mają tendencję do sztucznego "podnoszenia" tła pod innymi pikami. Używany do wysoce krystalicznych próbek lub gazów.

## 3. Voigt (Splot: Lorentz * Gauss)
Voigt to dokładny, analityczny **splot (konwolucja)** funkcji Gaussa i Lorentza. Matematycznie jest to całka uwzględniająca jednoczesne występowanie poszerzenia jednorodnego i niejednorodnego. 


* **Parametry dodatkowe:** * `Gamma` ($\gamma$): Reprezentuje udział szerokości Lorentza.
    * `Sigma` ($\sigma$): Reprezentuje udział szerokości Gaussa.
* **Zastosowanie:** Idealnie oddaje fizyczną rzeczywistość większości pomiarów (kombinacja poszerzenia aparaturowego, niejednorodności próbki i naturalnego czasu życia). 
* **Wada:** Obliczanie analitycznego splotu w każdej iteracji fitowania jest niezwykle zasobożerne dla procesora, co przy wielu pikach może drastycznie spowolnić optymalizację.

## 4. Pseudo-Voigt (Suma: Lorentz + Gauss)
Ponieważ prawdziwy profil Voigta jest trudny obliczeniowo, w spektroskopii najczęściej używa się funkcji Pseudo-Voigta. Jest to po prostu **suma ważona** (kombinacja liniowa) funkcji Gaussa i Lorentza.

$$y = \eta \cdot L(x) + (1-\eta) \cdot G(x)$$

* **Parametry dodatkowe:**
    * `Fraction` ($\eta$): Udział funkcji Lorentza. Przyjmuje wartości od 0 do 1. 
        * `Fraction = 0` to czysty Gauss.
        * `Fraction = 1` to czysty Lorentz.
        * `Fraction = 0.5` to 50% udziału Gaussa i 50% Lorentza.
    * Obie funkcje składowe (Gauss i Lorentz) w tym modelu dzielą wspólną pozycję `Center`, pole `Area` i mają przeliczaną na bieżąco wspólną szerokość połówkową (FWHM).
* **Zastosowanie:** **Złoty standard w analizie chemometrycznej i dekonwolucji widm ATR-FTIR białek.** Oblicza się ułamek sekundy, a błąd w stosunku do prawdziwego profilu Voigta wynosi zazwyczaj poniżej 1%. Pozwala idealnie dopasować ramiona pików (dzięki frakcji Lorentza) i rdzeń (dzięki frakcji Gaussa).

---

### Praktyczna porada dla studentów
Zaczynając analizę pasma amidowego I, najlepiej wystartować od samego modelu **Gaussian**. Jeśli algorytm (np. Levenberg-Marquardt) zgłasza błędy dopasowania w obszarach "dolin" między pikami, warto zmienić model głównych składowych na **PseudoVoigt**. Pozwoli to algorytmowi zoptymalizować parametr `Fraction` dla poszczególnych struktur, co zniweluje błędy rezydualne na krawędziach pasm bez tworzenia sztucznych tworów matematycznych.