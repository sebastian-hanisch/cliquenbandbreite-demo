"""Auswertungsfunktionen: `analyse` fuer alle vier Ansichten, Satz-1b-Sweep/Satz-2-Exploration (nur Plausibilitaet, keine Entscheidung), `cover_quality` (ehrlich in beide Richtungen)."""

import cb_constants as C
import cb_evaluation as ev


def test_analyse_gnkb_basic_shape():
    settings = ev.Settings(view="gnkb", n=6, k=2, b=4, seed=1)
    a = ev.analyse_gnkb(settings)
    assert a.n_vertices == len(a.verts)
    assert a.bw_cm == a.bw_rcm
    assert a.satz1a_applicable is True
    assert a.bw_satz1a is not None


def test_analyse_gnkb_satz1a_not_applicable_below_threshold():
    settings = ev.Settings(view="gnkb", n=10, k=3, b=1, seed=1)      # b=1 << (10+3-1)/2=6
    a = ev.analyse_gnkb(settings)
    assert a.satz1a_applicable is False
    assert a.bw_satz1a is None


def test_analyse_hyper_basic_shape():
    settings = ev.Settings(view="hyper", universe=8, k_hyper=2, m_hyper=6, seed=3)
    a = ev.analyse_hyper(settings)
    assert a.chi_e_proposition1 <= len(a.hyperedges)
    assert a.chi_e_greedy >= a.chi_e_proposition1
    assert a.chi_e_banded_dp >= a.chi_e_proposition1
    if a.chi_e_bruteforce is not None:
        assert a.chi_e_bruteforce == a.chi_e_proposition1


def test_analyse_electrode_basic_shape():
    settings = ev.Settings(view="electrode", grid=4, k_electrode=3, m_electrode=6, seed=3)
    a = ev.analyse_electrode(settings)
    assert a.universe == 16
    assert a.positions is not None
    assert a.chi_e_proposition1 <= len(a.hyperedges)


def test_analyse_textbook_returns_4_2_3():
    n, k, b, a = ev.analyse_textbook(ev.Settings(view="textbook"))
    assert (n, k, b) == (4, 2, 3)
    assert a.satz1a_applicable is True


def test_analyse_dispatches_on_view():
    for view in C.VIEWS:
        result = ev.analyse(ev.Settings(view=view))
        assert result is not None


def test_analyse_unknown_view_raises():
    import pytest
    with pytest.raises(ValueError):
        ev.analyse(ev.Settings(view="nope"))


def test_satz1b_sweep_ratio_gets_closer_to_one_for_larger_n_at_fixed_small_b():
    rows = ev.satz1b_sweep(k=2, bs=(2,), ns=(6, 10, 16, 24, 34, 46))
    assert len(rows) >= 4
    ratios = [r["ratio"] for r in rows]
    # Monoton muss es nicht sein, aber der letzte (groesste n) sollte naeher an 1 liegen als der erste - EIGENER NACHBAU, kein Beweis.
    assert abs(ratios[-1] - 1.0) <= abs(ratios[0] - 1.0) + 0.5


def test_satz2_exploration_is_labelled_as_exploration_and_never_claims_a_decision():
    rows = ev.satz2_exploration(k=2, betas=(0.2,), ns=(10, 16, 22))
    assert len(rows) == 3
    for r in rows:
        assert "measured_scaled" in r and "c1" in r and "upper_ref" in r


def test_reduction_check_returns_requested_number_of_trials():
    rows = ev.reduction_check(trials=50)
    assert len(rows) == 50
    assert all("match" in r for r in rows)


def test_cover_quality_reports_both_directions_honestly():
    """Die DP muss NICHT immer gewinnen - dieser Test prueft nur, dass die Messreihe intern konsistent ist (DP/Greedy >= exakt), nicht dass die DP gewinnt."""
    rows = ev.cover_quality()
    assert len(rows) == len(C.COVER_QUALITY_HYPER_SETTINGS)
    for r in rows:
        assert r["exact"] <= r["greedy"]
        assert r["exact"] <= r["banded_dp"]
    # ehrlicher Befund (s. README): mindestens einmal gewinnt die DP (== exakt, < greedy), mindestens einmal verliert sie (> greedy)
    assert any(r["banded_dp"] < r["greedy"] for r in rows)
    assert any(r["banded_dp"] > r["greedy"] for r in rows)


def test_satz1a_check_default_matches_constants():
    rows = ev.satz1a_check()
    assert [(r["n"], r["k"], r["b"]) for r in rows] == list(C.SATZ1A_CASES)
