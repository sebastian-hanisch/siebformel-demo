"""AppTest-Durchläufe der Experimente, des Permalinks und der Spielwiese (die allgemeinen Rauchtests stehen in test_app.py)."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import sbf_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(query: dict | None = None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _all_text(at) -> str:
    return " | ".join(e.value for e in list(at.success) + list(at.info) + list(at.warning) + list(at.error))


def _metrics(at) -> dict:
    return {m.label: m.value for m in at.metric}


def test_standard_case_shows_the_known_values_and_no_error():
    at = _app()
    assert not at.error
    assert _metrics(at) == {"Zuordnungen ohne verbotenes Feld": "3.000", "Anteil an allen Zuordnungen": "0,0744", "Teilmengen verbotener Felder": "16.384", "Summanden mit Turmzahlen": "5"}
    assert any(e.value.startswith("8 Aufgaben auf 8 Maschinen, 14 verbotene Paare: 3.000 Zuordnungen.") for e in at.success)
    assert any(e.value == "Alle gerechneten Wege geben je Frage dieselbe Zahl." for e in at.success)


def test_experiments_two_to_five_show_their_verdicts_without_a_click():
    text = _all_text(_app())
    assert "Zufallsbrett 40 % (n = 8): 524.288 Teilmengen verbotener Felder, davon nur 2.737 nichtangreifend und 8 Turmzahlen ungleich 0" in text
    assert "Ménage-Zahlen für n = 3 bis 12: 1, 2, 13, 80, 579, …, 59.216.642" in text
    assert "braucht das Sieb 124.344 Rechenschritte und 10 gespeicherte Zahlen, Held–Karp 9.225 Übergänge und 2.305 Zustände" in text
    assert "5.040 Hamiltonkreise mit Kosten von 8 bis 39; billigste Kosten 8, 1 Mal" in text
    assert "8,8·10⁻⁵ bei k = 25 und 2,8·10⁴ bei k = 40" in text
    assert "Von den Zahlen 1 bis 1000 sind 228 durch keinen der Teiler 2, 3, 5, 7 teilbar" in text
    assert "55.980 von 59.049 Zuordnungen von 10 Aufgaben auf 3 Maschinen lassen keine Maschine leer (94,8 %)" in text


def test_time_measurement_runs_on_click():
    at = _app()
    at.button(key="time_run").click().run(timeout=TIMEOUT)
    assert not at.exception and any("Gemessen auf diesem Rechner (Python)" in i.value for i in at.info)


@pytest.mark.parametrize("name,expected", [("Derangements: Hauptdiagonale 10 × 10", "1.334.961"), ("Ménage-Zahlen: 9 Paare", "43.387"), ("Leeres Brett: alle 7! Zuordnungen", "5.040"), ("Volles Brett: keine Zuordnung", "0")])
def test_board_presets_show_their_number(name, expected):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert _metrics(at)["Zuordnungen ohne verbotenes Feld"] == expected


def test_tour_preset_shows_tour_metrics():
    at = _app()
    at.sidebar.button(key="preset_Rundreise: alle Kanten, 8 Städte").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert _metrics(at) == {"Hamiltonkreise": "5.040", "Kleinste Kosten": "10", "Zahl der billigsten": "8", "Teilmengen im Sieb": "128"}


def test_tour_without_a_cycle_shows_dashes():
    at = _app({"task": "Rundreise", "n": "6", "share": "0"})
    assert not at.exception and not at.error
    assert _metrics(at) == {"Hamiltonkreise": "0", "Kleinste Kosten": "–", "Zahl der billigsten": "0", "Teilmengen im Sieb": "32"}
    assert any("es gibt keinen Hamiltonkreis" in e.value for e in at.success)


def test_tour_size_is_capped_with_a_note():
    at = _app({"task": "Rundreise", "n": "12", "share": "100"})
    assert not at.exception and any("höchstens 10 Städte" in i.value for i in at.info)
    assert _metrics(at)["Hamiltonkreise"] == "362.880"


def test_permalink_loads_and_clamps_the_values():
    at = _app({"task": "Rundreise", "board": "Ménage-Brett", "n": "99", "share": "-5", "r": "99", "seed": "5"})
    assert at.sidebar.selectbox(key="task_select").value == "Rundreise" and at.sidebar.selectbox(key="board_select").value == "Ménage-Brett"
    assert at.sidebar.slider(key="n_slider").value == C.N_MAX and at.sidebar.slider(key="share_slider").value == C.SHARE_MIN and at.sidebar.slider(key="r_slider").value == C.R_MAX


def test_permalink_with_garbage_is_ignored():
    at = _app({"task": "kein Name", "board": "x", "n": "abc", "share": "x", "r": "-", "seed": "zz"})
    assert at.sidebar.selectbox(key="task_select").value == C.DEFAULT_TASK and at.sidebar.selectbox(key="board_select").value == C.DEFAULT_BOARD and at.sidebar.slider(key="n_slider").value == C.DEFAULT_N


def test_random_seed_button_changes_the_seed():
    at = _app()
    before = at.sidebar.number_input(key="seed_input").value
    at.sidebar.button[-1].click().run(timeout=TIMEOUT)
    assert not at.exception and at.sidebar.number_input(key="seed_input").value != before


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders_without_error_or_checker_message(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error, name


def test_every_task_and_board_renders_without_error():
    for task in C.TASKS:
        for board in C.BOARDS:
            at = _app({"task": task, "board": board, "n": "7", "share": "60"})
            assert not at.error, (task, board, [e.value for e in at.error])


def test_playground_changes_with_its_widgets():
    at = _app()
    at.slider(key="play_limit").set_value(30).run(timeout=TIMEOUT)
    at.multiselect(key="play_divisors").set_value([2, 3]).run(timeout=TIMEOUT)
    assert not at.exception and any(e.value.startswith("Von den Zahlen 1 bis 30 sind 10 durch keinen der Teiler 2, 3 teilbar") for e in at.success)
    at.slider(key="play_n").set_value(12).run(timeout=TIMEOUT)
    assert not at.exception and any("Aufzählen entfällt" in e.value for e in at.success)
    at.multiselect(key="play_divisors").set_value([]).run(timeout=TIMEOUT)
    assert not at.exception and not at.error


def test_pdf_can_be_made_for_the_extreme_settings():
    for query in ({"n": "3"}, {"n": "12", "share": "100"}, {"task": "Rundreise", "n": "10", "share": "100", "r": "5"}, {"task": "Rundreise", "n": "3", "share": "0"}, {"board": "Ménage-Brett", "n": "12"}):
        at = _app(query)
        at.button(key="pdf_make").click().run(timeout=TIMEOUT)
        assert not at.exception, query
