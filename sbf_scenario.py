"""Szenario: Bretter und Kostenmatrizen aus den Einstellungen bauen (deterministisch aus Seed und Anteil), Eingaben begrenzen."""

import random

import sbf_algorithm as A
import sbf_constants as C


def effective_n(task: str, n: int) -> int:
    """Die Größe, mit der die App wirklich rechnet (Rundreise höchstens TOUR_N_MAX Städte)."""
    if task not in C.TASKS:
        raise ValueError(f"unbekannte Aufgabe {task!r}")
    n = max(C.N_MIN, min(n, C.N_MAX))
    return min(n, C.TOUR_N_MAX) if task == "Rundreise" else n


def random_board(n: int, share: int, seed: int) -> set:
    """Jedes Feld ist mit Wahrscheinlichkeit share/100 verboten."""
    rng = random.Random(seed)
    return {(i, j) for i in range(n) for j in range(n) if rng.random() < share / 100}


def make_board(kind: str, n: int, share: int, seed: int) -> set:
    if kind == "Zufallsbrett":
        return random_board(n, share, seed)
    if kind == "Hauptdiagonale":
        return A.diagonal_board(n)
    if kind == "Ménage-Brett":
        return A.menage_board(n)
    if kind == "Leeres Brett":
        return set()
    if kind == "Volles Brett":
        return A.full_board(n)
    raise ValueError(f"unbekanntes Brett {kind!r}")


def make_cost(n: int, share: int, r: int, seed: int) -> list:
    """Kostenmatrix einer gerichteten Rundreise: Kante i→j (i ≠ j) ist mit Wahrscheinlichkeit share/100 vorhanden und kostet 1 bis r; None = keine Kante."""
    rng = random.Random(seed)
    cost = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                present = rng.random() < share / 100
                c = rng.randint(1, r)
                cost[i][j] = c if present else None
    return cost


def complete_cost(n: int, c: int = 1) -> list:
    return [[None if i == j else c for j in range(n)] for i in range(n)]
