"""Bandbreite von G(n,k,b) und Cliquenueberdeckung - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zwoelftes und letztes Stueck der Graphen-und-Netzwerke-Reihe, ein Zusammenfluss von Stueck 11 (Bandbreite) und Stueck 5 (Graphfaerbung). Dieses Stueck ist als "mark=forschung" gekennzeichnet:
es baut direkt auf der eigenen, veroeffentlichten Forschungsarbeit des Autors auf - Engel und Hanisch, "Bandwidth of graphs resulting from the edge clique covering problem", arXiv:1605.00450
(2016). JEDE Zahl aus den Saetzen dieser Arbeit ist hier ein EIGENER NACHBAU, NUMERISCH NACHVOLLZOGEN - KEIN NEUER BEWEIS.

Lauffaehig mit: streamlit run app.py
"""

import streamlit as st

import cb_algorithm as A
import cb_constants as C
import cb_evaluation as ev
import cb_visualization as viz
from cb_presets import apply_preset, bounds, init_session_state_defaults, load_permalink_settings, randomize_seed, store_from_widget, sync_query_params, push_to_widget

st.set_page_config(page_title="Bandbreite von G(n,k,b) und Cliquenüberdeckung – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analyse(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _satz1a_check():
    return ev.satz1a_check()


@st.cache_data(show_spinner=False)
def _satz1b_sweep():
    return ev.satz1b_sweep()


@st.cache_data(show_spinner=False)
def _satz2_exploration():
    return ev.satz2_exploration()


@st.cache_data(show_spinner=False)
def _reduction_check():
    return ev.reduction_check()


@st.cache_data(show_spinner=False)
def _cover_quality():
    return ev.cover_quality()


def _german(x):
    return f"{x:,}".replace(",", ".") if isinstance(x, int) else x


st.title("🧬 Bandbreite von G(n,k,b) und Cliquenüberdeckung")
st.markdown(
    """
**Zwölftes und letztes Stück der Graphen-und-Netzwerke-Reihe** - ein Zusammenfluss von Stück 11 (Bandbreite) und Stück 5 (Graphfärbung). **Dieses Stück ist als "mark=forschung"
gekennzeichnet**: es baut direkt auf der eigenen, veröffentlichten Forschungsarbeit des Autors auf - **Engel und Hanisch, "Bandwidth of graphs resulting from the edge clique covering
problem", arXiv:1605.00450 (2016)**. Ein Hypergraph H=(V,E) modelliert z. B. ein Multielektroden-Array: ein Neuron mit Kontakt zu einer Elektrodenmenge S erzeugt eine **schwache Clique** im
**2-Sektionsgraphen** G_H; die kleinste **schwache Kantenclique-Überdeckung** (chi_e) identifiziert die Neuronen. **Proposition 1** des Papers zeigt chi_e(H) = chi_v(G~_H) - die
Eckenüberdeckungszahl durch Cliquen des **schwachen Kantenclique-Graphen**. Für die spezielle Graphenfamilie **G(n,k,b)** (k-elementige Teilmengen von {0,...,n} mit Spannweite <= b) gibt das
Paper eine **exakte Formel (Satz 1a)**, eine **Asymptotik (Satz 1b)** und für b~β·n mit **Satz 2** den exakten Wert (Fall a) bzw. nur Schranken mit einer **offenen Vermutung** für die obere Schranke (Fall b) für die Bandbreite an.
"""
)
st.caption(
    "**Jede Zahl aus den Sätzen dieses Papers ist hier ein eigener Nachbau, numerisch nachvollzogen - kein neuer Beweis.** Konrad Engel ist Ko-Autor der zugrundeliegenden Arbeit."
)

with st.expander("So funktioniert die Messung", expanded=True):
    st.markdown(
        """
1. **G(n,k,b)** (`gnkb_adjacency`): Ecken sind die k-elementigen Teilmengen X von {0,...,n} mit max(X)-min(X) <= b; X,Y benachbart, wenn max(X∪Y)-min(X∪Y) <= b. Bandbreite über
   Cuthill-McKee/Reverse-Cuthill-McKee, eine neue exakte Suche (`exact_bandwidth_layered`) und die geschlossene Satz-1a-Formel verglichen.
2. **2-Sektionsgraph und schwacher Kantenclique-Graph** (`two_section_graph`, `weak_edge_clique_graph`): u,v benachbart, wenn eine Hyperkante beide enthält; zwei Hyperkanten e,e' benachbart in
   G~_H, wenn e∪e' selbst eine schwache Clique ist.
3. **Cliquenüberdeckung** (`clique_cover_number`, `greedy_color`, `banded_coloring_dp`): exakt (Proposition 1 über G~_H) gegen Greedy gegen eine selbst entworfene, bandbreitenbeschränkte DP.
4. **Asymptotik/Vermutung**: Satz 1a exakt auf 28 Fällen, Satz 1b als Konvergenz gegen k·C(b,k), Satz 2 als reine Exploration (Fall a) ist bewiesen, Fall b) hat eine offene Vermutung) - ohne etwas davon zu entscheiden.
        """
    )

if C.PRESETS:
    st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
    preset_names = list(C.PRESETS.keys())
    rows_of_3 = [preset_names[i:i + 3] for i in range(0, len(preset_names), 3)]
    for row in rows_of_3:
        if not row:
            continue
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            with col:
                st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()
ss = st.session_state

with st.sidebar:
    st.header("⚙️ Einstellungen")
    view = st.radio("Ansicht", options=list(C.VIEWS), format_func=lambda v: C.VIEW_LABELS[v], key="view_select",
                     help="G(n,k,b): die Paper-Graphenfamilie selbst. Zufalls-Hypergraph/Elektrodengitter: allgemeines Testfeld für die Cliquenüberdeckung. Lehrbuch: die kleinste "
                          "nichttriviale G(n,k,b)-Instanz von Hand.")

    n, k, b = C.DEFAULT_N, C.DEFAULT_K, C.DEFAULT_B
    universe, k_hyper, m_hyper = C.DEFAULT_UNIVERSE, C.DEFAULT_K_HYPER, C.DEFAULT_M_HYPER
    grid, k_electrode, m_electrode = C.DEFAULT_GRID, C.DEFAULT_K_ELECTRODE, C.DEFAULT_M_ELECTRODE

    if view == "gnkb":
        n = st.slider("n (Grundmenge {0,...,n})", *bounds("n_slider"), value=int(ss["n_slider"]), key="n_widget", on_change=store_from_widget, args=("n_slider",))
        k = st.slider("k (Teilmengengröße)", *bounds("k_slider"), value=int(ss["k_slider"]), key="k_widget", on_change=store_from_widget, args=("k_slider",))
        b_max = min(n, C.B_HARD_MAX)
        b_val = min(int(ss["b_slider"]), b_max)
        if b_val != ss["b_slider"]:
            ss["b_slider"] = b_val
            push_to_widget("b_slider")
        b = st.slider("b (maximale Spannweite)", C.B_MIN, b_max, value=b_val, key="b_widget", on_change=store_from_widget, args=("b_slider",),
                      help="Satz 1a gilt für b >= (n+k-1)/2 - unterhalb dieser Schwelle wird nur gemessen, nicht mit der Formel verglichen.")
    elif view == "hyper":
        universe = st.slider("Grundmenge (Elektroden/Punkte)", *bounds("universe_slider"), value=int(ss["universe_slider"]), key="universe_widget", on_change=store_from_widget,
                              args=("universe_slider",))
        k_hyper = st.slider("k (Hyperkantengröße)", *bounds("khyper_slider"), value=int(ss["khyper_slider"]), key="khyper_widget", on_change=store_from_widget, args=("khyper_slider",))
        m_hyper = st.slider("m (Zahl der Hyperkanten)", *bounds("mhyper_slider"), value=int(ss["mhyper_slider"]), key="mhyper_widget", on_change=store_from_widget, args=("mhyper_slider",))
    elif view == "electrode":
        grid = st.slider("Elektrodenraster (grid × grid)", *bounds("grid_slider"), value=int(ss["grid_slider"]), key="grid_widget", on_change=store_from_widget, args=("grid_slider",))
        k_electrode = st.slider("k (Kontaktelektroden je Zelle)", *bounds("kelectrode_slider"), value=int(ss["kelectrode_slider"]), key="kelectrode_widget", on_change=store_from_widget,
                                 args=("kelectrode_slider",))
        m_electrode = st.slider("m (Zahl der Zellen)", *bounds("melectrode_slider"), value=int(ss["melectrode_slider"]), key="melectrode_widget", on_change=store_from_widget,
                                 args=("melectrode_slider",))

    st.markdown("---")
    if view in ("gnkb", "textbook"):
        bw_algo = st.radio("Sichtbare Bandbreiten-Nummerierung", options=list(C.BANDWIDTH_ALGORITHMS), format_func=lambda v: C.BANDWIDTH_ALGORITHM_LABELS[v], key="bandwidth_algo_widget",
                            on_change=store_from_widget, args=("bandwidth_algo_select",), index=list(C.BANDWIDTH_ALGORITHMS).index(ss["bandwidth_algo_select"]))
        cover_algo = ss["cover_algo_select"]
    else:
        cover_algo = st.radio("Sichtbares Cliquenüberdeckungs-Verfahren", options=list(C.COVER_ALGORITHMS), format_func=lambda v: C.COVER_ALGORITHM_LABELS[v], key="cover_algo_widget",
                               on_change=store_from_widget, args=("cover_algo_select",), index=list(C.COVER_ALGORITHMS).index(ss["cover_algo_select"]))
        bw_algo = ss["bandwidth_algo_select"]

    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), value=int(ss["seed_input"]), key="seed_widget", step=1, on_change=store_from_widget, args=("seed_input",),
                            help="Wirkt auf Zufalls-Hypergraph/Elektrodengitter und die 'Zufällig'-Nummerierung bei G(n,k,b).")
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)

