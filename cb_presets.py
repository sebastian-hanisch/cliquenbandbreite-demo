"""SETTING_SPECS-Permalink-Muster, Presets und Zufalls-Seed-Buttons (Standardmuster aus dem Demo-Portfolio, wie in `band_presets.py`)."""

import random
from dataclasses import dataclass
from typing import Callable, Optional

import streamlit as st

import cb_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: Callable
    default: object
    lo: Optional[float] = None
    hi: Optional[float] = None


def _choice_from(options):
    def cast(value):
        value = str(value)
        if value not in options:
            raise ValueError(value)
        return value
    return cast


def _int_choice(options):
    def cast(value):
        value = int(value)
        if value not in options:
            raise ValueError(value)
        return value
    return cast


SETTING_SPECS = {
    "view_select": SettingSpec("view", _choice_from(C.VIEWS), "gnkb"),
    "n_slider": SettingSpec("n", int, C.DEFAULT_N, C.N_MIN, C.N_MAX),
    "k_slider": SettingSpec("k", int, C.DEFAULT_K, C.K_MIN, C.K_MAX),
    "b_slider": SettingSpec("b", int, C.DEFAULT_B, C.B_MIN, C.B_HARD_MAX),
    "universe_slider": SettingSpec("universe", int, C.DEFAULT_UNIVERSE, C.UNIVERSE_MIN, C.UNIVERSE_MAX),
    "khyper_slider": SettingSpec("khyper", int, C.DEFAULT_K_HYPER, C.K_HYPER_MIN, C.K_HYPER_MAX),
    "mhyper_slider": SettingSpec("mhyper", int, C.DEFAULT_M_HYPER, C.M_HYPER_MIN, C.M_HYPER_MAX),
    "grid_slider": SettingSpec("grid", int, C.DEFAULT_GRID, C.GRID_MIN, C.GRID_MAX),
    "kelectrode_slider": SettingSpec("kelectrode", int, C.DEFAULT_K_ELECTRODE, C.K_ELECTRODE_MIN, C.K_ELECTRODE_MAX),
    "melectrode_slider": SettingSpec("melectrode", int, C.DEFAULT_M_ELECTRODE, C.M_ELECTRODE_MIN, C.M_ELECTRODE_MAX),
    "bandwidth_algo_select": SettingSpec("bwalgo", _choice_from(C.BANDWIDTH_ALGORITHMS), "cm"),
    "cover_algo_select": SettingSpec("covalgo", _choice_from(C.COVER_ALGORITHMS), "greedy"),
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
    "cb_step": SettingSpec("step", _int_choice(tuple(C.STEPS)), 1),
}
PRESET_KEYS = {"view": "view_select", "n": "n_slider", "k": "k_slider", "b": "b_slider", "universe": "universe_slider", "khyper": "khyper_slider", "mhyper": "mhyper_slider",
               "grid": "grid_slider", "kelectrode": "kelectrode_slider", "melectrode": "melectrode_slider", "bwalgo": "bandwidth_algo_select", "covalgo": "cover_algo_select",
               "seed": "seed_input", "step": "cb_step"}
WIDGET_KEYS = {"n_slider": "n_widget", "k_slider": "k_widget", "b_slider": "b_widget", "universe_slider": "universe_widget", "khyper_slider": "khyper_widget",
               "mhyper_slider": "mhyper_widget", "grid_slider": "grid_widget", "kelectrode_slider": "kelectrode_widget", "melectrode_slider": "melectrode_widget",
               "bandwidth_algo_select": "bandwidth_algo_widget", "cover_algo_select": "cover_algo_widget", "seed_input": "seed_widget"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def load_permalink_settings():
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
                if spec.lo is not None:
                    value = max(spec.lo, value)
                if spec.hi is not None:
                    value = min(spec.hi, value)
                st.session_state[state_key] = value
            except (ValueError, TypeError):
                pass
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def store_from_widget(state_key):
    st.session_state[state_key] = st.session_state[WIDGET_KEYS[state_key]]


def push_to_widget(state_key):
    widget_key = WIDGET_KEYS[state_key]
    if widget_key in st.session_state:
        st.session_state[widget_key] = st.session_state[state_key]


def apply_preset(name):
    p = C.PRESETS[name]
    for key, state_key in PRESET_KEYS.items():
        if key in p:
            st.session_state[state_key] = p[key]
    for state_key in WIDGET_KEYS:
        push_to_widget(state_key)


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
    push_to_widget("seed_input")
