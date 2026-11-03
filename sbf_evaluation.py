"""Kennzahlen, Experimente und Verdikte. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text)."""

import math
import time
from dataclasses import dataclass, field

import sbf_algorithm as A
import sbf_constants as C
from sbf_scenario import complete_cost, effective_n, make_board, make_cost, random_board

_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


@dataclass(frozen=True)
class Settings:
    task: str = C.DEFAULT_TASK
    board: str = C.DEFAULT_BOARD
    n: int = C.DEFAULT_N
    share: int = C.DEFAULT_SHARE
    r: int = C.DEFAULT_R
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True, eq=False)
class Analysis:
    settings: Settings
    n_eff: int
    ways: list                             # Rechenwege: {"Gruppe", "Weg", "Wert", "Text", "Schritte", "Grund"}
    problems: list                         # Meldungen des Vergleichs der Rechenwege
    notes: list                            # Hinweise zu begrenzten Eingaben
    info: dict = field(default_factory=dict)   # Kennzahlen der Aufgabe (Zuordnung oder Rundreise)


# ----------------------------------------------------------------------------- Formatierung

_BREAK = "·10"


def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 12 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit Stellenzahl (ohne Stringumwandlung der ganzen Zahl)."""
    if x < 10 ** 12:
        return f"{x:,}".replace(",", ".")
    d = A.digit_count(x)
    s = str(x // 10 ** (d - 3))
    return f"{s[0]},{s[1:3]}{_BREAK}{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def sci_text(x: float) -> str:
    """Gleitkommazahl als Mantisse mal Zehnerpotenz (z. B. 2,8·10⁴) oder ohne Potenz, wenn sie klein genug ist."""
    if x == 0:
        return "0"
    if 0.01 <= abs(x) < 10000:
        return de(x, 2)
    mant, exp = f"{x:.1e}".split("e")
    return f"{mant.replace('.', ',')}{_BREAK}{str(int(exp)).translate(_SUPER)}"


def share_text(x: float) -> str:
    if x == 0:
        return "0"
    if x >= 0.001:
        return de(x, 4)
    return sci_text(x)


def pair_text(p) -> str:
    return "keine Rundreise" if p is None or p[1] == 0 else f"Kosten {p[0]}, {big_text(p[1])} Mal"


# ----------------------------------------------------------------------------- Analyse der eingestellten Aufgabe

def formula_value(kind: str, n: int):
    """Bekannter Wert aus einer Formel (Name, Wert), wenn es für das Brett eine gibt."""
    if kind == "Hauptdiagonale":
        return "Formel Σ(−1)^j·C(n,j)·(n−j)!", A.derangements_sieve(n)
    if kind == "Ménage-Brett":
        return "Formel der Turmzahlen 2n/(2n−k)·C(2n−k,k)", A.menage_numbers(n)[n]
    if kind == "Leeres Brett":
        return "Fakultät n!", math.factorial(n)
    if kind == "Volles Brett":
        return "kein Feld erlaubt", 0
    return None


def analyse(s: Settings) -> Analysis:
    n = effective_n(s.task, s.n)
    notes = []
    ways, problems = [], []

    def add(group, name, value, text, steps, reason=""):
        ways.append({"Gruppe": group, "Weg": name, "Wert": value, "Text": text, "Schritte": steps, "Grund": reason})

    if s.task == "Zuordnung":
        forbidden = make_board(s.board, n, s.share, s.seed)
        value, rook = A.sieve_rook(n, forbidden)
        nonzero = sum(1 for x in rook if x)
        add("Zuordnungen", "Sieb mit Turmzahlen", value, big_text(value), nonzero)
        cells = len(forbidden)
        if cells <= C.FIELD_SIEVE_MAX:
            v2, subsets, good = A.sieve_over_cells(n, forbidden)
            add("Zuordnungen", "Sieb über Feldmengen", v2, big_text(v2), subsets)
        else:
            add("Zuordnungen", "Sieb über Feldmengen", None, "", None, f"übersprungen: 2^{cells} Teilmengen, nur bis {C.FIELD_SIEVE_MAX} Felder")
        allowed = A.allowed_of(n, forbidden)
        v3, subsets3 = A.ryser(n, allowed)
        add("Zuordnungen", "Ryser-Sieb über Spaltenmengen", v3, big_text(v3), subsets3)
        v4, states = A.permanent_dp(n, allowed)
        add("Zuordnungen", "Teilmengen-DP", v4, big_text(v4), states)
        known = formula_value(s.board, n)
        if known is not None:
            add("Zuordnungen", known[0], known[1], big_text(known[1]), n + 1)
        if n <= C.ENUM_ASSIGN_N:
            v5 = A.assignments_brute(n, forbidden)
            add("Zuordnungen", "Aufzählen aller Permutationen", v5, big_text(v5), math.factorial(n))
        else:
            add("Zuordnungen", "Aufzählen aller Permutationen", None, "", None, f"nur bis n = {C.ENUM_ASSIGN_N}")
        info = {"value": value, "rook": rook, "cells": cells, "subsets": 2 ** cells, "nonattacking": sum(rook), "nonzero": nonzero, "total": math.factorial(n),
                "forbidden": frozenset(forbidden)}
    else:
        cost = make_cost(n, s.share, s.r, s.seed)
        adj = A.adjacency_of(cost)
        cycles, ops = A.ham_sieve(n, adj)
        add("Hamiltonkreise", "Sieb über Spaziergänge", cycles, big_text(cycles), ops)
        c2, states, transitions = A.ham_dp(n, adj)
        add("Hamiltonkreise", "Held–Karp-Zähler", c2, big_text(c2), transitions)
        if n <= C.ENUM_TOUR_N:
            c3 = A.ham_brute(n, adj)
            add("Hamiltonkreise", "Aufzählen aller Reihenfolgen", c3, big_text(c3), math.factorial(n - 1))
        else:
            add("Hamiltonkreise", "Aufzählen aller Reihenfolgen", None, "", None, f"nur bis n = {C.ENUM_TOUR_N}")
        poly, ops_poly = A.tsp_sieve(n, cost, s.r)
        best = A.best_of_poly(poly) or (None, 0)
        add("Kosten", "Sieb mit Polynomgewichten", best, pair_text(best), ops_poly)
        hk, hk_states = A.tsp_dp(n, cost)
        add("Kosten", "Held–Karp (Paar aus Kosten und Zahl)", hk or (None, 0), pair_text(hk), hk_states)
        if n <= C.ENUM_TOUR_N:
            br = A.tsp_brute(n, cost)
            add("Kosten", "Aufzählen aller Reihenfolgen", br or (None, 0), pair_text(br), math.factorial(n - 1))
        else:
            add("Kosten", "Aufzählen aller Reihenfolgen", None, "", None, f"nur bis n = {C.ENUM_TOUR_N}")
        info = {"cycles": cycles, "best": best, "poly": poly, "subsets": A.ham_sieve_subsets(n), "sieve_ops": ops, "hk_states": states, "hk_transitions": transitions,
                "arcs": sum(1 for row in adj for x in row if x), "cost": cost}
    if s.task == "Rundreise" and n != s.n:
        notes.append(f"Die Rundreise hat höchstens {C.TOUR_N_MAX} Städte (das Sieb hat 2^(n−1) Teilmengen): gerechnet wird mit {n}.")
    for group in sorted({w["Gruppe"] for w in ways}):
        done = [w for w in ways if w["Gruppe"] == group and w["Wert"] is not None]
        if any(w["Wert"] != done[0]["Wert"] for w in done):
            problems.append(f"{group}: " + ", ".join(f"{w['Weg']} = {w['Text']}" for w in done) + " weichen ab")
    return Analysis(s, n, ways, problems, notes, info)


def way_rows(a: Analysis) -> list[dict]:
    """Tabelle der Rechenwege: Gruppe, Ergebnis, Schritte, Übereinstimmung."""
    rows = []
    reference = {}
    for w in a.ways:
        if w["Wert"] is not None and w["Gruppe"] not in reference:
            reference[w["Gruppe"]] = w["Wert"]
    for w in a.ways:
        if w["Wert"] is None:
            rows.append({"Frage": w["Gruppe"], "Weg": w["Weg"], "Ergebnis": "–", "Schritte": "–", "Prüfung": w["Grund"]})
        else:
            rows.append({"Frage": w["Gruppe"], "Weg": w["Weg"], "Ergebnis": w["Text"], "Schritte": big_text(w["Schritte"]), "Prüfung": "gleich" if w["Wert"] == reference[w["Gruppe"]] else "weicht ab"})
    return rows


def share_of_all(a: Analysis):
    """Anteil der Zuordnungen an allen n! Permutationen (None bei der Rundreise)."""
    if a.settings.task != "Zuordnung":
        return None
    return a.info["value"] / a.info["total"]


def verdict_answers(a: Analysis):
    if a.problems:
        return "error", "Die Rechenwege widersprechen sich: " + "; ".join(a.problems)
    checked = [w["Weg"] for w in a.ways if w["Wert"] is not None]
    info = a.info
    if a.settings.task == "Zuordnung":
        head = (f"{a.n_eff} Aufgaben auf {a.n_eff} Maschinen, {info['cells']} verbotene Paare: {big_text(info['value'])} Zuordnungen. "
                f"Das Sieb über alle Teilmengen verbotener Paare hätte {big_text(info['subsets'])} {'Summand' if info['subsets'] == 1 else 'Summanden'}, davon sind {big_text(info['nonattacking'])} nichtangreifend; mit den Turmzahlen bleiben {info['nonzero']}.")
    else:
        best = info["best"]
        cost_part = "es gibt keinen Hamiltonkreis, also auch keine Kosten" if best[1] == 0 else f"die kleinsten Kosten sind {best[0]}, {big_text(best[1])} Mal"
        head = (f"{a.n_eff} Städte (gerichtet, ab Stadt 0): {big_text(info['cycles'])} Hamiltonkreise, {cost_part}. "
                f"Das Sieb braucht {big_text(info['subsets'])} Teilmengen und {a.n_eff} gespeicherte Zahlen, Held–Karp {big_text(info['hk_states'])} Zustände.")
    return "success", f"{head} {len(checked)} Rechenweg(e) geben je Frage dieselbe Zahl."


# ----------------------------------------------------------------------------- Experiment 2: Terme schrumpfen

def terms_rows() -> list[dict]:
    rows = []
    for label, n, share in C.TERMS_BOARDS:
        if label == "Hauptdiagonale":
            f = A.diagonal_board(n)
        elif label == "Ménage-Brett":
            f = A.menage_board(n)
        else:
            f = random_board(n, share, C.TERMS_SEED + n + share)
        r = A.rook_numbers(n, f)
        value = sum((-1) ** k * r[k] * math.factorial(n - k) for k in range(n + 1))
        rows.append({"Brett": label, "n": n, "verbotene Felder": len(f), "Teilmengen 2^|F|": 2 ** len(f), "nichtangreifend": sum(r), "Turmzahlen ungleich 0": sum(1 for x in r if x), "Zuordnungen": value})
    return rows


def verdict_terms(rows: list[dict]):
    r = rows[3]
    return "success", (f"{r['Brett']} (n = {r['n']}): {big_text(r['Teilmengen 2^|F|'])} Teilmengen verbotener Felder, davon nur {big_text(r['nichtangreifend'])} nichtangreifend und {r['Turmzahlen ungleich 0']} Turmzahlen ungleich 0: "
                       "nach der Zahl der Türme zusammengefasst bleiben höchstens n + 1 Summanden (die Turmzahlen selbst muss man ausrechnen).")


def menage_rows() -> list[dict]:
    formula = A.menage_numbers(max(C.MENAGE_NS))
    rows = []
    for n in C.MENAGE_NS:
        board = A.menage_board(n)
        sieve, rook = A.sieve_rook(n, board)
        brute = A.assignments_brute(n, board) if n <= C.MENAGE_BRUTE_N else None
        rows.append({"n": n, "Ménage-Zahl (Sieb mit Turmzahlen)": sieve, "Formel der Turmzahlen": formula[n], "Aufzählen": brute, "Turmzahlen ungleich 0": sum(1 for x in rook if x)})
    return rows


def menage_check(rows: list[dict]) -> list[str]:
    problems = []
    for r in rows:
        if r["Ménage-Zahl (Sieb mit Turmzahlen)"] != r["Formel der Turmzahlen"]:
            problems.append(f"n = {r['n']}: Sieb und Formel weichen ab")
        if r["Aufzählen"] is not None and r["Aufzählen"] != r["Ménage-Zahl (Sieb mit Turmzahlen)"]:
            problems.append(f"n = {r['n']}: Aufzählen und Sieb weichen ab")
    return problems


def verdict_menage(rows: list[dict], problems: list[str]):
    if problems:
        return "error", "Die Ménage-Zahlen widersprechen sich: " + "; ".join(problems)
    last = rows[-1]
    return "success", (f"Ménage-Zahlen für n = {rows[0]['n']} bis {last['n']}: {', '.join(big_text(r['Ménage-Zahl (Sieb mit Turmzahlen)']) for r in rows[:5])}, …, {big_text(last['Ménage-Zahl (Sieb mit Turmzahlen)'])}. "
                       f"Sieb mit Turmzahlen, Formel der Turmzahlen und (bis n = {C.MENAGE_BRUTE_N}) Aufzählen geben dieselben Zahlen.")


# ----------------------------------------------------------------------------- Experiment 3: Sieb gegen Held–Karp

def hk_rows() -> list[dict]:
    rows = []
    for n in C.HK_NS:
        adj = A.adjacency_of(complete_cost(n))
        sieve, ops = A.ham_sieve(n, adj)
        dp, states, transitions = A.ham_dp(n, adj)
        rows.append({"n": n, "Hamiltonkreise": sieve, "Held–Karp-Zähler": dp, "Teilmengen im Sieb": A.ham_sieve_subsets(n), "Rechenschritte Sieb": ops, "gespeicherte Zahlen Sieb": n,
                     "Zustände Held–Karp": states, "Übergänge Held–Karp": transitions, "Schritte Sieb : Held–Karp": ops / transitions})
    return rows


def hk_check(rows: list[dict]) -> list[str]:
    return [f"n = {r['n']}: Sieb {r['Hamiltonkreise']}, Held–Karp {r['Held–Karp-Zähler']}, (n−1)! = {math.factorial(r['n'] - 1)}" for r in rows
            if not (r["Hamiltonkreise"] == r["Held–Karp-Zähler"] == math.factorial(r["n"] - 1))]


def verdict_hk(rows: list[dict], problems: list[str]):
    if problems:
        return "error", "Sieb und Held–Karp widersprechen sich: " + "; ".join(problems)
    last = rows[-1]
    return "warning", (f"Für n = {last['n']} (vollständiger Digraph, {big_text(last['Hamiltonkreise'])} Hamiltonkreise) braucht das Sieb {big_text(last['Rechenschritte Sieb'])} Rechenschritte und {last['gespeicherte Zahlen Sieb']} gespeicherte Zahlen, "
                       f"Held–Karp {big_text(last['Übergänge Held–Karp'])} Übergänge und {big_text(last['Zustände Held–Karp'])} Zustände: das Sieb rechnet etwa das {de(last['Schritte Sieb : Held–Karp'], 1)}-fache, spart aber den Speicher. "
                       "Die Aussage „das Sieb ist schneller“ gilt nicht; „das Sieb braucht weniger Speicher“ schon.")


def time_experiment() -> list[dict]:
    rows = []
    for n in C.TIME_NS:
        adj = A.adjacency_of(complete_cost(n))
        t0 = time.perf_counter()
        A.ham_sieve(n, adj)
        t1 = time.perf_counter()
        A.ham_dp(n, adj)
        t2 = time.perf_counter()
        rows.append({"n": n, "Sieb (Sekunden)": t1 - t0, "Held–Karp (Sekunden)": t2 - t1})
    return rows


def verdict_time(rows: list[dict]):
    last = rows[-1]
    return "info", (f"Gemessen auf diesem Rechner (Python): n = {last['n']}: Sieb {de(last['Sieb (Sekunden)'], 3)} s, Held–Karp {de(last['Held–Karp (Sekunden)'], 3)} s "
                    f"(etwa das {de(last['Sieb (Sekunden)'] / max(last['Held–Karp (Sekunden)'], 1e-9), 0)}-fache). Eine Messung, keine Garantie.")


# ----------------------------------------------------------------------------- Experiment 4: TSP mit Polynomgewichten

def tsp_experiment(seed: int) -> dict:
    n = C.TSP_N
    cost = make_cost(n, C.TSP_SHARE, C.TSP_R, seed)
    poly, ops = A.tsp_sieve(n, cost, C.TSP_R)
    best = A.best_of_poly(poly)
    hk, _ = A.tsp_dp(n, cost)
    brute = A.tsp_brute(n, cost)
    problems = []
    if best != hk or hk != brute:
        problems.append(f"Sieb {best}, Held–Karp {hk}, Aufzählen {brute}")
    if any(c < 0 for c in poly):
        problems.append("negative Koeffizienten im Kostenpolynom")
    if sum(poly) != math.factorial(n - 1):
        problems.append("Zahl der Kreise ist nicht (n−1)!")
    return {"n": n, "poly": poly, "best": best, "hk": hk, "brute": brute, "ops": ops, "cycles": sum(poly), "brute_steps": math.factorial(n - 1), "problems": problems}


def verdict_tsp(res: dict):
    if res["problems"]:
        return "error", "Sieb, Held–Karp und Aufzählen widersprechen sich: " + "; ".join(res["problems"])
    best = res["best"]
    spread = max(w for w, c in enumerate(res["poly"]) if c)
    return "success", (f"{res['n']} Städte, alle Kanten, Kosten 1 bis {C.TSP_R}: {big_text(res['cycles'])} Hamiltonkreise mit Kosten von {best[0]} bis {spread}; billigste Kosten {best[0]}, {big_text(best[1])} Mal, "
                       "gleich Held–Karp und Aufzählen. Das Kostenpolynom gibt die ganze Verteilung, nicht nur das Minimum.")


# ----------------------------------------------------------------------------- Experiment 5: Exaktheit

def float_rows() -> list[dict]:
    rows = []
    for k in C.FLOAT_KS:
        exact = A.surjections_sieve(k, k)
        fl = A.surjections_sieve_float(k, k)
        biggest = max(math.comb(k, j) * j ** k for j in range(k + 1))  # Betrag der Summanden des Siebs, mit ganzen Zahlen gerechnet
        rows.append({"k = n": k, "exakt (k!)": exact, "Gleitkomma": fl, "relative Abweichung": abs(fl - float(exact)) / float(exact), "größter Summand": float(biggest)})
    return rows


def float_check(rows: list[dict]) -> list[str]:
    return [f"k = {r['k = n']}: exaktes Sieb ist nicht k!" for r in rows if r["exakt (k!)"] != math.factorial(r["k = n"])]


def verdict_float(rows: list[dict], problems: list[str]):
    if problems:
        return "error", "Das exakte Sieb weicht von k! ab: " + "; ".join(problems)
    last = rows[-1]
    return "warning", (f"Surjektionen von k auf k (Ergebnis k!) über das Sieb: in Gleitkomma ist die relative Abweichung {sci_text(rows[1]['relative Abweichung'])} bei k = {rows[1]['k = n']}, "
                       f"{sci_text(rows[3]['relative Abweichung'])} bei k = {rows[3]['k = n']} und {sci_text(last['relative Abweichung'])} bei k = {last['k = n']} (größter Summand {sci_text(last['größter Summand'])}): "
                       "die Summanden löschen sich fast aus, dabei geht jede Stelle verloren. Mit ganzen Zahlen stimmt es immer.")


# ----------------------------------------------------------------------------- Spielwiese

def legendre_play(limit: int, divisors) -> dict:
    limit = max(C.PLAY_LIMIT_MIN, min(limit, C.PLAY_LIMIT_MAX))
    divisors = tuple(sorted(set(divisors))) or (2,)
    value, terms = A.legendre_sieve(limit, divisors)
    return {"limit": limit, "divisors": divisors, "value": value, "terms": terms, "brute": A.legendre_brute(limit, divisors)}


def verdict_legendre(res: dict):
    if res["value"] != res["brute"]:
        return "error", f"Sieb ({res['value']}) und Aufzählen ({res['brute']}) weichen ab."
    return "success", (f"Von den Zahlen 1 bis {res['limit']} sind {big_text(res['value'])} durch keinen der Teiler {', '.join(str(d) for d in res['divisors'])} teilbar; "
                       f"das Sieb braucht {res['terms']} Summanden (2^{len(res['divisors'])}), Aufzählen {res['limit']} Prüfungen.")


def machines_play(n: int, k: int) -> dict:
    n = max(1, min(n, C.PLAY_MAX))
    k = max(1, min(k, C.PLAY_MAX))
    sieve = A.surjections_sieve(n, k)
    brute = A.surjections_brute(n, k) if k ** n <= C.PLAY_BRUTE_LIMIT else None
    return {"n": n, "k": k, "sieve": sieve, "all": k ** n, "brute": brute, "terms": k + 1}


def verdict_machines(res: dict):
    if res["brute"] is not None and res["brute"] != res["sieve"]:
        return "error", f"Sieb ({res['sieve']}) und Aufzählen ({res['brute']}) weichen ab."
    check = "Aufzählen bestätigt es" if res["brute"] is not None else "Aufzählen entfällt (zu viele Möglichkeiten)"
    return "success", (f"{big_text(res['sieve'])} von {big_text(res['all'])} Zuordnungen von {res['n']} Aufgaben auf {res['k']} Maschinen lassen keine Maschine leer ({de(100 * res['sieve'] / res['all'], 1)} %); "
                       f"das Sieb braucht {res['terms']} Summanden; {check}.")