step = st.select_slider("Schritt", options=list(C.STEPS), key="cb_step", format_func=lambda s: C.STEPS[s])

sync_query_params({"view_select": view, "n_slider": int(n) if view == "gnkb" else int(ss["n_slider"]), "k_slider": int(k) if view == "gnkb" else int(ss["k_slider"]),
                    "b_slider": int(b) if view == "gnkb" else int(ss["b_slider"]), "universe_slider": int(universe) if view == "hyper" else int(ss["universe_slider"]),
                    "khyper_slider": int(k_hyper) if view == "hyper" else int(ss["khyper_slider"]), "mhyper_slider": int(m_hyper) if view == "hyper" else int(ss["mhyper_slider"]),
                    "grid_slider": int(grid) if view == "electrode" else int(ss["grid_slider"]), "kelectrode_slider": int(k_electrode) if view == "electrode" else int(ss["kelectrode_slider"]),
                    "melectrode_slider": int(m_electrode) if view == "electrode" else int(ss["melectrode_slider"]), "bandwidth_algo_select": bw_algo, "cover_algo_select": cover_algo,
                    "seed_input": int(seed), "cb_step": int(step)})

settings = ev.Settings(view=view, n=int(n), k=int(k), b=int(b), universe=int(universe), k_hyper=int(k_hyper), m_hyper=int(m_hyper), grid=int(grid), k_electrode=int(k_electrode),
                        m_electrode=int(m_electrode), seed=int(seed))

