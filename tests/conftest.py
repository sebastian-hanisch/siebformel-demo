"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand_derangements_4():
    """Hauptdiagonale n = 4: Turmzahlen C(4,k) = 1, 4, 6, 4, 1; Zuordnungen 4! − 4·3! + 6·2! − 4·1! + 1·0! = 24 − 24 + 12 − 4 + 1 = 9."""
    return {"n": 4, "rook": [1, 4, 6, 4, 1], "value": 9}


@pytest.fixture
def hand_menage_3():
    """Ménage n = 3: Brett (i,i) und (i,i+1 mod 3), 6 Felder. r0 = 1, r1 = 6, r2 = C(6,2) − 3 (gleiche Zeile) − 3 (gleiche Spalte) = 9, r3 = 2 (die zwei Permutationen, die nur verbotene Felder benutzen);
    Zuordnungen 3! − 6·2! + 9·1! − 2·0! = 6 − 12 + 9 − 2 = 1."""
    return {"n": 3, "rook": [1, 6, 9, 2], "value": 1}


@pytest.fixture
def hand_digraph_4():
    """Digraph mit den Kanten 0→1, 0→2, 1→2, 2→3, 3→0: einziger Hamiltonkreis ist 0→1→2→3→0 (von 0 muss es über 1 oder 2 weitergehen; 0→2 lässt die 1 nicht mehr erreichen, weil nur 0→1 in 1 hineinführt)."""
    n = 4
    arcs = {(0, 1), (0, 2), (1, 2), (2, 3), (3, 0)}
    return {"n": n, "adj": [[(i, j) in arcs for j in range(n)] for i in range(n)], "cycles": 1}


@pytest.fixture
def hand_triangle_costs():
    """Kreis 0→1→2→0 mit Kosten 1, 2, 3 (nur diese drei Kanten): ein Hamiltonkreis mit Kosten 6; Kostenpolynom z^6."""
    n = 3
    cost = [[None] * n for _ in range(n)]
    cost[0][1], cost[1][2], cost[2][0] = 1, 2, 3
    return {"n": n, "cost": cost, "cmax": 3}
