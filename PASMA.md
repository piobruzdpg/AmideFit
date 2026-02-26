# Analiza Widm FTIR Białek: Pasmo Amidowe I (1600 - 1700 cm⁻¹)

**Aktualizacja:** Wiosna 2026
**Kontekst:** Wytyczne do dekonwolucji pasm w programie AmideFit-Py w oparciu o najnowszą literaturę (post-2015) oraz badania nad agregacją białek.

## 1. Kluczowe Wnioski z Przeglądu Literatury

1.  **Ewolucja przypisań (Agregaty vs β-kartka):** Najważniejszą zmianą w ostatnich latach jest precyzyjne oddzielenie natywnej wewnątrzcząsteczkowej β-kartki (ok. 1630–1643 cm⁻¹) od nienatywnej, międzycząsteczkowej β-kartki tworzącej włókna amyloidowe i agregaty (bardzo wąskie i silne pasma w rejonie 1615–1630 cm⁻¹, najczęściej ~1620 cm⁻¹). 
2.  **Przesunięcia izotopowe (H₂O vs D₂O):** Wymiana protonów na deuter (H -> D) w wiązaniach peptydowych osłabia sprzężenia wibracyjne. Skutkuje to przesunięciem pasm w dół (tzw. pasmo Amidu I').
    * Struktury elastyczne i wyeksponowane na rozpuszczalnik (Pętle, Random Coil, zewnętrzne warstwy α-helisy) przesuwają się mocniej (nawet o 5-10 cm⁻¹).
    * Sztywne, osłonięte rdzenie hydrofobowe (wewnętrzne β-kartki, silne agregaty) przesuwają się słabiej (1-4 cm⁻¹).
3.  **Łańcuchy boczne (Side Chains):** Reszty aminokwasowe, szczególnie arginina (Arg), asparagina (Asn) i glutamina (Gln), posiadają własne drgania grup C=O i C=N, które mocno absorbują na krańcach pasma amidowego I (ok. 1580-1615 cm⁻¹ oraz 1670-1680 cm⁻¹). Należy uważać, aby nie pomylić ich z agregatami lub skrętem (turn).

## 2. Tabele Przypisań Struktur Drugorzędowych

*Uwaga: W programie AmideFit-Py przykrywające się zakresy są rozwiązywane poprzez priorytetyzację (kolejność na liście w konfiguracji).*

### Tabela 1: Pomiary w H₂O (Amide I)
| Zakres (cm⁻¹) | Struktura / Przypisanie | Charakterystyka |
| :--- | :--- | :--- |
| 1680 – 1695 | **β-kartka (Antyrównoległa)** | Słabe pasmo wysokoczęstościowe (rozszczepienie rezonansowe). |
| 1695 – 1720 | **Agregaty (Antyrównoległe)** | Często skorelowane z silnym pikiem przy ~1620 cm⁻¹. |
| 1665 – 1680 | **Zakręty (β-Turns)** | Nakładają się z pętlami i wysoką β-kartką. |
| 1658 – 1665 | **Helisa 3₁₀ / Pętle** | Struktury przejściowe, krótkożyciowe helisy. |
| 1650 – 1658 | **α-helisa** | Klasyczna, dobrze uformowana helisa. |
| 1640 – 1650 | **Nieuporządkowane (Random Coil)** | Pętle, silne oddziaływanie z rozpuszczalnikiem. |
| 1624 – 1640 | **β-kartka (Natywna)** | Główne pasmo struktury β. |
| 1615 – 1624 | **Agregaty (Intermolecular β)** | Amyloidy, silnie upakowane włókna nienatywne. |
| 1580 – 1615 | **Łańcuchy boczne (AA)** | Głównie Arg, Asn, Gln (drgania C=N, C=O). |

### Tabela 2: Pomiary w D₂O (Amide I')
| Zakres (cm⁻¹) | Struktura / Przypisanie | Charakterystyka |
| :--- | :--- | :--- |
| 1675 – 1690 | **β-kartka (Antyrównoległa)** | Przesunięta nieznacznie w dół. |
| 1690 – 1720 | **Agregaty (Antyrównoległe)** | Zazwyczaj słabo wymieniające H/D. |
| 1655 – 1675 | **Zakręty (β-Turns)** | Bardzo szeroki zakres. |
| 1650 – 1655 | **Helisa 3₁₀** | Wąski zakres, oddzielony od α-helisy. |
| 1640 – 1650 | **α-helisa** | Silne przesunięcie z 1655 ze względu na H/D exchange. |
| 1636 – 1645 | **Nieuporządkowane (Random Coil)** | Najsilniejsze przesunięcie, w pełni otwarte na D₂O. |
| 1620 – 1638 | **β-kartka (Natywna)** | Relatywnie stabilna, osłonięta przed rozpuszczalnikiem. |
| 1605 – 1620 | **Agregaty (Intermolecular β)** | Często nietknięte przez deuterację rdzenia. |
| 1580 – 1605 | **Łańcuchy boczne (AA)** | Przesunięte drgania reszt aminokwasowych. |