with st.spinner("Werte die Instanz aus..."):
    if view == "textbook":
        tb_n, tb_k, tb_b, a = _analyse(settings)
    else:
        a = _analyse(settings)

st.markdown("## 🎯 Die Instanz")
if view in ("gnkb", "textbook"):
    label_n, label_k, label_b = (tb_n, tb_k, tb_b) if view == "textbook" else (n, k, b)
    st.markdown(f"**G({label_n},{label_k},{label_b})**: {_german(a.n_vertices)} Ecken. Cuthill-McKee-Bandbreite **{a.bw_cm}**"
                + (f", exakt **{a.bw_exact}**" if a.bw_exact is not None else ", exakt nicht in angemessener Zeit berechnet")
                + (f", Satz-1a-Formel **{a.bw_satz1a}**" if a.satz1a_applicable else " (Satz 1a hier nicht anwendbar: b < (n+k-1)/2)") + ".")
else:
    st.markdown(f"**{_german(a.universe)} Grundelemente, {_german(len(a.hyperedges))} Hyperkanten**. Schwache Kantenclique-Überdeckung: exakt (Proposition 1) **{a.chi_e_proposition1}**, "
                f"Greedy **{a.chi_e_greedy}**, bandbreitenbeschränkte DP **{a.chi_e_banded_dp}**"
                + (f", Definitions-Brute-Force **{a.chi_e_bruteforce}**" if a.chi_e_bruteforce is not None else "") + ".")

