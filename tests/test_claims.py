"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Es gibt keine Zeit als Zahl; die Zahlen sind exakt oder Bänder."""

import math

import sbf_algorithm as A
import sbf_constants as C
import sbf_evaluation as ev
from sbf_scenario import complete_cost

S = ev.Settings


def test_readme_hand_instances():
    assert A.derangements_sieve(4) == 24 - 4 * 6 + 6 * 2 - 4 * 1 + 1 == 9
    assert A.sieve_rook(3, A.menage_board(3)) == (1, [1, 6, 9, 2]) and 6 - 12 + 9 - 2 == 1
    adj = [[False] * 4 for _ in range(4)]
    for i, j in ((0, 1), (0, 2), (1, 2), (2, 3), (3, 0)):
        adj[i][j] = True
    assert A.ham_sieve(4, adj)[0] == A.ham_dp(4, adj)[0] == A.ham_brute(4, adj) == 1
    assert A.ham_sieve(5, [[i != j for j in range(5)] for i in range(5)])[0] == 24 == math.factorial(4)
    assert A.surjections_sieve(4, 2) == 14 == 2 ** 4 - 2 and A.legendre_sieve(30, [2, 3])[0] == 30 - 15 - 10 + 5 == 10


def test_readme_menage_sequence():
    assert A.menage_numbers(12) == [1, 0, 0, 1, 2, 13, 80, 579, 4738, 43387, 439792, 4890741, 59216642]
    assert [A.assignments_brute(n, A.menage_board(n)) for n in range(3, 9)] == [1, 2, 13, 80, 579, 4738]
    assert A.rook_numbers(6, A.menage_board(6)) == [1, 12, 54, 112, 105, 36, 2]


def test_readme_terms_table():
    rows = ev.terms_rows()
    assert [(r["Brett"], r["n"], r["verbotene Felder"], r["Teilmengen 2^|F|"], r["nichtangreifend"], r["Turmzahlen ungleich 0"], r["Zuordnungen"]) for r in rows] == [
        ("Hauptdiagonale", 10, 10, 1024, 1024, 11, 1334961),
        ("Ménage-Brett", 10, 20, 1048576, 15127, 11, 439792),
        ("Zufallsbrett 20 %", 8, 12, 4096, 235, 7, 6620),
        ("Zufallsbrett 40 %", 8, 19, 524288, 2737, 8, 2068),
        ("Zufallsbrett 15 %", 12, 27, 134217728, 45652, 11, 34256044)]


def test_readme_standard_instance():
    a = ev.analyse(S())
    info = a.info
    assert (info["cells"], info["value"], info["subsets"], info["nonattacking"], info["nonzero"]) == (14, 3000, 16384, 212, 5)
    assert round(ev.share_of_all(a), 4) == 0.0744 and info["total"] == 40320 and info["rook"] == [1, 14, 60, 92, 45, 0, 0, 0, 0]
    assert 40320 - 14 * 5040 + 60 * 720 - 92 * 120 + 45 * 24 == 3000          # Handrechnung des Siebs mit den Turmzahlen
    assert [w["Schritte"] for w in a.ways] == [5, 16384, 255, 233, 40320]


def test_readme_presets():
    s = ev.Settings
    expected = {"Standardfall: Zufallsbrett 8 × 8": 3000, "Derangements: Hauptdiagonale 10 × 10": 1334961, "Ménage-Zahlen: 9 Paare": 43387, "Leeres Brett: alle 7! Zuordnungen": 5040, "Volles Brett: keine Zuordnung": 0}
    for name, value in expected.items():
        assert ev.analyse(s(**C.PRESETS[name])).info["value"] == value, name
    menage = ev.analyse(s(**C.PRESETS["Ménage-Zahlen: 9 Paare"])).info
    assert (menage["cells"], menage["subsets"], menage["nonattacking"], menage["nonzero"]) == (18, 262144, 5778, 10)
    full = ev.analyse(s(**C.PRESETS["Rundreise: alle Kanten, 8 Städte"])).info
    assert (full["cycles"], full["best"], full["subsets"], full["sieve_ops"], full["hk_states"], full["hk_transitions"]) == (5040, (10, 8), 128, 15638, 449, 1351)
    partial = ev.analyse(s(**C.PRESETS["Rundreise: Kanten fehlen, Kosten bis 5"])).info
    assert (partial["cycles"], partial["best"], partial["hk_states"], partial["arcs"]) == (30, (18, 1), 226, partial["arcs"]) and partial["arcs"] < 56


