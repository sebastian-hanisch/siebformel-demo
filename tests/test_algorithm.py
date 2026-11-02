"""Einheitentests des Rechenkerns an von Hand gerechneten Werten (DEMO-PLAYBOOK §1b)."""

import math

import pytest

import sbf_algorithm as A


def test_derangements_of_four_by_hand(hand_derangements_4):
    n = hand_derangements_4["n"]
    value, rook = A.sieve_rook(n, A.diagonal_board(n))
    assert rook == hand_derangements_4["rook"] and value == hand_derangements_4["value"] == 9
    assert A.derangements_sieve(4) == 9 and A.sieve_over_cells(4, A.diagonal_board(4)) == (9, 16, 16)       # alle 16 Teilmengen der Diagonale sind nichtangreifend


def test_menage_three_by_hand(hand_menage_3):
    n = hand_menage_3["n"]
    value, rook = A.sieve_rook(n, A.menage_board(n))
    assert rook == hand_menage_3["rook"] and value == hand_menage_3["value"] == 1
    assert A.assignments_brute(n, A.menage_board(n)) == 1 and A.menage_numbers(3) == [1, 0, 0, 1]


def test_menage_sequence_by_hand():
    assert A.menage_numbers(8) == [1, 0, 0, 1, 2, 13, 80, 579, 4738]
    assert [A.rook_numbers_cycle_formula(3, k) for k in range(4)] == [1, 6, 9, 2]


def test_sieve_over_cells_counts_non_attacking_subsets():
    # drei Felder in einer Zeile: nichtangreifend sind nur die leere Menge und die drei einzelnen
    assert A.sieve_over_cells(3, {(0, 0), (0, 1), (0, 2)}) == (6 - 3 * 2, 8, 4)
    assert A.rook_numbers(3, {(0, 0), (0, 1), (0, 2)}) == [1, 3, 0, 0]


def test_rook_numbers_by_hand():
    assert A.rook_numbers(2, {(0, 0), (1, 1)}) == [1, 2, 1] and A.rook_numbers(2, {(0, 0), (0, 1), (1, 0), (1, 1)}) == [1, 4, 2]
    assert A.rook_numbers(3, set()) == [1, 0, 0, 0]


def test_permanent_by_hand():
    allowed = A.allowed_of(3, {(0, 0), (1, 1), (2, 2)})             # alle Zuordnungen ohne Fixpunkt: 2
    assert A.ryser(3, allowed) == (2, 7) and A.permanent_dp(3, allowed)[0] == 2
    assert A.permanent_dp(3, allowed)[1] == 1 + 2 + 3 + 1             # Zustände: Anfang, nach Zeile 1: Spalte 2 oder 3, nach Zeile 2: alle drei Spaltenpaare, nach Zeile 3: alle Spalten


def test_surjections_and_derangements_by_hand():
    assert A.surjections_sieve(4, 2) == 14 == 2 ** 4 - 2 and A.surjections_brute(4, 2) == 14 and A.surjections_sieve(3, 4) == 0
    assert [A.derangements_sieve(n) for n in range(7)] == [1, 0, 1, 2, 9, 44, 265]


def test_legendre_by_hand():
    assert A.legendre_sieve(30, [2, 3]) == (30 - 15 - 10 + 5, 4) == (10, 4)
    assert A.legendre_brute(30, [2, 3]) == 10 and A.legendre_sieve(10, []) == (10, 1)
    assert A.legendre_sieve(1000, [2, 3, 5, 7]) == (228, 16) and A.legendre_brute(1000, [2, 3, 5, 7]) == 228
    assert A.legendre_sieve(12, [4, 6])[0] == 12 - 3 - 2 + 1 == 8       # kgV(4, 6) = 12


def test_hamilton_cycles_by_hand(hand_digraph_4):
    n, adj = hand_digraph_4["n"], hand_digraph_4["adj"]
    assert A.ham_sieve(n, adj)[0] == A.ham_dp(n, adj)[0] == A.ham_brute(n, adj) == hand_digraph_4["cycles"] == 1
    kn = [[i != j for j in range(5)] for i in range(5)]
    assert A.ham_sieve(5, kn)[0] == A.ham_dp(5, kn)[0] == A.ham_brute(5, kn) == 24


def test_hamilton_counts_and_states_by_hand():
    kn = [[i != j for j in range(4)] for i in range(4)]
    count, states, transitions = A.ham_dp(4, kn)
    assert count == 6 and states == 1 + 3 * 2 ** 2 == 13 and transitions == 3 + 6 + 6      # 0→j (3), danach je 2 Wege weiter (6), danach je 1 Weg (6)
    assert A.ham_sieve_subsets(4) == 8 and A.ham_sieve_subsets(1) == 1


def test_tsp_polynomial_by_hand(hand_triangle_costs):
    n, cost, cmax = hand_triangle_costs["n"], hand_triangle_costs["cost"], hand_triangle_costs["cmax"]
    poly, ops = A.tsp_sieve(n, cost, cmax)
    assert poly == [0] * 6 + [1, 0, 0, 0] and len(poly) == n * cmax + 1 and A.best_of_poly(poly) == (6, 1)
    assert A.tsp_sieve_lists(n, cost, cmax) == poly and A.tsp_dp(n, cost)[0] == (6, 1) and A.tsp_brute(n, cost) == (6, 1)


def test_tsp_polynomial_of_the_complete_graph_with_equal_costs():
    n = 4
    cost = [[None if i == j else 2 for j in range(n)] for i in range(n)]
    poly, _ = A.tsp_sieve(n, cost, 2)
    assert poly[8] == 6 and sum(poly) == 6 and A.best_of_poly(poly) == (8, 6)       # alle 3! Kreise kosten 4·2


def test_best_of_poly():
    assert A.best_of_poly([0, 0, 0]) is None and A.best_of_poly([0, 3, 5]) == (1, 3)


def test_digit_count_and_log10():
    assert A.digit_count(0) == 1 and A.digit_count(999) == 3 and A.digit_count(1000) == 4 and A.digit_count(10 ** 5000) == 5001
    with pytest.raises(ValueError):
        A.digit_count(-1)
    assert A.log10_int(1) == 0 and abs(A.log10_int(10 ** 500) - 500) < 1e-9
    with pytest.raises(ValueError):
        A.log10_int(0)


def test_invalid_input_is_refused():
    with pytest.raises(ValueError):
        A.rook_numbers(3, {(3, 0)})
    with pytest.raises(ValueError):
        A.allowed_of(2, {(0, 2)})
    with pytest.raises(ValueError):
        A.legendre_sieve(10, [0])
    with pytest.raises(ValueError):
        A.tsp_sieve(1, [[None]], 3)