if step == 1:
    if view in ("gnkb", "textbook"):
        perms = {"natural": a.perm_natural, "random": a.perm_random, "cm": a.perm_cm, "rcm": a.perm_rcm}
        if bw_algo in perms:
            st.plotly_chart(viz.build_gnkb_intervals(a.verts, perms[bw_algo], f"Ecken sortiert nach {C.BANDWIDTH_ALGORITHM_LABELS[bw_algo]}"), width="stretch",
                             key=f"s1_intervals_{view}_{n}_{k}_{b}_{seed}_{bw_algo}")
        values = {"Natürlich": a.bw_natural, "Zufällig": a.bw_random, "Cuthill-McKee": a.bw_cm, "Reverse Cuthill-McKee": a.bw_rcm, "Exakt": a.bw_exact,
                  "Satz-1a-Formel": a.bw_satz1a if a.satz1a_applicable else None}
        st.plotly_chart(viz.build_bandwidth_bars(values), width="stretch", key=f"s1_bars_{view}_{n}_{k}_{b}_{seed}")
        st.caption("Reverse Cuthill-McKee hat (wie in Stück 11 bewiesen) exakt dieselbe Bandbreite wie Cuthill-McKee - hier zusätzlich auf G(n,k,b) bestätigt.")
    else:
        st.info("Schritt 1 (G(n,k,b) und seine Bandbreite) ist für die Ansichten Zufalls-Hypergraph/Elektrodengitter nicht anwendbar - wählen Sie G(n,k,b) oder Lehrbuch.")
elif step == 2:
    if view in ("hyper", "electrode"):
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(viz.build_two_section_graph(a.universe, a.two_section, a.hyperedges, a.positions), width="stretch",
                             key=f"s2_ts_{view}_{universe}_{k_hyper}_{m_hyper}_{grid}_{k_electrode}_{m_electrode}_{seed}")
        with c2:
            st.plotly_chart(viz.build_weg_graph(a.weg_adj, a.hyperedges), width="stretch",
                             key=f"s2_weg_{view}_{universe}_{k_hyper}_{m_hyper}_{grid}_{k_electrode}_{m_electrode}_{seed}")
        st.caption("Links: der 2-Sektionsgraph G_H (Ecken = Grundmenge). Rechts: der schwache Kantenclique-Graph G~_H (Ecken = Hyperkanten) - zwei Hyperkanten sind verbunden, wenn ihre "
                   "Vereinigung selbst eine schwache Clique ist.")
    else:
        st.info("Schritt 2 (Von der Hyperkante zur Clique) ist für die Ansicht G(n,k,b)/Lehrbuch nicht anwendbar - wählen Sie Zufalls-Hypergraph oder Elektrodengitter.")
elif step == 3:
    if view in ("hyper", "electrode"):
        st.plotly_chart(viz.build_cover_comparison_bars(a.chi_e_proposition1, a.chi_e_greedy, a.chi_e_banded_dp), width="stretch",
                         key=f"s3_bars_{view}_{universe}_{k_hyper}_{m_hyper}_{grid}_{k_electrode}_{m_electrode}_{seed}")
        with st.spinner("Rechne den Cliquenüberdeckungs-Qualitätsvergleich..."):
            cq_rows = _cover_quality()
        st.plotly_chart(viz.build_cover_quality_chart(cq_rows), width="stretch", key="s3_quality")
        st.plotly_chart(viz.build_dp_effort_chart(cq_rows), width="stretch", key="s3_effort")
        st.caption("Die bandbreitenbeschränkte DP (`banded_coloring_dp`) benutzt die Cuthill-McKee-Reihenfolge auf dem Komplementgraphen; sie gewinnt auf manchen Instanzen gegen Greedy, "
                   "verliert auf anderen - ehrlich in beide Richtungen gemessen (s. README 'Befunde').")
    else:
        st.info("Schritt 3 (Cliquenüberdeckung im Vergleich) ist für die Ansicht G(n,k,b)/Lehrbuch nicht anwendbar - wählen Sie Zufalls-Hypergraph oder Elektrodengitter.")
