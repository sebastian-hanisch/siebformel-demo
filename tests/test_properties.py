"""Eigenschaften (ORACLE-PLAYBOOK §5): Aussagen, die für jede Instanz gelten, auf festen Zufallsständen."""

import math
import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

import sbf_algorithm as A
import sbf_evaluation as ev

ROOT = Path(__file__).resolve().parent.parent


def _board(seed, n_lo=3, n_hi=8, dens=(0.15, 0.3, 0.5)):
    rng = random.Random(seed)
    n = rng.randint(n_lo, n_hi)
    return n, {(i, j) for i in range(n) for j in range(n) if rng.random() < rng.choice(dens)}


def _value(n, f):
    return A.sieve_rook(n, f)[0]


@pytest.mark.parametrize("seed", range(40))
def test_assignments_are_between_zero_and_n_factorial(seed):
    n, f = _board(seed)
    assert 0 <= _value(n, f) <= math.factorial(n)


@pytest.mark.parametrize("seed", range(40))
def test_more_forbidden_fields_never_give_more_assignments(seed):
    n, f = _board(seed)
    extra = random.Random(seed).choice([(i, j) for i in range(n) for j in range(n)])
    assert _value(n, f | {extra}) <= _value(n, f)


@pytest.mark.parametrize("seed", range(40))
def test_permuting_rows_and_columns_or_transposing_does_not_change_the_count(seed):
    n, f = _board(seed)
    rng = random.Random(seed + 1)
    rows, cols = list(range(n)), list(range(n))
    rng.shuffle(rows)
    rng.shuffle(cols)
    moved = {(rows[i], cols[j]) for i, j in f}
    transposed = {(j, i) for i, j in f}
    assert _value(n, moved) == _value(n, transposed) == _value(n, f)
    assert A.rook_numbers(n, moved) == A.rook_numbers(n, f)


@pytest.mark.parametrize("seed", range(30))
def test_rook_numbers_are_non_negative_and_r1_is_the_field_count(seed):
    n, f = _board(seed)
    r = A.rook_numbers(n, f)
    assert all(x >= 0 for x in r) and r[0] == 1 and r[1] == len(f)


@pytest.mark.parametrize("n", range(1, 25))
def test_derangements_plus_permutations_with_fixed_points_equal_n_factorial(n):
    assert sum(math.comb(n, f) * A.derangements_sieve(n - f) for f in range(n + 1)) == math.factorial(n)


@pytest.mark.parametrize("seed", range(40))
def test_hamilton_cycles_of_the_transpose_and_of_a_relabelling_are_the_same(seed):
    rng = random.Random(seed)
    n = rng.randint(3, 8)
    adj = [[i != j and rng.random() < 0.7 for j in range(n)] for i in range(n)]
    transposed = [[adj[j][i] for j in range(n)] for i in range(n)]
    perm = [0] + rng.sample(range(1, n), n - 1)
    relabelled = [[adj[perm.index(i)][perm.index(j)] for j in range(n)] for i in range(n)]
    base = A.ham_sieve(n, adj)[0]
    assert A.ham_sieve(n, transposed)[0] == A.ham_sieve(n, relabelled)[0] == base >= 0


@pytest.mark.parametrize("seed", range(40))
def test_an_extra_arc_never_removes_a_hamilton_cycle(seed):
    rng = random.Random(seed)
    n = rng.randint(3, 8)
    adj = [[i != j and rng.random() < 0.6 for j in range(n)] for i in range(n)]
    i, j = rng.sample(range(n), 2)
    more = [row[:] for row in adj]
    more[i][j] = True
    assert A.ham_sieve(n, more)[0] >= A.ham_sieve(n, adj)[0]


@pytest.mark.parametrize("seed", range(30))
def test_scaling_all_costs_scales_the_exponents(seed):
    rng = random.Random(seed)
    n = rng.randint(3, 7)
    cmax = rng.choice([2, 3])
    c = rng.randint(2, 4)
    cost = [[(rng.randint(1, cmax) if i != j and rng.random() < 0.8 else None) for j in range(n)] for i in range(n)]
    scaled = [[None if x is None else c * x for x in row] for row in cost]
    base, _ = A.tsp_sieve(n, cost, cmax)
    big, _ = A.tsp_sieve(n, scaled, c * cmax)
    assert all(big[c * w] == base[w] for w in range(len(base))) and sum(big) == sum(base)


@pytest.mark.parametrize("seed", range(30))
def test_the_cost_polynomial_sums_to_the_cycle_count(seed):
    rng = random.Random(seed)
    n = rng.randint(3, 8)
    cost = [[(rng.randint(1, 4) if i != j and rng.random() < 0.7 else None) for j in range(n)] for i in range(n)]
    poly, _ = A.tsp_sieve(n, cost, 4)
    assert sum(poly) == A.ham_sieve(n, A.adjacency_of(cost))[0] and all(x >= 0 for x in poly)


@pytest.mark.parametrize("n", range(1, 21))
@pytest.mark.parametrize("k", range(1, 6))
def test_surjections_never_exceed_all_assignments_and_vanish_for_k_above_n(n, k):
    sur = A.surjections_sieve(n, k)
    assert 0 <= sur <= k ** n and (sur == 0) == (k > n)


def test_the_float_sieve_fails_where_the_exact_sieve_does_not():
    exact = A.surjections_sieve(40, 40)
    assert exact == math.factorial(40)
    assert abs(A.surjections_sieve_float(40, 40) - float(exact)) / float(exact) > 1
    assert abs(A.surjections_sieve_float(10, 10) - float(math.factorial(10))) / float(math.factorial(10)) < 1e-9


@pytest.mark.parametrize("seed", range(20))
def test_legendre_is_monotone_in_the_divisor_set(seed):
    rng = random.Random(seed)
    divisors = rng.sample([2, 3, 5, 7, 11, 13], 4)
    limit = rng.randint(50, 1000)
    counts = [A.legendre_sieve(limit, divisors[:k])[0] for k in range(5)]
    assert counts[0] == limit and all(x >= y for x, y in zip(counts, counts[1:]))


def test_analyses_are_deterministic_across_hash_seeds():
    code = ("import sys; sys.path.insert(0, %r); import sbf_evaluation as ev; "
            "a = ev.analyse(ev.Settings('Zuordnung', 'Zufallsbrett', 8, 20, 3, 35)); b = ev.analyse(ev.Settings('Rundreise', 'Zufallsbrett', 7, 70, 4, 35)); "
            "print(a.info['value'], sorted(a.info['forbidden']), b.info['cycles'], b.info['best'], b.info['poly'])" % str(ROOT))
    runs = {subprocess.run([sys.executable, "-X", "utf8", "-c", code], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONHASHSEED": str(h)}).stdout for h in (0, 1, 12345)}
    assert len(runs) == 1 and runs.pop().strip()


def test_every_setting_gives_a_consistent_analysis():
    for task in ("Zuordnung", "Rundreise"):
        for seed in range(5):
            a = ev.analyse(ev.Settings(task, "Zufallsbrett", 6, 40 + 10 * seed, 3, seed))
            assert a.problems == []
