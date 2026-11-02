"""Randfälle: leere Eingaben, Grenzen der Regler, jede Aufgabe und jedes Brett bei den kleinsten Größen, Formatierung großer Zahlen."""

import pytest

import sbf_algorithm as A
import sbf_constants as C
import sbf_evaluation as ev
import sbf_scenario as S


def test_one_by_one_boards():
    assert A.sieve_rook(1, set())[0] == 1 and A.sieve_rook(1, {(0, 0)})[0] == 0
    assert A.ryser(1, [[1]])[0] == 1 and A.permanent_dp(1, [[0]])[0] == 0 and A.assignments_brute(1, {(0, 0)}) == 0


def test_two_by_two_boards():
    assert A.sieve_rook(2, {(0, 0), (1, 1)})[0] == 1 and A.sieve_rook(2, {(0, 0), (0, 1)})[0] == 0 and A.sieve_rook(2, {(0, 0)})[0] == 1
    assert A.rook_numbers(2, {(0, 0), (1, 1)}) == [1, 2, 1]


def test_zero_size_board():
    assert A.sieve_rook(0, set()) == (1, [1]) and A.ryser(0, []) == (1, 1) and A.permanent_dp(0, [])[0] == 1


def test_empty_digraph_has_no_hamilton_cycle():
    for n in (2, 3, 6):
        empty = [[False] * n for _ in range(n)]
        assert A.ham_sieve(n, empty)[0] == A.ham_dp(n, empty)[0] == A.ham_brute(n, empty) == 0
        poly, _ = A.tsp_sieve(n, [[None] * n for _ in range(n)], 3)
        assert sum(poly) == 0 and A.best_of_poly(poly) is None


def test_one_and_two_cities():
    assert A.ham_sieve(1, [[True]])[0] == A.ham_dp(1, [[True]])[0] == A.ham_brute(1, [[True]]) == 1 and A.ham_sieve(1, [[False]])[0] == 0
    two = [[False, True], [True, False]]
    assert A.ham_sieve(2, two)[0] == A.ham_dp(2, two)[0] == A.ham_brute(2, two) == 1
    assert A.ham_sieve(2, [[False, True], [False, False]])[0] == 0


def test_digraph_without_a_return_arc_has_no_cycle():
    n = 4
    adj = [[i == j - 1 for j in range(n)] for i in range(n)]            # nur 0→1→2→3, keine Rückkante
    assert A.ham_sieve(n, adj)[0] == A.ham_dp(n, adj)[0] == A.ham_brute(n, adj) == 0


def test_all_costs_equal_gives_a_single_exponent():
    n = 5
    cost = S.complete_cost(n, 3)
    poly, _ = A.tsp_sieve(n, cost, 3)
    assert [w for w, c in enumerate(poly) if c] == [15] and poly[15] == 24 and A.tsp_dp(n, cost)[0] == (15, 24)


def test_effective_n_caps_the_tour():
    assert S.effective_n("Zuordnung", 12) == 12 and S.effective_n("Rundreise", 12) == C.TOUR_N_MAX and S.effective_n("Zuordnung", 1) == C.N_MIN and S.effective_n("Rundreise", 99) == C.TOUR_N_MAX
    with pytest.raises(ValueError):
        S.effective_n("Unsinn", 5)


def test_make_board_kinds():
    assert S.make_board("Hauptdiagonale", 4, 99, 1) == A.diagonal_board(4) and S.make_board("Ménage-Brett", 5, 99, 1) == A.menage_board(5)
    assert S.make_board("Leeres Brett", 4, 99, 1) == set() and S.make_board("Volles Brett", 3, 0, 1) == A.full_board(3)
    assert S.make_board("Zufallsbrett", 6, 0, 1) == set() and S.make_board("Zufallsbrett", 6, 100, 1) == A.full_board(6)
    assert S.make_board("Zufallsbrett", 6, 30, 5) == S.make_board("Zufallsbrett", 6, 30, 5) != S.make_board("Zufallsbrett", 6, 30, 6)
    with pytest.raises(ValueError):
        S.make_board("Unsinn", 4, 10, 1)