else:
    with st.spinner("Rechne Satz 1a/1b/2 (kann einige Sekunden dauern)..."):
        s1a_rows = _satz1a_check()
        s1b_rows = _satz1b_sweep()
        s2_rows = _satz2_exploration()
    st.markdown("### Satz 1a (exakt, b ≥ (n+k-1)/2)")
    st.plotly_chart(viz.build_satz1a_scatter(s1a_rows), width="stretch", key="s4_satz1a")
    n_match = sum(1 for r in s1a_rows if r["match"])
    st.caption(f"{n_match} von {len(s1a_rows)} bestätigten (n,k,b)-Tripeln: Formel == exakte Suche (`exact_bandwidth_layered`), EIGENER NACHBAU, kein neuer Beweis.")
    st.markdown("### Satz 1b (Asymptotik, b=o(n))")
    st.plotly_chart(viz.build_satz1b_chart(s1b_rows), width="stretch", key="s4_satz1b")
    st.caption("Verhältnis gemessene Bandbreite / [k·C(b,k)] über wachsendes n - bei b = 2 und b = 3 liegt es bei 1; bei b = 4 gibt die exakte Suche meist auf (nur n = 10 gelingt, dort 11 < 12); sonst bleibt eine Cuthill-McKee-Obergrenze, sie liegt darüber (ca. 1,1 bis 1,8) und nähert sich 1 nicht. KEIN Gültigkeitstest (die Formel gilt nur im Grenzwert n→∞).")
    st.markdown("### Satz 2 (b~β·n: Fall a) exakt, Fall b) offene Vermutung)")
    beta_choice = st.select_slider("β", options=C.SATZ2_BETAS, key="satz2_beta")
    st.plotly_chart(viz.build_satz2_chart(s2_rows, beta_choice), width="stretch", key=f"s4_satz2_{beta_choice}")
    if A.satz2_case(beta_choice) == "a":
        st.caption(f"Für β = {beta_choice} gilt im Paper Fall a): B ~ c1·n^k ist asymptotisch bewiesen (c2+c3 ist hier nur die allgemeine Obergrenze, nicht der Wert). Die Kurve ist die Cuthill-McKee-Obergrenze bei endlichem n, keine exakte Bandbreite.")
    else:
        st.caption(f"Für β = {beta_choice} gilt im Paper Fall b): bewiesen sind nur die Schranken max{{c1, c2+c3/q^(k-1)}} ≲ B/n^k ≲ c2+c3; dass die obere Schranke der wahre Wert ist, ist die offene Vermutung.")
    st.caption("NUR EXPLORATION mit endlichem n - sie bestätigt weder den bewiesenen Wert in Fall a) noch entscheidet sie die offene Vermutung in Fall b), unabhängig davon, wie nah die Kurven an den Schranken liegen.")

st.markdown("---")

st.markdown("## 🎯 Was diese Demo zeigt")
r1, r2, r3, r4 = st.columns(4)
if view in ("gnkb", "textbook"):
    r1.metric("Ecken |V(G(n,k,b))|", _german(a.n_vertices))
    r2.metric("Bandbreite Cuthill-McKee", a.bw_cm)
    r3.metric("Exakt", a.bw_exact if a.bw_exact is not None else "n/a")
    r4.metric("Satz-1a-Formel", a.bw_satz1a if a.satz1a_applicable else "n/a")
else:
    r1.metric("Hyperkanten", _german(len(a.hyperedges)))
    r2.metric("chi_e exakt (Proposition 1)", a.chi_e_proposition1)
    r3.metric("chi_e Greedy", a.chi_e_greedy)
    r4.metric("chi_e bandbreitenbeschränkte DP", a.chi_e_banded_dp)

st.markdown("---")

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Satz 1a gilt allgemein** | Nur für b >= (n+k-1)/2 bewiesen - außerhalb dieser Schwelle wird nur GEMESSEN, nicht mit der Formel verglichen. | - |
| **`exact_bandwidth_layered` löst jede Instanz** | Nein - Bandbreitenminimierung ist NP-vollständig; ab einem `node_budget` gibt der Löser ehrlich "nicht in angemessener Zeit berechnet" zurück, statt zu hängen (gemessen: Schwierigkeit hängt NICHT einfach von der Eckenzahl ab, s. README). | - |
| **Satz 2 ist entschieden** | Nur teilweise: Fall a) ist im Paper bewiesen, in Fall b) ist die obere Schranke eine offene Vermutung. Die Demo zeigt nur eine Exploration mit endlichem n, niemals eine Entscheidung. | - |
| **`banded_coloring_dp` schlägt Greedy immer** | Nein - ein Greedy-Verfahren mit Fenster-Zustand, gemessen mal besser, mal schlechter als eine andere Greedy-Reihenfolge (nie besser als das globale Optimum). | - |
| **Elektrodengitter-Beispiel ist realistisch** | Nein - eine stark vereinfachte, synthetische Illustration der Paper-Motivation, KEINE Rekonstruktion der echten Spike-Simulation aus `delay-graph-demo`. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**2-Sektionsgraph** $G_H=(V,E_H)$ eines Hypergraphen $H=(V,E)$: $\{u,v\}\in E_H$ genau dann, wenn eine Hyperkante $e\in E$ beide enthält.