def test_readme_sieve_against_held_karp():
    rows = ev.hk_rows()
    assert [(r["n"], r["Teilmengen im Sieb"], r["Rechenschritte Sieb"], r["Zustände Held–Karp"], r["Übergänge Held–Karp"]) for r in rows] == [
        (6, 32, 1580, 81, 165), (7, 64, 5154, 193, 486), (8, 128, 15638, 449, 1351), (9, 256, 45000, 1025, 3592), (10, 512, 124344, 2305, 9225)]
    assert [round(r["Schritte Sieb : Held–Karp"], 1) for r in rows] == [9.6, 10.6, 11.6, 12.5, 13.5]
    assert [r["Hamiltonkreise"] for r in rows] == [120, 720, 5040, 40320, 362880]
    assert [r["Zustände Held–Karp"] for r in rows] == [1 + (n - 1) * 2 ** (n - 2) for n in range(6, 11)]


def test_readme_tsp_experiment():
    res = ev.tsp_experiment(35)
    assert (res["n"], res["cycles"], res["best"], res["hk"], res["brute"], res["ops"]) == (8, 5040, (8, 1), (8, 1), (8, 1), 15638)
    assert min(w for w, c in enumerate(res["poly"]) if c) == 8 and max(w for w, c in enumerate(res["poly"]) if c) == 39


def test_readme_float_table():
    rows = ev.float_rows()
    assert [round(r["relative Abweichung"] / 10 ** math.floor(math.log10(r["relative Abweichung"])), 1) if r["relative Abweichung"] else 0 for r in rows] == [0, 1.5, 2.1, 8.8, 3.2, 2.8]
    assert [math.floor(math.log10(r["relative Abweichung"])) if r["relative Abweichung"] else None for r in rows] == [None, -10, -7, -5, -2, 4]
    assert f"{rows[-1]['größter Summand']:.1e}" == "1.2e+64" and f"{rows[1]['größter Summand']:.2e}" == "4.38e+17"
    assert all(r["exakt (k!)"] == math.factorial(r["k = n"]) for r in rows)


def test_readme_surjections_and_legendre():
    assert A.surjections_sieve(10, 3) == 55980 and 3 ** 10 == 59049 and round(55980 / 59049, 3) == 0.948
    assert [round(A.surjections_sieve(10, k) / k ** 10, 4) for k in (3, 4, 5)] == [0.948, 0.7806, 0.5225]
    assert A.surjections_sieve(12, 3) == 519156 and 3 ** 12 == 531441 and round(519156 / 531441 * 100, 1) == 97.7
    assert A.legendre_sieve(1000, [2, 3, 5, 7]) == (228, 16) and A.legendre_brute(1000, [2, 3, 5, 7]) == 228


def test_readme_permanents_via_ryser():
    """Ryser-Sieb gegen Aufzählen: 2^n − 1 Summanden gegen n! Permutationen."""
    assert [2 ** n - 1 for n in (10, 12, 14)] == [1023, 4095, 16383] and [math.factorial(n) for n in (10, 12)] == [3628800, 479001600]
    full = [[1] * 8 for _ in range(8)]
    assert A.ryser(8, full) == (40320, 255) and A.permanent_dp(8, full)[0] == 40320


def test_app_text_limits_come_from_the_constants():
    assert (C.N_MAX, C.TOUR_N_MAX, C.R_MAX, C.FIELD_SIEVE_MAX, C.ENUM_ASSIGN_N, C.ENUM_TOUR_N) == (12, 10, 5, 16, 8, 8)
    assert (C.MENAGE_NS, C.MENAGE_BRUTE_N, C.HK_NS, C.TIME_NS, C.TSP_N, C.TSP_SHARE, C.TSP_R, C.FLOAT_KS) == (tuple(range(3, 13)), 8, (6, 7, 8, 9, 10), (8, 10, 12), 8, 100, 5, (10, 15, 20, 25, 30, 40))
    assert (C.PLAY_LIMIT_MIN, C.PLAY_LIMIT_MAX, C.PLAY_MAX, C.PLAY_BRUTE_LIMIT, C.TERMS_SEED) == (10, 1000, 12, 100_000, 100)
