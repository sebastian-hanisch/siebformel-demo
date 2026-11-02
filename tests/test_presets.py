"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import sbf_constants as C
import sbf_evaluation as ev
import sbf_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["task"] in C.TASKS and preset["board"] in C.BOARDS and C.N_MIN <= preset["n"] <= C.N_MAX, name
        assert C.SHARE_MIN <= preset["share"] <= C.SHARE_MAX and C.R_MIN <= preset["r"] <= C.R_MAX and 0 <= preset["seed"] <= C.SEED_MAX, name


def test_every_preset_passes_the_checker_without_notes():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.notes == [] and a.n_eff == preset["n"], name


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[next(iter(C.PRESETS))]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_presets_show_what_their_help_says():
    stats = {name: ev.analyse(ev.Settings(**p)) for name, p in C.PRESETS.items()}
    assert stats["Derangements: Hauptdiagonale 10 × 10"].info["nonzero"] == 11 and stats["Derangements: Hauptdiagonale 10 × 10"].info["subsets"] == 1024
    assert stats["Leeres Brett: alle 7! Zuordnungen"].info["nonzero"] == 1 and stats["Volles Brett: keine Zuordnung"].info["value"] == 0
    assert stats["Rundreise: alle Kanten, 8 Städte"].info["cycles"] == 5040 and stats["Rundreise: alle Kanten, 8 Städte"].info["subsets"] == 128
    assert stats["Rundreise: Kanten fehlen, Kosten bis 5"].info["cycles"] < 5040
    values = {(a.settings.task, a.info.get("value", a.info.get("cycles")), a.info.get("best")) for a in stats.values()}
    assert len(values) == len(C.PRESETS)