**Schwache Clique.** $C\subseteq V$ ist eine schwache Clique von $H$, wenn $C$ eine Clique in $G_H$ ist.

**Schwache Kantenclique-Überdeckung.** Eine Familie schwacher Cliquen $\mathcal{C}$, sodass jede Hyperkante $e\in E$ Teilmenge eines $C\in\mathcal{C}$ ist; $\bar\chi_e(H)$ ist die kleinste
Familiengröße.

**Schwacher Kantenclique-Graph** $\tilde G_H=(\tilde V,\tilde E)$: $\tilde V=E$; zwei Hyperkanten $e,e'$ sind benachbart, wenn $e\cup e'$ selbst eine schwache Clique ist.

**Proposition 1** (Engel und Hanisch 2016): $\bar\chi_e(H)=\bar\chi_v(\tilde G_H)$, wobei $\bar\chi_v$ die EckenÜBERDECKUNGSzahl DURCH CLIQUEN ist ($=\chi(\overline{\tilde G_H})$, die
Färbungszahl des Komplementgraphen) - NICHT die Färbungszahl von $\tilde G_H$ selbst.

**$G_{n,k,b}$**: Ecken sind die $k$-elementigen Teilmengen $X\subseteq\{0,\dots,n\}$ mit $\max(X)-\min(X)\le b$; $X,Y$ benachbart, wenn $\max(X\cup Y)-\min(X\cup Y)\le b$.

**Satz 1a** (für $b\ge(n+k-1)/2$): $B(G_{n,k,b})=\left\lceil\frac{(n+1)\binom{b}{k-1}-(k-1)\binom{b+1}{k}+\binom{2b-n+1}{k}-2}{2}\right\rceil$.

**Satz 1b** (für $b=o(n)$): $B(G_{n,k,b})\sim k\binom{b}{k}$.

**Satz 2** (für $b\sim\beta n$, OFFENE VERMUTUNG): mit $1=q\beta+r$ ($q\ge2$ ganzzahlig, $0\le r<\beta$), für $r>\frac{q-1}{q^2+q-1}$: $\max\{c_1,c_2+c_3/q^{k-1}\}n^k\lesssim B\lesssim(c_2+c_3)n^k$;
die Menge der $\beta$, für die die obere Schranke nicht bewiesen ist, hat Lebesgue-Maß $\approx0{,}119$.

**Alle Zahlen aus diesen Sätzen sind hier ein eigener Nachbau, numerisch nachvollzogen - kein neuer Beweis.**

**Literatur.** Engel, K., & Hanisch, S. (2016). *Bandwidth of graphs resulting from the edge clique covering problem.* arXiv:1605.00450 [math.CO]. Cuthill, E., & McKee, J. (1969). *Reducing
the bandwidth of sparse symmetric matrices.* Proceedings of the 24th National Conference ACM, 157–172. George, A., & Liu, J. W. H. (1979). *An implementation of a pseudoperipheral node
finder.* ACM Transactions on Mathematical Software 5(3), 284–295. Papadimitriou, C. H. (1976). *The NP-completeness of the bandwidth minimization problem.* Computing 16(3), 263–270. Unger,
W. (1998). *The complexity of the approximation of the bandwidth problem.* 39th IEEE FOCS, 82–91. Bodlaender, H. L. (1988). *Dynamic programming on graphs with bounded treewidth.* ICALP 1988.

Implementiert in `cb_algorithm.py` (Bandbreite, 2-Sektionsgraph, Cliquenüberdeckung, bandbreitenbeschränkte DP), `cb_scenario.py` (G(n,k,b), Hypergraphen), `cb_evaluation.py` (Auswertung,
Satz-1a/1b/2-Messreihen).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Graphen und Netzwerke: BFS bis Cliquenbandbreite](https://sebastianhanisch.net/konzepte-graphen-netzwerke.html)."
)
