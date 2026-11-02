"""Orakel-Tests: das Sieb gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §5).

Unabhängig heißt: Aufzählen aller Permutationen und Rundreisen, die Teilmengen-DP (Permanente, Held–Karp mit Paar-Semiring), die Formeln für Derangements, Surjektionen und Turmzahlen des Kreisbretts,
das Aufzählen der Zahlen mit Teilern und die Koeffizientenlisten für die gepackten Polynome. Feste Zufallsstände."""

import itertools
import math
import random

import pytest

import sbf_algorithm as A


def _board(seed, n_lo=3, n_hi=7):
    rng = random.Random(seed)
    n = rng.randint(n_lo, n_hi)
    f = {(i, j) for i in range(n) for j in range(n) if rng.random() < rng.choice([0.15, 0.3, 0.5])}
    return n, set(sorted(f)[:16])


@pytest.mark.parametrize("seed", range(100))
def test_all_assignment_methods_equal_the_enumeration(seed):
    n, f = _board(seed)
    ref = A.assignments_brute(n, f)
    allowed = A.allowed_of(n, f)
    assert A.sieve_over_cells(n, f)[0] == A.sieve_rook(n, f)[0] == A.ryser(n, allowed)[0] == A.permanent_dp(n, allowed)[0] == ref


@pytest.mark.parametrize("seed", range(40))
def test_rook_numbers_equal_counting_non_attacking_subsets(seed):
    n, f = _board(seed, 3, 6)
    cells = sorted(f)
    r = [sum(1 for s in itertools.combinations(cells, k) if A.is_non_attacking(s)) for k in range(n + 1)]
    assert A.rook_numbers(n, f) == r


def test_menage_numbers_equal_the_enumeration_and_the_formula():
    assert [A.assignments_brute(n, A.menage_board(n)) for n in range(3, 9)] == [1, 2, 13, 80, 579, 4738]
    assert A.menage_numbers(12) == [1, 0, 0, 1, 2, 13, 80, 579, 4738, 43387, 439792, 4890741, 59216642]
    assert all(A.sieve_rook(n, A.menage_board(n))[0] == A.menage_numbers(n)[n] for n in range(3, 13))
    assert all(A.rook_numbers(n, A.menage_board(n))[k] == A.rook_numbers_cycle_formula(n, k) for n in range(3, 11) for k in range(n + 1))


def test_diagonal_board_has_binomial_rook_numbers_and_derangements():
    for n in range(1, 13):
        assert A.rook_numbers(n, A.diagonal_board(n)) == [math.comb(n, k) for k in range(n + 1)]
        assert A.sieve_rook(n, A.diagonal_board(n))[0] == A.derangements_sieve(n)
    d = [1, 0]
    for n in range(2, 31):
        d.append((n - 1) * (d[-1] + d[-2]))
    assert [A.derangements_sieve(n) for n in range(31)] == d


def test_empty_and_full_boards():
    for n in range(1, 9):
        assert A.sieve_rook(n, set())[0] == math.factorial(n) and A.sieve_rook(n, A.full_board(n))[0] == 0
        assert A.rook_numbers(n, A.full_board(n))[n] == math.factorial(n)


@pytest.mark.parametrize("seed", range(100))
def test_hamilton_cycles_sieve_equals_held_karp_and_enumeration(seed):
    rng = random.Random(seed)
    n = rng.randint(3, 8)
    p = rng.choice([0.5, 0.7, 0.9])
    adj = [[i != j and rng.random() < p for j in range(n)] for i in range(n)]
    assert A.ham_sieve(n, adj)[0] == A.ham_dp(n, adj)[0] == A.ham_brute(n, adj)


@pytest.mark.parametrize("n", range(3, 9))
def test_complete_digraph_has_n_minus_1_factorial_cycles(n):
    kn = [[i != j for j in range(n)] for i in range(n)]
    assert A.ham_sieve(n, kn)[0] == A.ham_dp(n, kn)[0] == math.factorial(n - 1)
    assert A.ham_dp(n, kn)[1] == 1 + (n - 1) * 2 ** (n - 2)


@pytest.mark.parametrize("seed", range(60))
def test_tsp_sieve_equals_held_karp_and_enumeration(seed):
    rng = random.Random(1000 + seed)
    n = rng.randint(3, 8)
    cmax = rng.choice([2, 3, 5])
    p = rng.choice([0.6, 0.8, 1.0])
    cost = [[(rng.randint(1, cmax) if i != j and rng.random() < p else None) for j in range(n)] for i in range(n)]
    poly, _ = A.tsp_sieve(n, cost, cmax)
    assert all(c >= 0 for c in poly)
    assert A.best_of_poly(poly) == A.tsp_dp(n, cost)[0] == A.tsp_brute(n, cost)
    assert sum(poly) == A.ham_brute(n, A.adjacency_of(cost))


@pytest.mark.parametrize("seed", range(20))
def test_packed_polynomial_equals_the_coefficient_lists(seed):
    rng = random.Random(2000 + seed)
    n = rng.randint(3, 7)
    cmax = rng.choice([2, 4])
    cost = [[(rng.randint(1, cmax) if i != j and rng.random() < 0.8 else None) for j in range(n)] for i in range(n)]
    assert A.tsp_sieve(n, cost, cmax)[0] == A.tsp_sieve_lists(n, cost, cmax)


def test_surjections_equal_the_enumeration_and_the_stirling_triangle():
    s2 = [[0] * 22 for _ in range(21)]
    s2[0][0] = 1
    for n in range(1, 21):
        for k in range(1, n + 1):
            s2[n][k] = k * s2[n - 1][k] + s2[n - 1][k - 1]
    assert all(A.surjections_sieve(n, k) == math.factorial(k) * s2[n][k] for n in range(1, 21) for k in range(1, 8))
    assert all(A.surjections_sieve(n, k) == A.surjections_brute(n, k) for n in range(1, 7) for k in range(1, 5))


@pytest.mark.parametrize("seed", range(40))
def test_legendre_sieve_equals_enumeration(seed):
    rng = random.Random(seed)
    divisors = rng.sample([2, 3, 4, 5, 6, 7, 9, 10, 11, 13], rng.randint(1, 5))
    limit = rng.randint(10, 400)
    value, terms = A.legendre_sieve(limit, divisors)
    assert value == A.legendre_brute(limit, divisors) and terms == 2 ** len(divisors)


def test_phi_by_the_sieve():
    """Eulers φ(n) über das Sieb über die Primteiler: n·Produkt(1 − 1/p) als Summe über Teilmengen."""
    for n in range(2, 200):
        primes = [p for p in range(2, n + 1) if n % p == 0 and all(p % q for q in range(2, p))]
        value, _ = A.legendre_sieve(n, primes)
        assert value == sum(1 for x in range(1, n + 1) if math.gcd(x, n) == 1)


def test_ryser_equals_the_permanent_by_laplace_expansion():
    def perm(m):
        n = len(m)
        if n == 0:
            return 1
        return sum(m[0][j] * perm([row[:j] + row[j + 1:] for row in m[1:]]) for j in range(n))

    rng = random.Random(7)
    for _ in range(40):
        n = rng.randint(1, 7)
        m = [[rng.randint(0, 1) for _ in range(n)] for _ in range(n)]
        assert A.ryser(n, m)[0] == A.permanent_dp(n, m)[0] == perm(m)
