# Siebformel – alles zählen, das Verbotene abziehen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-siebformel-demo.streamlit.app/)** -->

Stück 7 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1), `rationale-ef-demo` (Stück 2), `symbolische-methode-demo` (Stück 3), `semiring-rekursion-demo` (Stück 4), `multimengen-partitionen-demo` (Stück 5) und `beschriftete-strukturen-demo` (Stück 6); sie haben **aufgebaut**. Diese Demo geht den umgekehrten Weg: erst **alles** zählen, dann das **Verbotene** abziehen (Siebformel, Inklusion–Exklusion). Beispiele: Zuordnungen mit verbotenen Feldern (Turmzahlen, Ménage-Zahlen, Ryser-Sieb), Hamiltonkreise über Spaziergänge und TSP mit Polynomgewichten, jeweils gegen Held–Karp aus Stück 4 und gegen Aufzählen geprüft. Das Sieb spart Speicher, nicht Zeit, und es sollte mit ganzen Zahlen gerechnet werden.

## Warum dieses Problem

Verbote lassen sich schlecht aufbauen: Wer Zuordnungen ohne verbotene Paare erzeugen will, müsste jedes Verbot im Aufbau berücksichtigen. Die Siebformel rechnet dagegen: Zahl aller Objekte, minus die mit einem Verbot, plus die mit zweien, und so weiter. Die Summanden wachsen mit 2^k; nach der Zahl der Türme zusammengefasst bleiben bei Zuordnungen höchstens n + 1 Summanden (die Turmzahlen selbst muss man ausrechnen). Die Demo zeigt, wie stark (Experiment 2), dass das Sieb bei den Hamiltonkreisen keine Zeit spart (Experiment 3), dass es eine ganze Kostenverteilung liefert (Experiment 4) und dass es mit ganzen Zahlen gerechnet werden sollte (Experiment 5).

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt und quantifiziert:** Zuordnungen mit verbotenen Feldern: Sieb exakt, Terme wachsen mit 2^|F|, Kürzung durch Turmzahlen. Im Standardfall (8 × 8, 14 verbotene Felder): 16.384 Teilmengen, 212 nichtangreifend, **5 Turmzahlen ungleich 0**.
- **Der Plan-Hook zu Held–Karp war nur zur Hälfte richtig:** Das Sieb über Spaziergänge liefert dieselben Zahlen, rechnet aber **mehr**, nicht weniger (n = 10: 124.344 Rechenschritte gegen 9.225 Übergänge, etwa das 13,5-fache). Es spart Speicher (10 gespeicherte Zahlen gegen 2.305 Zustände).
- **Zahl korrigiert:** Phase 0 schätzte für Held–Karp bei n = 10 etwa 23.040 Übergänge und damit ein Verhältnis von etwa 5. Der exakt gezählte Wert ist **9.225**, das Verhältnis **13,5** (n = 6: 9,6).
- **Neu: Kostenverteilung.** Das TSP-Sieb mit Polynomgewichten liefert die Zahl der Hamiltonkreise je Gesamtkosten, nicht nur das Minimum (mit gepackten ganzen Zahlen gerechnet: die Verschiebung um B·Kosten Bit ersetzt die Polynommultiplikation).
- **Gleitkomma:** Bei den Hamiltonkreisen ist Gleitkomma nach einer unabhängigen Nachrechnung bis n = 14 exakt, ab n = 15 weicht das Ergebnis von der ganzen Zahl ab (relativ 1,6·10⁻⁹ bei n = 16); das kontrolliert vorführbare Versagen sind die Surjektionen von k auf k (relative Abweichung 1,5·10⁻¹⁰ bei k = 15, 2,8·10⁴ bei k = 40).
- **Die App-Zahlen weichen von Phase 0 ab** (feste, andere Seeds für die Zufallsbretter): z. B. Zufallsbrett 40 % mit n = 8: 19 verbotene Felder, 2.737 nichtangreifend, 8 Turmzahlen (Phase 0: 22 Felder, 4.514, 9). Aussage unverändert, Zahlen im Test.
- **Randfall im Code gefunden und behoben:** Das Ryser-Sieb gab für die leere Matrix (n = 0) 0 statt 1 zurück, weil die leere Spaltenmenge übersprungen wird; für n ≥ 1 trägt sie 0 bei. Die App beginnt bei n = 3, der Fall ist dort nicht erreichbar.
- **Falsche Handrechnung (meine, nicht der Code):** In einem Test hatte ich die Zustände der Teilmengen-DP für die Permanente mit 2 statt 3 Spaltenpaaren nach Zeile 2 gezählt; ein Test erwartete eine falsche Bezugsgröße für „weicht ab“. Beides im Test korrigiert, der Code war richtig.
- **Port:** Der Plan sah 9320 vor; die Demo läuft darauf.

