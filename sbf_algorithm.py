"""Rechenkern: die Siebformel (Inklusion–Exklusion) mit ganzen Zahlen. Zuordnungen mit verbotenen Feldern (Sieb über Feldmengen, Turmzahlen, Ryser, Teilmengen-DP, Aufzählen),
Hamiltonkreise über Spaziergänge, TSP mit Polynomgewichten, Held–Karp als Gegenprobe, Zahlen ohne gegebene Teiler, Surjektionen.

Ein Brett ist eine Menge verbotener Felder (Zeile, Spalte) mit 0 <= Zeile, Spalte < n. Ein Digraph ist eine Kostenmatrix `cost[i][j]` (None = keine Kante) oder eine Wahrheitsmatrix `adj`.
Alles mit `int`; keine Gleitkommazahlen im Zählen (außer in `surjections_sieve_float`, das genau ihr Versagen zeigt)."""

import itertools
import math
from functools import lru_cache

C = math.comb


# ----------------------------------------------------------------------------- Zahlen

def digit_count(x: int) -> int:
    """Zahl der Dezimalstellen einer ganzen Zahl x >= 0, ohne sie in einen String zu wandeln (Python begrenzt die Umwandlung auf 4300 Stellen)."""
    if x < 0:
        raise ValueError("x darf nicht negativ sein")
    d = max(1, int(x.bit_length() * 0.30102999566398))
    while 10 ** d <= x:
        d += 1
    while d > 1 and 10 ** (d - 1) > x:
        d -= 1
    return d


