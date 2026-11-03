"""Verdikte und Formatierung an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import math

import sbf_algorithm as A
import sbf_constants as C
import sbf_evaluation as ev

S = ev.Settings


def test_formatting():
    assert ev.de(3.14159, 3) == "3,142" and ev.big_text(0) == "0" and ev.big_text(1234567) == "1.234.567" and ev.big_text(10 ** 12) == "1,00·10¹² (13 Stellen)"
    assert ev.sci_text(0) == "0" and ev.sci_text(0.5) == "0,50" and ev.sci_text(1.46e-10) == "1,5·10⁻¹⁰" and ev.sci_text(27646.99) == "2,8·10⁴" and ev.sci_text(1.2e64) == "1,2·10⁶⁴"
    assert ev.share_text(0) == "0" and ev.share_text(0.0744) == "0,0744" and ev.share_text(0.0009) == "9,0·10⁻⁴"
    assert ev.pair_text((6, 1)) == "Kosten 6, 1 Mal" and ev.pair_text((8, 1234)) == "Kosten 8, 1.234 Mal" and ev.pair_text(None) == "keine Rundreise" and ev.pair_text((None, 0)) == "keine Rundreise"


def test_formula_values():
    assert ev.formula_value("Hauptdiagonale", 10) == ("Formel Σ(−1)^j·C(n,j)·(n−j)!", 1334961)
    assert ev.formula_value("Ménage-Brett", 9)[1] == 43387 and ev.formula_value("Leeres Brett", 7)[1] == 5040 and ev.formula_value("Volles Brett", 5)[1] == 0
    assert ev.formula_value("Zufallsbrett", 8) is None


def test_verdict_answers_for_the_standard_board():
    a = ev.analyse(S())
    kind, text = ev.verdict_answers(a)
    assert kind == "success" and text == ("8 Aufgaben auf 8 Maschinen, 14 verbotene Paare: 3.000 Zuordnungen. Das Sieb über alle Teilmengen verbotener Paare hätte 16.384 Summanden, davon sind 212 nichtangreifend; "
                                          "mit den Turmzahlen bleiben 5. 5 Rechenweg(e) geben je Frage dieselbe Zahl.")


def test_verdict_answers_for_named_boards():
    text = ev.verdict_answers(ev.analyse(S("Zuordnung", "Hauptdiagonale", 10)))[1]
    assert text.startswith("10 Aufgaben auf 10 Maschinen, 10 verbotene Paare: 1.334.961 Zuordnungen. Das Sieb über alle Teilmengen verbotener Paare hätte 1.024 Summanden, davon sind 1.024 nichtangreifend; mit den Turmzahlen bleiben 11.")
    assert ev.verdict_answers(ev.analyse(S("Zuordnung", "Ménage-Brett", 9)))[1].startswith("9 Aufgaben auf 9 Maschinen, 18 verbotene Paare: 43.387 Zuordnungen.")
    assert "hätte 1 Summand, davon sind 1 nichtangreifend; mit den Turmzahlen bleiben 1." in ev.verdict_answers(ev.analyse(S("Zuordnung", "Leeres Brett", 7)))[1]
    assert ev.verdict_answers(ev.analyse(S("Zuordnung", "Volles Brett", 6)))[1].startswith("6 Aufgaben auf 6 Maschinen, 36 verbotene Paare: 0 Zuordnungen. Das Sieb über alle Teilmengen verbotener Paare hätte 68.719.476.736 Summanden")


def test_verdict_answers_for_tours():
    assert ev.verdict_answers(ev.analyse(S("Rundreise", "Zufallsbrett", 8, 100, 3, 35))) == (
        "success", "8 Städte (gerichtet, ab Stadt 0): 5.040 Hamiltonkreise, die kleinsten Kosten sind 10, 8 Mal. Das Sieb braucht 128 Teilmengen und 8 gespeicherte Zahlen, Held–Karp 449 Zustände. 6 Rechenweg(e) geben je Frage dieselbe Zahl.")
    assert ev.verdict_answers(ev.analyse(S("Rundreise", "Zufallsbrett", 8, 60, 5, 35)))[1].startswith("8 Städte (gerichtet, ab Stadt 0): 30 Hamiltonkreise, die kleinsten Kosten sind 18, 1 Mal.")
    assert "es gibt keinen Hamiltonkreis, also auch keine Kosten" in ev.verdict_answers(ev.analyse(S("Rundreise", "Zufallsbrett", 6, 0, 3, 1)))[1]


def test_verdict_answers_reports_a_disagreement_as_an_error():
    a = ev.analyse(S())
    broken = ev.Analysis(a.settings, a.n_eff, a.ways, ["Zuordnungen: Sieb = 3, Ryser = 4 weichen ab"], [], a.info)
    assert ev.verdict_answers(broken) == ("error", "Die Rechenwege widersprechen sich: Zuordnungen: Sieb = 3, Ryser = 4 weichen ab")


def test_way_rows_flag_a_deviating_way():
    a = ev.analyse(S("Zuordnung", "Hauptdiagonale", 5))
    ways = [dict(w) for w in a.ways]
    ways[1]["Wert"], ways[1]["Text"] = 45, "45"
    rows = ev.way_rows(ev.Analysis(a.settings, a.n_eff, ways, [], [], a.info))
    assert rows[0]["Prüfung"] == "gleich" and rows[1]["Prüfung"] == "weicht ab" and rows[2]["Prüfung"] == "gleich"


def test_analyse_reports_a_wrong_way_as_a_problem(monkeypatch):
    monkeypatch.setattr(A, "permanent_dp", lambda n, allowed: (999, 1))
    a = ev.analyse(S("Zuordnung", "Hauptdiagonale", 5))
    assert a.problems and "Teilmengen-DP" in a.problems[0] and ev.verdict_answers(a)[0] == "error"
    monkeypatch.undo()
    monkeypatch.setattr(A, "ham_dp", lambda n, adj: (7, 1, 1))
    b = ev.analyse(S("Rundreise", "Zufallsbrett", 5, 100, 2, 1))
    assert b.problems and "Hamiltonkreise" in b.problems[0] and "Kosten" not in b.problems[0]


def test_way_rows_for_a_small_board():
    rows = ev.way_rows(ev.analyse(S("Zuordnung", "Hauptdiagonale", 5)))
    assert rows[:3] == [{"Frage": "Zuordnungen", "Weg": "Sieb mit Turmzahlen", "Ergebnis": "44", "Schritte": "6", "Prüfung": "gleich"},
                        {"Frage": "Zuordnungen", "Weg": "Sieb über Feldmengen", "Ergebnis": "44", "Schritte": "32", "Prüfung": "gleich"},
                        {"Frage": "Zuordnungen", "Weg": "Ryser-Sieb über Spaltenmengen", "Ergebnis": "44", "Schritte": "31", "Prüfung": "gleich"}]
    assert rows[-1] == {"Frage": "Zuordnungen", "Weg": "Aufzählen aller Permutationen", "Ergebnis": "44", "Schritte": "120", "Prüfung": "gleich"}


def test_share_of_all():
    assert abs(ev.share_of_all(ev.analyse(S("Zuordnung", "Hauptdiagonale", 5))) - 44 / 120) < 1e-15 and ev.share_of_all(ev.analyse(S("Rundreise"))) is None


def test_terms_rows_and_verdict():
    rows = ev.terms_rows()
    assert [(r["Brett"], r["n"], r["verbotene Felder"], r["Turmzahlen ungleich 0"]) for r in rows][:2] == [("Hauptdiagonale", 10, 10, 11), ("Ménage-Brett", 10, 20, 11)]
    assert rows[0]["Teilmengen 2^|F|"] == rows[0]["nichtangreifend"] == 1024 and rows[1]["Zuordnungen"] == 439792 and rows[0]["Zuordnungen"] == 1334961
    assert all(r["Teilmengen 2^|F|"] == 2 ** r["verbotene Felder"] and r["nichtangreifend"] <= r["Teilmengen 2^|F|"] for r in rows)
    kind, text = ev.verdict_terms(rows)
    assert kind == "success" and text.startswith("Zufallsbrett 40 % (n = 8): 524.288 Teilmengen verbotener Felder, davon nur 2.737 nichtangreifend und 8 Turmzahlen ungleich 0")


def test_menage_rows_check_and_verdict():
    rows = ev.menage_rows()
    assert [r["Ménage-Zahl (Sieb mit Turmzahlen)"] for r in rows] == [1, 2, 13, 80, 579, 4738, 43387, 439792, 4890741, 59216642]
    assert [r["Aufzählen"] for r in rows][:6] == [1, 2, 13, 80, 579, 4738] and rows[6]["Aufzählen"] is None
    assert ev.menage_check(rows) == []
    assert ev.verdict_menage(rows, []) == ("success", "Ménage-Zahlen für n = 3 bis 12: 1, 2, 13, 80, 579, …, 59.216.642. Sieb mit Turmzahlen, Formel der Turmzahlen und (bis n = 8) Aufzählen geben dieselben Zahlen.")
    assert ev.verdict_menage(rows, ["x"])[0] == "error"
    assert ev.menage_check([dict(rows[0], **{"Formel der Turmzahlen": 5})]) and ev.menage_check([dict(rows[0], Aufzählen=7)])


def test_hk_rows_check_and_verdict():
    rows = ev.hk_rows()
    assert [(r["n"], r["Teilmengen im Sieb"], r["Rechenschritte Sieb"], r["Zustände Held–Karp"]) for r in rows] == [(6, 32, 1580, 81), (7, 64, 5154, 193), (8, 128, 15638, 449), (9, 256, 45000, 1025), (10, 512, 124344, 2305)]
    # Übergänge von Held–Karp von Hand: (n−1) vom Anfang, danach für die Menge mit s Städten C(n−1, s−1) Mengen, s−1 mögliche letzte Städte, n−s Fortsetzungen
    assert [r["Übergänge Held–Karp"] for r in rows] == [(n - 1) + sum(math.comb(n - 1, s - 1) * (s - 1) * (n - s) for s in range(2, n)) for n in range(6, 11)]
    assert [r["Übergänge Held–Karp"] for r in rows][0] == 5 + 20 + 60 + 60 + 20 == 165 and rows[-1]["Übergänge Held–Karp"] == 9225
    assert [r["Hamiltonkreise"] for r in rows] == [math.factorial(r["n"] - 1) for r in rows] and ev.hk_check(rows) == []
    kind, text = ev.verdict_hk(rows, [])
    assert kind == "warning" and text.startswith("Für n = 10 (vollständiger Digraph, 362.880 Hamiltonkreise) braucht das Sieb 124.344 Rechenschritte und 10 gespeicherte Zahlen, Held–Karp 9.225 Übergänge und 2.305 Zustände: das Sieb rechnet etwa das 13,5-fache")
    assert ev.verdict_hk(rows, ["x"])[0] == "error" and ev.hk_check([dict(rows[0], Hamiltonkreise=7)])


def test_time_experiment_shape_and_verdict_text():
    rows = [{"n": 8, "Sieb (Sekunden)": 0.01, "Held–Karp (Sekunden)": 0.002}, {"n": 12, "Sieb (Sekunden)": 0.18, "Held–Karp (Sekunden)": 0.04}]
    assert ev.verdict_time(rows) == ("info", "Gemessen auf diesem Rechner (Python): n = 12: Sieb 0,180 s, Held–Karp 0,040 s (etwa das 4-fache). Eine Messung, keine Garantie.")
    res = ev.time_experiment()
    assert [r["n"] for r in res] == list(C.TIME_NS) and all(r["Sieb (Sekunden)"] >= 0 and r["Held–Karp (Sekunden)"] >= 0 for r in res)


def test_tsp_experiment_and_verdict():
    res = ev.tsp_experiment(35)
    assert res["n"] == 8 and res["cycles"] == 5040 == res["brute_steps"] and res["best"] == res["hk"] == res["brute"] == (8, 1) and res["problems"] == []
    assert ev.verdict_tsp(res) == ("success", "8 Städte, alle Kanten, Kosten 1 bis 5: 5.040 Hamiltonkreise mit Kosten von 8 bis 39; billigste Kosten 8, 1 Mal, gleich Held–Karp und Aufzählen. "
                                              "Das Kostenpolynom gibt die ganze Verteilung, nicht nur das Minimum.")
    assert ev.verdict_tsp(dict(res, problems=["x"]))[0] == "error"


def test_float_rows_check_and_verdict():
    rows = ev.float_rows()
    assert [r["k = n"] for r in rows] == list(C.FLOAT_KS) and ev.float_check(rows) == [] and all(r["exakt (k!)"] == math.factorial(r["k = n"]) for r in rows)
    assert rows[0]["relative Abweichung"] < 1e-12 and 1e-11 < rows[1]["relative Abweichung"] < 1e-9 and rows[-1]["relative Abweichung"] > 1e4
    assert [r["relative Abweichung"] for r in rows] == sorted(r["relative Abweichung"] for r in rows)
    kind, text = ev.verdict_float(rows, [])
    assert kind == "warning" and "1,5·10⁻¹⁰ bei k = 15, 8,8·10⁻⁵ bei k = 25 und 2,8·10⁴ bei k = 40 (größter Summand 1,2·10⁶⁸)" in text
    assert ev.verdict_float(rows, ["x"])[0] == "error" and ev.float_check([dict(rows[0], **{"exakt (k!)": 5})])


def test_legendre_and_machines_play():
    res = ev.legendre_play(30, (3, 2))
    assert res["divisors"] == (2, 3) and res["value"] == res["brute"] == 10 and res["terms"] == 4
    assert ev.verdict_legendre(res) == ("success", "Von den Zahlen 1 bis 30 sind 10 durch keinen der Teiler 2, 3 teilbar; das Sieb braucht 4 Summanden (2^2), Aufzählen 30 Prüfungen.")
    assert ev.verdict_legendre(dict(res, value=11))[0] == "error"
    m = ev.machines_play(10, 3)
    assert m == {"n": 10, "k": 3, "sieve": 55980, "all": 59049, "brute": 55980, "terms": 4}
    assert ev.verdict_machines(m) == ("success", "55.980 von 59.049 Zuordnungen von 10 Aufgaben auf 3 Maschinen lassen keine Maschine leer (94,8 %); das Sieb braucht 4 Summanden; Aufzählen bestätigt es.")
    big = ev.machines_play(12, 3)
    assert big["brute"] is None and "Aufzählen entfällt (zu viele Möglichkeiten)" in ev.verdict_machines(big)[1] and ev.verdict_machines(dict(m, brute=1))[0] == "error"