## Modell

Ein **Brett** ist eine Menge verbotener Felder (Zeile, Spalte). `rook_numbers` zählt die Möglichkeiten, k nicht schlagende Türme auf die verbotenen Felder zu stellen (Zeile für Zeile mit Spaltenmaske); `sieve_rook` rechnet Σ(−1)^k·r_k·(n−k)!; `sieve_over_cells` summiert über alle Teilmengen verbotener Felder; `ryser` ist das Sieb über Spaltenmengen (Permanente); `permanent_dp` die Teilmengen-DP. Eine **Rundreise** ist eine Kostenmatrix (None = keine Kante): `ham_sieve` zählt Hamiltonkreise über geschlossene Spaziergänge in Teilmengen der Städte (ein Vektor als Speicher), `ham_dp` ist der Held–Karp-Zähler, `tsp_sieve` das Sieb mit Polynomgewichten (gepackt in eine ganze Zahl), `tsp_dp` Held–Karp mit Paar (Kosten, Zahl der besten). Dazu `surjections_sieve`, `legendre_sieve` und die Formeln für Derangements und Ménage-Zahlen. Die Formeln stehen im 📐-Expander der App.

## Methodik

- **Rechenwege in der App** (Experiment 1): Sieb mit Turmzahlen, Sieb über Feldmengen (bis 16 verbotene Felder), Ryser-Sieb, Teilmengen-DP, Formel (Derangements, Ménage, n!) und Aufzählen aller Permutationen (bis n = 8); bei der Rundreise Sieb über Spaziergänge, Held–Karp-Zähler und Aufzählen (bis n = 8) für die Zahl der Kreise, dazu Sieb mit Polynomgewichten, Held–Karp mit Paar-Semiring und Aufzählen für Kosten. Bei Abweichung zeigt die App einen Fehler statt einer Zahl.
- **Aufwand** wird als Zahl der Summanden, Zustände, Übergänge und Rechenschritte gezählt (exakt, getestet); die Zeit steht nur als Messung auf Klick.
- **Eingabe:** Aufgabe (Zuordnung oder Rundreise), Brett (Zufallsbrett, Hauptdiagonale, Ménage-Brett, leer, voll), Größe n (Rundreise höchstens 10), Anteil in Prozent, Kostenbereich r (1 bis 5), Seed. Instanzen sind deterministisch aus diesen Werten; die Adresszeile spiegelt die Einstellung.

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_algorithm.py`, `tests/test_verdicts.py` oder `tests/test_oracle_sbf.py`. Zeiten stehen in keinem Test; sie sind gemessen und gekennzeichnet.

| Frage | Befund |
|---|---|
| Handinstanzen | Derangements von 4: 4! − 4·3! + 6·2! − 4·1! + 1·0! = 9; Ménage n = 3: Turmzahlen 1, 6, 9, 2 und 6 − 12 + 9 − 2 = 1; Digraph 0→1, 0→2, 1→2, 2→3, 3→0: ein Hamiltonkreis (0→1→2→3→0); vollständiger Digraph mit 5 Städten: 24 = 4!; Surjektionen von 4 auf 2: 2⁴ − 2 = 14; Zahlen von 1 bis 30 ohne Teiler 2 und 3: 30 − 15 − 10 + 5 = 10 |
| Ménage-Zahlen (Experiment 2) | n = 0 bis 12: 1, 0, 0, 1, 2, 13, 80, 579, 4.738, 43.387, 439.792, 4.890.741, 59.216.642 (aus dem Gedächtnis, durch mehrere Wege bestätigt); Aufzählen n = 3 bis 8: 1, 2, 13, 80, 579, 4.738; Turmzahlen n = 6: 1, 12, 54, 112, 105, 36, 2 |
| Summanden schrumpfen (Experiment 2), feste Zufallsbretter | Hauptdiagonale n = 10: 10 Felder, 1.024 Teilmengen, alle nichtangreifend, 11 Turmzahlen; Ménage-Brett n = 10: 20 Felder, 1.048.576 / 15.127 / 11; Zufallsbrett 20 % n = 8: 12 Felder, 4.096 / 235 / 7; Zufallsbrett 40 % n = 8: 19 Felder, 524.288 / 2.737 / 8; Zufallsbrett 15 % n = 12: 27 Felder, 134.217.728 / 45.652 / 11 |
| Standardfall | Zufallsbrett 8 × 8, Anteil 20 %, Seed 35: 14 verbotene Felder, 3.000 Zuordnungen (7,44 % von 8!), Turmzahlen 1, 14, 60, 92, 45; 40.320 − 14·5.040 + 60·720 − 92·120 + 45·24 = 3.000; Summanden: 5 (Turmzahlen), 16.384 (Feldmengen), 255 (Ryser), 233 (Teilmengen-DP), 40.320 (Aufzählen) |
| Sieb gegen Held–Karp (Experiment 3), vollständiger Digraph | Teilmengen im Sieb 32, 64, 128, 256, 512 für n = 6 bis 10; Rechenschritte 1.580, 5.154, 15.638, 45.000, 124.344; Held–Karp Zustände 81, 193, 449, 1.025, 2.305 = 1 + (n−1)·2^(n−2), Übergänge 165, 486, 1.351, 3.592, 9.225; Verhältnis der Schritte 9,6, 10,6, 11,6, 12,5, 13,5; Hamiltonkreise 120, 720, 5.040, 40.320, 362.880 = (n−1)!; Speicher: n Zahlen gegen die Zustände |
| TSP über das Sieb (Experiment 4), n = 8, Kosten 1 bis 5, alle Kanten, Seed 35 | 5.040 Hamiltonkreise mit Kosten von 8 bis 39, billigste Kosten 8, einmal, gleich Held–Karp und Aufzählen; 15.638 Rechenschritte |
| Gleitkomma (Experiment 5), Surjektionen k auf k | relative Abweichung 0, 1,5·10⁻¹⁰, 2,1·10⁻⁷, 8,8·10⁻⁵, 3,2·10⁻², 2,8·10⁴ für k = 10, 15, 20, 25, 30, 40 (Spalte „letzter Summand k^k“: 1,0·10¹⁰ bis 1,2·10⁶⁴; der größte Summand liegt bei 4,8·10¹⁰ für k = 10 bis 1,2·10⁶⁸ für k = 40); mit ganzen Zahlen stimmt es immer (= k!) |
| Surjektionen und Legendre (Spielwiese) | 10 Aufgaben auf 3 Maschinen: 55.980 von 59.049 lassen keine Maschine leer (94,8 %; bei k = 4, 5: 0,7806, 0,5225); 12 auf 3: 519.156 von 531.441 (97,7 %); Zahlen von 1 bis 1000 ohne Teiler 2, 3, 5, 7: 228 mit 16 Summanden |
| Presets | Hauptdiagonale 10: 1.334.961 Zuordnungen; Ménage-Zahl für 9 Paare: 43.387 (18 Felder, 262.144 Teilmengen, 5.778 nichtangreifend, 10 Turmzahlen); leeres Brett n = 7: 5.040; volles Brett n = 6: 0; Rundreise mit allen Kanten, 8 Städte: 5.040 Kreise, billigste Kosten 10, 8 Mal; mit 60 % der Kanten und Kosten bis 5: 30 Kreise, billigste Kosten 18, einmal |
| Zeit (nur gemessen, **nicht getestet**) | Auf dem Entwicklungsrechner (Phase 0): vollständiger Digraph n = 10: Sieb 0,03 s, Held–Karp-Zähler 0,01 s; n = 12: 0,18 s gegen 0,04 s; die App misst n = 8, 10, 12 auf Klick |

## Ehrliche Grenzen

- **Literaturwerte aus dem Gedächtnis:** Ménage-Folge, Ryser-Formel und die Spaziergangs-Variante der Siebformel für Hamiltonkreise (Karp, Bax, Kohn–Gottlieb–Kohn) wurden nicht an einer Quelle gelesen. Mehrere unabhängige Rechenwege stimmen überein; das ersetzt keine Quelle.
- **„Das Sieb schlägt die DP“ gilt nur für den Speicher:** Die Zeitmessung ist eine Python-Messung dieses Rechners und kein Satz über Algorithmen in anderen Sprachen.
- **Das Sieb über Feldmengen** läuft nur bis 16 verbotene Felder (2^16 Teilmengen); die Turmzahlen laufen für alle zulässigen Größen (n ≤ 12).
- **TSP nur mit kleinen ganzzahligen Kosten** (1 bis 5): Der Grad des Kostenpolynoms ist n·r; die Rundreise ist auf 10 Städte begrenzt (2^(n−1) Teilmengen).
- **Nur gerichtete Hamiltonkreise ab Stadt 0:** ein ungerichteter Kreis zählt in beide Richtungen doppelt; Björklunds Verfahren für ungerichtete Hamiltonkreise ist nicht Teil der Demo.
- **Aufzählen als Prüfer ist begrenzt** (Zuordnung und Rundreise bis n = 8); darüber prüfen sich Sieb, Teilmengen-DP und Formeln gegenseitig.
- **Das Gleitkomma-Beispiel ist ein Existenzbeweis des Fehlers**, kein Allgemeinbefund für Siebformeln; bei den Hamiltonkreisen ist Gleitkomma bis n = 14 exakt, ab n = 15 weicht das Ergebnis ab (relativ 1,6·10⁻⁹ bei n = 16).
- **Die Permanente ist #P-schwer**; das Ryser-Sieb mit 2^n − 1 Summanden ist ein Rechenweg bis n = 12, kein Härtebeweis.
- **Zeiten** sind Python-Messungen dieses Rechners; zwei Läufe unterscheiden sich.
- **Browser:** Seitentext, Zahlen, Diagrammbreiten, Preset-Klick und die Zeitmessung im Browser geprüft; Handy-Breite nicht.
- Alles simuliert, keine echten Daten.

## Verifikation

- **Kern:** Handinstanzen (Derangements von 4, Ménage n = 3, Digraph mit einem Kreis, Dreieck mit Kosten 1, 2, 3), Aufzählen aller Permutationen und Rundreisen, Zählen nichtangreifender Teilmengen für die Turmzahlen, Teilmengen-DP für Permanente und Held–Karp, Formeln, Laplace-Entwicklung der Permanente, Koeffizientenlisten für die gepackten Polynome, Eulers φ über das Sieb; 100 Zufallsbretter (n = 3 bis 7), 100 Zufallsdigraphen (n = 3 bis 8), 60 TSP-Instanzen (n = 3 bis 8, Kosten bis 2, 3, 5).
- **Eigenschaften:** Zuordnungen zwischen 0 und n!; mehr verbotene Felder geben nie mehr Zuordnungen; Zeilen, Spalten und Transponieren ändern nichts; Turmzahlen nichtnegativ mit r₁ = Zahl der Felder; Derangements plus Permutationen mit Fixpunkten = n!; Transponieren und Umbenennen der Städte ändern die Zahl der Kreise nicht; ein weiterer Pfeil nimmt keinen Kreis weg; Skalieren der Kosten verschiebt die Exponenten; das Kostenpolynom summiert sich zur Zahl der Kreise; Surjektionen höchstens k^n; Gleitkomma-Sieb versagt bei k = 40; gleiches Ergebnis in Prozessen mit verschiedenem `PYTHONHASHSEED`.
- **Randfälle:** 1 × 1-, 2 × 2- und 0 × 0-Brett, leerer Digraph, eine und zwei Städte, Digraph ohne Rückkante, alle Kosten gleich, Rundreise mit mehr als 10 Städten (Hinweis), Sieb über Feldmengen übersprungen, Aufzählen übersprungen, Rundreise ohne Hamiltonkreis, jede Aufgabe mit jedem Brett bei den kleinsten Größen, Grenzen der Spielwiese.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), alle Experimente, Permalink mit Müll und Grenzwerten, Rundreise mit zu vielen Städten, Zufalls-Seed-Knopf, jede Aufgabe mit jedem Brett, jedes Preset, Spielwiese, PDF an den Rändern; Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

940 Tests (`pytest tests`), zuletzt in etwa einer Minute auf dem Entwicklungsrechner (Messung, nicht getestet).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `sbf_algorithm.py` | Kern: Siebformeln, Turmzahlen, Ryser, Teilmengen-DP, Hamiltonkreise, TSP, Aufzählen |
| `sbf_constants.py` | Regler-Grenzen, Schwellen, Farben, Presets |
| `sbf_evaluation.py` | Analyse, Experimente, Verdikte, Formatierung |
| `sbf_layout.py` | Fester Kopf (Stylesheet) |
| `sbf_pdf_export.py` | PDF der aktuellen Aufgabe (fpdf2) |
| `sbf_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed |
| `sbf_scenario.py` | Bretter und Kostenmatrizen aus den Einstellungen |
| `sbf_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Verdikte, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Björklunds Verfahren (ungerichtete Hamiltonkreise), Möbius-Inversion auf Verbänden, Bonferroni-Ungleichungen:** nur als Ausblick.
- **Chromatisches Polynom und Tutte-Polynom (Sieb über Kantenmengen):** Stück 14 der Reihe.
- **Zählen nach Parameter mit Mittel und Streuung:** Stück 8; das Kostenpolynom ist hier schon eine Verteilung nach den Kosten, ohne die allgemeine Theorie.
- **Entscheidungsdiagramme gegen 2^k Teilmengen:** Stück 13.
- **Kosten über 5 und mehr als 10 Städte:** nicht berechnet.
- **Verwandte Demos:** `semiring-rekursion-demo` (Held–Karp als Netz, Paar-Semiring), `beschriftete-strukturen-demo` (Surjektionen als Zahlenprobe), `traveling-tournament-demo` (nur Name); nur Verweise.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
