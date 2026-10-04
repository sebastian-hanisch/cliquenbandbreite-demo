"""AppTest-Rauchtests: Voreinstellung, jedes Preset, jede Ansicht/jeder Schritt, bedingte Regler, Permalink-Grenzen, Footer."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import cb_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(step=1, **state):
    at = AppTest.from_file(APP, default_timeout=300)
    state.setdefault("cb_step", step)
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    return at


def _ok(at):
    assert not at.exception, [e.value for e in at.exception]


def _click(at, key):
    next(b for b in at.button if b.key == key).click().run()


def test_default_run_shows_the_summary():
    at = _run()
    _ok(at)
    assert list(at.metric)


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_button_runs(name):
    at = _run()
    _click(at, f"preset_{name}")
    _ok(at)
    p, ss = C.PRESETS[name], at.session_state
    assert ss["view_select"] == p["view"] and ss["cb_step"] == p["step"]


@pytest.mark.parametrize("step", [1, 2, 3, 4])
@pytest.mark.parametrize("view", list(C.VIEWS))
def test_every_step_runs_for_every_view(step, view):
    at = _run(step=step, view_select=view)
    _ok(at)
    assert at.session_state["cb_step"] == step
    assert at.session_state["view_select"] == view


def _chart_count(at):
    return len(at.get("plotly_chart"))


def test_step1_shows_charts_for_gnkb_and_a_hint_otherwise():
    at = _run(step=1, view_select="gnkb")
    _ok(at)
    assert _chart_count(at) >= 2
    at_hyper = _run(step=1, view_select="hyper")
    _ok(at_hyper)
    assert any("nicht anwendbar" in i.value for i in at_hyper.info)


def test_step2_shows_two_charts_for_hyper_and_electrode():
    at = _run(step=2, view_select="hyper")
    _ok(at)
    assert _chart_count(at) >= 2
    at2 = _run(step=2, view_select="electrode")
    _ok(at2)
    assert _chart_count(at2) >= 2
    at_gnkb = _run(step=2, view_select="gnkb")
    _ok(at_gnkb)
    assert any("nicht anwendbar" in i.value for i in at_gnkb.info)


def test_step3_shows_cover_comparison_for_hyper_and_electrode():
    at = _run(step=3, view_select="hyper")
    _ok(at)
    assert _chart_count(at) >= 3
    at_textbook = _run(step=3, view_select="textbook")
    _ok(at_textbook)
    assert any("nicht anwendbar" in i.value for i in at_textbook.info)


def test_step4_shows_satz1a_1b_2_charts_regardless_of_view():
    for view in C.VIEWS:
        at = _run(step=4, view_select=view)
        _ok(at)
        assert _chart_count(at) >= 3


def test_sidebar_shows_the_controls_that_belong_to_the_view():
    gnkb = _run(view_select="gnkb")
    assert any(w.key == "n_widget" for w in gnkb.slider) and not any(w.key == "universe_widget" for w in gnkb.slider)
    hyper = _run(view_select="hyper")
    assert any(w.key == "universe_widget" for w in hyper.slider) and not any(w.key == "n_widget" for w in hyper.slider)
    electrode = _run(view_select="electrode")
    assert any(w.key == "grid_widget" for w in electrode.slider) and not any(w.key == "universe_widget" for w in electrode.slider)
    textbook = _run(view_select="textbook")
    assert not any(w.key in ("n_widget", "universe_widget", "grid_widget") for w in textbook.slider)


def test_b_slider_never_exceeds_n():
    at = _run(view_select="gnkb", n_slider=4, b_slider=99)
    _ok(at)
    assert at.session_state["b_slider"] <= 4


def test_dice_button_changes_the_seed_and_the_visible_widget():
    at = _run(view_select="hyper")
    old = at.session_state["seed_input"]
    next(b for b in at.button if b.label == "🎲 Neue Instanz generieren").click().run()
    _ok(at)
    assert at.session_state["seed_input"] != old and at.session_state["seed_widget"] == at.session_state["seed_input"]


def test_permalink_values_are_clamped_and_invalid_choices_fall_back_to_the_default():
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in dict(view="nope", n="9999", k="9999", b="9999", universe="9999", khyper="9999", mhyper="9999", grid="9999", kelectrode="9999", melectrode="9999", bwalgo="up",
                      covalgo="up", seed="-4", step="9").items():
        at.query_params[k] = v
    at.run()
    _ok(at)
    ss = at.session_state
    assert ss["view_select"] == "gnkb"
    assert ss["n_slider"] == C.N_MAX
    assert ss["k_slider"] == C.K_MAX
    assert ss["b_slider"] == C.B_HARD_MAX
    assert ss["universe_slider"] == C.UNIVERSE_MAX
    assert ss["bandwidth_algo_select"] == "cm"
    assert ss["cover_algo_select"] == "greedy"
    assert ss["seed_input"] == 0
    assert ss["cb_step"] == 1


def test_permalink_accepts_valid_values_and_writes_them_back():
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in dict(view="hyper", universe="8", khyper="2", mhyper="6", seed="7", step="2").items():
        at.query_params[k] = v
    at.run()
    _ok(at)
    ss = at.session_state
    assert (ss["view_select"], ss["universe_slider"], ss["khyper_slider"], ss["mhyper_slider"], ss["seed_input"], ss["cb_step"]) == ("hyper", 8, 2, 6, 7, 2)
    qp = at.query_params
    assert qp["seed"] in (["7"], "7") and qp["step"] in (["2"], "2")


def test_switching_view_back_and_forth_keeps_the_stored_values():
    at = _run(view_select="gnkb", n_slider=9, k_slider=3, seed_input=11)
    at.session_state["view_select"] = "hyper"
    at.run()
    _ok(at)
    at.session_state["view_select"] = "gnkb"
    at.run()
    _ok(at)
    assert at.session_state["n_widget"] == 9 and at.session_state["k_widget"] == 3 and at.session_state["seed_widget"] == 11


def test_footer_limits_and_literature_are_present():
    at = _run()
    assert any("Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net)" in c.value for c in at.caption)
    assert any("Wo die Annahmen enden" in s.value for s in at.subheader)
    assert any("Engel" in m.value and "Hanisch" in m.value and "arXiv:1605.00450" in m.value for e in at.expander for m in e.markdown)
    assert any("eigener Nachbau" in m.value for e in at.expander for m in e.markdown)


def test_footer_credits_konrad_engel_as_coauthor():
    at = _run()
    assert any("Konrad Engel" in c.value for c in at.caption)
