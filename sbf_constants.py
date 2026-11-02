"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

TASKS = ("Zuordnung", "Rundreise")
DEFAULT_TASK = "Zuordnung"
BOARDS = ("Zufallsbrett", "Hauptdiagonale", "Ménage-Brett", "Leeres Brett", "Volles Brett")
DEFAULT_BOARD = "Zufallsbrett"
N_MIN, N_MAX, DEFAULT_N = 3, 12, 8              # Zeilen und Spalten des Bretts beziehungsweise Städte (Rundreise höchstens TOUR_N_MAX)
TOUR_N_MAX = 10                                  # das Sieb über Spaziergänge hat 2^(n−1) Teilmengen
SHARE_MIN, SHARE_MAX, DEFAULT_SHARE = 0, 100, 20  # Zufallsbrett: Anteil verbotener Felder in %; Rundreise: Anteil vorhandener Kanten in %
R_MIN, R_MAX, DEFAULT_R = 1, 5, 3               # Rundreise: Kosten liegen zwischen 1 und r (das Kostenpolynom hat Grad n·r)
SEED_MAX, DEFAULT_SEED = 999999, 35

FIELD_SIEVE_MAX = 16                             # Sieb über Feldmengen nur bis hier (2^16 Teilmengen)
ENUM_ASSIGN_N = 8                                # Aufzählen aller Zuordnungen bis hier
ENUM_TOUR_N = 8                                  # ... aller Rundreisen bis hier

MENAGE_NS = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12)    # Experiment 2: Ménage-Zahlen
MENAGE_BRUTE_N = 8                               # ... gegen Aufzählen bis hier
TERMS_SEED = 100                                 # ... feste Zufallsbretter
TERMS_BOARDS = (("Hauptdiagonale", 10, 0), ("Ménage-Brett", 10, 0), ("Zufallsbrett 20 %", 8, 20), ("Zufallsbrett 40 %", 8, 40), ("Zufallsbrett 15 %", 12, 15))
HK_NS = (6, 7, 8, 9, 10)                         # Experiment 3: vollständiger Digraph
TIME_NS = (8, 10, 12)                            # ... gemessene Zeit (nur auf Klick, nicht getestet)
TSP_N, TSP_SHARE, TSP_R = 8, 100, 5              # Experiment 4: feste Instanz (nur der Seed kommt aus dem Regler)
FLOAT_KS = (10, 15, 20, 25, 30, 40)              # Experiment 5: Surjektionen n = k
PLAY_LIMIT_MIN, PLAY_LIMIT_MAX, PLAY_LIMIT_DEFAULT = 10, 1000, 1000   # Spielwiese: Zahlen bis N
PLAY_DIVISORS = (2, 3, 5, 7, 11, 13)             # ... Auswahl der Teiler
PLAY_DIVISORS_DEFAULT = (2, 3, 5, 7)
PLAY_MAX = 12                                    # ... Aufgaben n und Maschinen k bis hier
PLAY_BRUTE_LIMIT = 100_000                       # ... Aufzählen der Zuordnungen, wenn k^n darunter liegt

COLOR_MAIN = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_WARN = "#c0504d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Standardfall: Zufallsbrett 8 × 8": {"task": "Zuordnung", "board": "Zufallsbrett", "n": 8, "share": 20, "r": 3, "seed": 35},
    "Derangements: Hauptdiagonale 10 × 10": {"task": "Zuordnung", "board": "Hauptdiagonale", "n": 10, "share": 20, "r": 3, "seed": 35},
    "Ménage-Zahlen: 9 Paare": {"task": "Zuordnung", "board": "Ménage-Brett", "n": 9, "share": 20, "r": 3, "seed": 35},
    "Leeres Brett: alle 7! Zuordnungen": {"task": "Zuordnung", "board": "Leeres Brett", "n": 7, "share": 20, "r": 3, "seed": 35},
    "Volles Brett: keine Zuordnung": {"task": "Zuordnung", "board": "Volles Brett", "n": 6, "share": 20, "r": 3, "seed": 35},
    "Rundreise: alle Kanten, 8 Städte": {"task": "Rundreise", "board": "Zufallsbrett", "n": 8, "share": 100, "r": 3, "seed": 35},
    "Rundreise: Kanten fehlen, Kosten bis 5": {"task": "Rundreise", "board": "Zufallsbrett", "n": 8, "share": 60, "r": 5, "seed": 35},
}
PRESET_HELP = {
    "Standardfall: Zufallsbrett 8 × 8": "Acht Aufgaben auf acht Maschinen, jedes fünfte Paar verboten (zufällig): das Sieb über Feldmengen hätte Millionen Summanden, die Turmzahlen nur wenige.",
    "Derangements: Hauptdiagonale 10 × 10": "Jede Aufgabe darf nicht auf die Maschine mit gleicher Nummer: 1.334.961 Zuordnungen, das Sieb hat 11 Summanden statt 1.024 Teilmengen.",
    "Ménage-Zahlen: 9 Paare": "Zuordnung i darf weder auf Platz i noch auf Platz i+1 (zyklisch): die Ménage-Zahl 43.387 für neun Paare.",
    "Leeres Brett: alle 7! Zuordnungen": "Kein Feld verboten: 5.040 Zuordnungen, das Sieb hat nur den Summanden 7!.",
    "Volles Brett: keine Zuordnung": "Alle Felder verboten: 0 Zuordnungen, das Sieb löscht sich vollständig aus.",
    "Rundreise: alle Kanten, 8 Städte": "Jede Verbindung vorhanden: 5.040 Hamiltonkreise ((n−1)!), das Sieb braucht 128 Teilmengen und nur 8 gespeicherte Zahlen, Held–Karp 449 Zustände.",
    "Rundreise: Kanten fehlen, Kosten bis 5": "40 % der Verbindungen fehlen, Kosten 1 bis 5: wie viele Hamiltonkreise bleiben, und was kostet der billigste?",
}