def log10_int(x: int) -> float:
    """Zehnerlogarithmus einer ganzen Zahl x >= 1, auf etwa 15 Stellen genau."""
    if x < 1:
        raise ValueError("x muss mindestens 1 sein")
    d = digit_count(x)
    if d <= 15:
        return math.log10(x)
    shift = d - 15
    return shift + math.log10(x // 10 ** shift)


# ----------------------------------------------------------------------------- Zuordnungen mit verbotenen Feldern

def _check_board(n, forbidden):
    for i, j in forbidden:
        if not (0 <= i < n and 0 <= j < n):
            raise ValueError(f"Feld {(i, j)} liegt nicht im {n}×{n}-Brett")


def diagonal_board(n):
    return {(i, i) for i in range(n)}


def menage_board(n):
    """Diagonale plus Nebendiagonale (zyklisch): σ(i) ≠ i und σ(i) ≠ i+1 mod n."""
    return {(i, i) for i in range(n)} | {(i, (i + 1) % n) for i in range(n)}


def full_board(n):
    return {(i, j) for i in range(n) for j in range(n)}


def allowed_of(n, forbidden):
    _check_board(n, forbidden)
    return [[0 if (i, j) in forbidden else 1 for j in range(n)] for i in range(n)]


def is_non_attacking(cells) -> bool:
    rows, cols = set(), set()
    for i, j in cells:
        if i in rows or j in cols:
            return False
        rows.add(i)
        cols.add(j)
    return True


def assignments_brute(n, forbidden) -> int:
    """Zuordnungen (Permutationen) ohne verbotenes Feld durch Aufzählen aller Permutationen."""
    _check_board(n, forbidden)
    return sum(1 for p in itertools.permutations(range(n)) if all((i, p[i]) not in forbidden for i in range(n)))


def sieve_over_cells(n, forbidden):
    """Siebformel über alle Teilmengen verbotener Felder: Summe (−1)^|S|·(n − |S|)! über nichtangreifende S (angreifende tragen 0 bei). Gibt (Ergebnis, Zahl der Teilmengen, Zahl der nichtangreifenden)."""
    _check_board(n, forbidden)
    cells = sorted(forbidden)
    total, subsets, good = 0, 0, 0
    for k in range(len(cells) + 1):
        for s in itertools.combinations(cells, k):
            subsets += 1
            if is_non_attacking(s):
                good += 1
                total += (-1) ** k * math.factorial(n - k)
    return total, subsets, good


def rook_numbers(n, forbidden) -> list[int]:
    """r_k = Zahl der Möglichkeiten, k nicht schlagende Türme auf die verbotenen Felder zu stellen (Zeile für Zeile, Spaltenmaske); Liste r_0..r_n."""
    _check_board(n, forbidden)
    rows = [[j for j in range(n) if (i, j) in forbidden] for i in range(n)]

    @lru_cache(maxsize=None)
    def f(i, mask):
        if i == n:
            return (1,)
        out = list(f(i + 1, mask))
        for j in rows[i]:
            if not mask >> j & 1:
                sub = f(i + 1, mask | 1 << j)
                if len(out) < len(sub) + 1:
                    out += [0] * (len(sub) + 1 - len(out))
                for k, v in enumerate(sub):
                    out[k + 1] += v
        return tuple(out)

    r = list(f(0, 0))
    return r + [0] * (n + 1 - len(r))


def sieve_rook(n, forbidden):
    """Siebformel mit Turmzahlen: Summe_k (−1)^k·r_k·(n − k)!. Gibt (Ergebnis, Turmzahlen)."""
    r = rook_numbers(n, forbidden)
    return sum((-1) ** k * r[k] * math.factorial(n - k) for k in range(n + 1)), r


def ryser(n, allowed):
    """Permanente der 0/1-Matrix `allowed` über das Sieb über Spaltenmengen: Summe_S (−1)^(n−|S|)·Produkt_i Summe_(j in S) a_ij. Gibt (Wert, Zahl der Teilmengen)."""
    if n == 0:
        return 1, 1                                  # die leere Matrix hat die Permanente 1 (die leere Menge ist der einzige Summand)
    total = 0
    for s in range(1, 1 << n):                       # die leere Spaltenmenge trägt für n >= 1 den Wert 0 bei (leere Zeilensumme)
        cols = [j for j in range(n) if s >> j & 1]
        prod = 1
        for i in range(n):
            prod *= sum(allowed[i][j] for j in cols)
            if prod == 0:
                break
        total += (-1) ** (n - len(cols)) * prod
    return total, (1 << n) - 1


def permanent_dp(n, allowed):
    """Teilmengen-DP: Zahl der Zuordnungen der ersten i Zeilen je Maske belegter Spalten. Gibt (Wert, Zahl der Zustände)."""
    dp = {0: 1}
    states = 1
    for i in range(n):
        new = {}
        for mask, c in dp.items():
            for j in range(n):
                if allowed[i][j] and not mask >> j & 1:
                    new[mask | 1 << j] = new.get(mask | 1 << j, 0) + c
        dp = new
        states += len(dp)
    return dp.get((1 << n) - 1, 0), states


def rook_numbers_cycle_formula(n: int, k: int) -> int:
    """Turmzahlen des Kreisbretts (Ménage-Brett): r_k = 2n/(2n−k)·C(2n−k, k), n >= 3."""
    return 2 * n * C(2 * n - k, k) // (2 * n - k)


def menage_numbers(n_max: int) -> list[int]:
    """Ménage-Zahlen für n = 3..n_max über die Formel der Turmzahlen (ohne das Brett aufzubauen); für n < 3 die Werte 1, 0, 0."""
    out = [1, 0, 0]
    for n in range(3, n_max + 1):
        out.append(sum((-1) ** k * rook_numbers_cycle_formula(n, k) * math.factorial(n - k) for k in range(n + 1)))
    return out[: n_max + 1]


def derangements_sieve(n: int) -> int:
    return sum((-1) ** j * C(n, j) * math.factorial(n - j) for j in range(n + 1))


def surjections_sieve(n: int, k: int) -> int:
    """Zuordnungen von n Aufgaben auf k Maschinen, jede Maschine mindestens eine: Summe_j (−1)^(k−j) C(k, j) jⁿ (k + 1 Summanden)."""
    return sum((-1) ** (k - j) * C(k, j) * j ** n for j in range(k + 1))


def surjections_sieve_float(n: int, k: int) -> float:
    """Dasselbe Sieb in Gleitkommazahlen: zeigt, wie die Auslöschung das Ergebnis zerstört."""
    return sum((-1) ** (k - j) * float(C(k, j)) * float(j) ** n for j in range(k + 1))


def surjections_brute(n: int, k: int) -> int:
    return sum(1 for f in itertools.product(range(k), repeat=n) if len(set(f)) == k)


def legendre_sieve(limit: int, divisors) -> tuple:
    """Zahlen von 1 bis limit, die durch keinen der Teiler teilbar sind: Summe über Teilmengen S der Teiler von (−1)^|S|·⌊limit / kgV(S)⌋. Gibt (Ergebnis, Zahl der Summanden)."""
    if any(d < 1 for d in divisors):
        raise ValueError("Teiler müssen mindestens 1 sein")
    total = 0
    terms = 0
    for k in range(len(divisors) + 1):
        for s in itertools.combinations(divisors, k):
            terms += 1
            total += (-1) ** k * (limit // (math.lcm(*s) if s else 1))
    return total, terms


def legendre_brute(limit: int, divisors) -> int:
    return sum(1 for x in range(1, limit + 1) if all(x % d for d in divisors))


# ----------------------------------------------------------------------------- Hamiltonkreise

def ham_brute(n, adj) -> int:
    """Hamiltonkreise (gerichtet, ab Stadt 0, jeder Kreis einmal) durch Aufzählen aller Reihenfolgen; für n = 1 ist es eine Schleife in Stadt 0."""
    if n == 1:
        return 1 if adj[0][0] else 0
    return sum(1 for perm in itertools.permutations(range(1, n)) if all(adj[a][b] for a, b in zip((0,) + perm, perm + (0,))))


def ham_dp(n, adj):
    """Held–Karp als Zähler: Zahl der Pfade von 0 über eine Menge nach j. Gibt (Hamiltonkreise, Zahl der Zustände, Zahl der Übergänge)."""
    full = (1 << n) - 1
    dp = {(1, 0): 1}
    transitions = 0
    for mask in range(1, full + 1, 2):
        for j in range(n):
            c = dp.get((mask, j), 0)
            if not c:
                continue
            for k in range(n):
                if adj[j][k] and not mask >> k & 1:
                    key = (mask | 1 << k, k)
                    dp[key] = dp.get(key, 0) + c
                    transitions += 1
    total = sum(dp.get((full, j), 0) for j in range(1, n) if adj[j][0]) if n > 1 else (1 if adj[0][0] else 0)
    return total, len(dp), transitions


def ham_sieve(n, adj):
    """Hamiltonkreise über die Siebformel über Spaziergänge: Summe über S ⊆ V∖{0} von (−1)^(n−1−|S|)·(Zahl der geschlossenen Spaziergänge der Länge n von 0 in S ∪ {0}).
    Speicher: ein Vektor mit n Zahlen. Gibt (Hamiltonkreise, Zahl der Rechenschritte)."""
    if n == 1:
        return (1 if adj[0][0] else 0), 0
    total = 0
    ops = 0
    for s in range(1 << (n - 1)):
        verts = [0] + [v + 1 for v in range(n - 1) if s >> v & 1]
        v = {0: 1}
        for _ in range(n):
            nv = {}
            for i, c in v.items():
                for j in verts:
                    if adj[i][j]:
                        nv[j] = nv.get(j, 0) + c
                        ops += 1
            v = nv
        total += (-1) ** (n - len(verts)) * v.get(0, 0)
    return total, ops


def ham_sieve_subsets(n: int) -> int:
    return 1 << (n - 1) if n > 1 else 1


# ----------------------------------------------------------------------------- TSP

def tsp_sieve(n, cost, cmax):
    """Kosten-Polynom aller Hamiltonkreise: das Sieb über Spaziergänge mit Gewicht z^Kosten je Kante, die Polynome als eine große ganze Zahl gepackt (B Bit je Koeffizient, ein Schritt zu Kosten c ist ein
    Verschieben um B·c Bit). Koeffizient w = Zahl der Hamiltonkreise mit Kosten w. Gibt (Koeffizienten bis n·cmax, Zahl der Rechenschritte)."""
    if n < 2:
        raise ValueError("verlangt n >= 2")
    bits = n * n.bit_length() + n + 2                      # Spaziergänge der Länge n: höchstens n^n je Teilmenge, höchstens 2^(n−1) Teilmengen
    pos = neg = 0
    ops = 0
    for s in range(1 << (n - 1)):
        verts = [0] + [v + 1 for v in range(n - 1) if s >> v & 1]
        v = {0: 1}
        for _ in range(n):
            nv = {}
            for i, x in v.items():
                for j in verts:
                    c = cost[i][j]
                    if c is not None:
                        nv[j] = nv.get(j, 0) + (x << (bits * c))
                        ops += 1
            v = nv
        w = v.get(0, 0)
        if (n - len(verts)) % 2:
            neg += w
        else:
            pos += w
    mask = (1 << bits) - 1
    poly = [((pos >> (bits * e)) & mask) - ((neg >> (bits * e)) & mask) for e in range(n * cmax + 1)]
    return poly, ops


def tsp_sieve_lists(n, cost, cmax):
    """Dasselbe mit Koeffizientenlisten statt gepackter Zahl (langsamer, Gegenprobe für die gepackte Fassung)."""
    deg = n * cmax
    total = [0] * (deg + 1)
    for s in range(1 << (n - 1)):
        verts = [0] + [v + 1 for v in range(n - 1) if s >> v & 1]
        v = {0: [1] + [0] * deg}
        for _ in range(n):
            nv = {}
            for i, poly in v.items():
                for j in verts:
                    c = cost[i][j]
                    if c is None:
                        continue
                    t = nv.setdefault(j, [0] * (deg + 1))
                    for e in range(deg + 1 - c):
                        if poly[e]:
                            t[e + c] += poly[e]
            v = nv
        w = v.get(0)
        if w is not None:
            sign = (-1) ** (n - len(verts))
            for e in range(deg + 1):
                total[e] += sign * w[e]
    return total


def best_of_poly(poly):
    """(kleinste Kosten, Zahl der Kreise mit diesen Kosten) aus dem Kosten-Polynom, None ohne Kreis."""
    for w, c in enumerate(poly):
        if c:
            return w, c
    return None


def tsp_dp(n, cost):
    """Held–Karp mit Paar (kleinste Kosten, Zahl der besten) wie in Stück 4. Gibt ((Kosten, Zahl) oder None, Zahl der Zustände)."""
    full = (1 << n) - 1
    dp = {(1, 0): (0, 1)}
    for mask in range(1, full + 1, 2):
        for j in range(n):
            cur = dp.get((mask, j))
            if cur is None:
                continue
            for k in range(n):
                c = cost[j][k]
                if c is not None and not mask >> k & 1:
                    cand = (cur[0] + c, cur[1])
                    key = (mask | 1 << k, k)
                    old = dp.get(key)
                    if old is None or cand[0] < old[0]:
                        dp[key] = cand
                    elif cand[0] == old[0]:
                        dp[key] = (old[0], old[1] + cand[1])
    best = None
    for j in range(1, n):
        cur = dp.get((full, j))
        c = cost[j][0]
        if cur is not None and c is not None:
            cand = (cur[0] + c, cur[1])
            if best is None or cand[0] < best[0]:
                best = cand
            elif cand[0] == best[0]:
                best = (best[0], best[1] + cand[1])
    return best, len(dp)


def tsp_brute(n, cost):
    best = None
    for perm in itertools.permutations(range(1, n)):
        path = (0,) + perm
        total = 0
        ok = True
        for a, b in zip(path, path[1:] + (0,)):
            c = cost[a][b]
            if c is None:
                ok = False
                break
            total += c
        if ok:
            if best is None or total < best[0]:
                best = (total, 1)
            elif total == best[0]:
                best = (best[0], best[1] + 1)
    return best


def adjacency_of(cost):
    return [[c is not None for c in row] for row in cost]