def test_make_cost_ranges_and_shares():
    full = S.make_cost(6, 100, 4, 3)
    assert all(full[i][i] is None for i in range(6)) and all(1 <= full[i][j] <= 4 for i in range(6) for j in range(6) if i != j)
    assert all(x is None for row in S.make_cost(5, 0, 3, 3) for x in row) and S.make_cost(6, 60, 4, 3) == S.make_cost(6, 60, 4, 3)
    costs = {x for row in S.make_cost(8, 100, 5, 1) for x in row if x is not None}
    assert costs <= {1, 2, 3, 4, 5} and len(costs) >= 4


def test_huge_numbers_are_formatted_without_str_limits():
    assert ev.big_text(10 ** 5000).endswith("(5001 Stellen)") and ev.big_text(0) == "0"
    assert ev.sci_text(0) == "0" and ev.sci_text(0.5) == "0,50" and ev.sci_text(27646.99) == "2,8·10⁴"


@pytest.mark.parametrize("task", C.TASKS)
@pytest.mark.parametrize("board", C.BOARDS)
@pytest.mark.parametrize("n", [3, 4])
def test_every_task_and_board_works_at_the_smallest_sizes(task, board, n):
    a = ev.analyse(ev.Settings(task, board, n, 50, 2, 7))
    assert a.problems == [] and ev.verdict_answers(a)[0] == "success" and ev.way_rows(a)


def test_rundreise_with_too_many_cities_gets_a_note():
    a = ev.analyse(ev.Settings("Rundreise", "Zufallsbrett", 12, 100, 3, 1))
    assert a.n_eff == C.TOUR_N_MAX and a.notes and "höchstens 10 Städte" in a.notes[0] and a.info["cycles"] == 362880
    assert not ev.analyse(ev.Settings("Rundreise", "Zufallsbrett", 8, 100, 3, 1)).notes


def test_field_sieve_is_skipped_over_the_limit_and_run_below():
    over = ev.analyse(ev.Settings("Zuordnung", "Volles Brett", 5))
    row = next(r for r in ev.way_rows(over) if r["Weg"] == "Sieb über Feldmengen")
    assert row["Ergebnis"] == "–" and "übersprungen" in row["Prüfung"]
    under = ev.analyse(ev.Settings("Zuordnung", "Hauptdiagonale", 5))
    assert next(r for r in ev.way_rows(under) if r["Weg"] == "Sieb über Feldmengen")["Ergebnis"] == "44"


def test_enumeration_limits():
    assert next(r for r in ev.way_rows(ev.analyse(ev.Settings("Zuordnung", "Zufallsbrett", 9))) if r["Weg"].startswith("Aufzählen"))["Ergebnis"] == "–"
    assert next(r for r in ev.way_rows(ev.analyse(ev.Settings("Zuordnung", "Zufallsbrett", 8))) if r["Weg"].startswith("Aufzählen"))["Prüfung"] == "gleich"
    assert next(r for r in ev.way_rows(ev.analyse(ev.Settings("Rundreise", "Zufallsbrett", 9, 100))) if r["Weg"].startswith("Aufzählen"))["Ergebnis"] == "–"


def test_a_tour_with_no_cycle_is_reported():
    a = ev.analyse(ev.Settings("Rundreise", "Zufallsbrett", 6, 0, 3, 1))
    assert a.info["cycles"] == 0 and a.info["best"] == (None, 0) and "es gibt keinen Hamiltonkreis" in ev.verdict_answers(a)[1]
    assert [r["Ergebnis"] for r in ev.way_rows(a) if r["Frage"] == "Kosten"][:3] == ["keine Rundreise"] * 3


def test_playground_clamps_its_input():
    assert ev.legendre_play(1, [])["limit"] == C.PLAY_LIMIT_MIN and ev.legendre_play(10 ** 6, [3])["limit"] == C.PLAY_LIMIT_MAX and ev.legendre_play(100, [])["divisors"] == (2,)
    res = ev.machines_play(500, 0)
    assert (res["n"], res["k"]) == (C.PLAY_MAX, 1) and ev.machines_play(-1, 99)["n"] == 1
