"""Auswertung: eine Instanz mit Bandbreite unter allen sichtbaren Nummerierungen (`analyse`, Schritt 1/2/3-Grundlage), die schwache Kantenclique-Ueberdeckung exakt/Greedy/DP (`analyse`,
Schritt 2/3), der Satz-1a-Check (`satz1a_check`, Korrektheits-Kette Punkt 3), der Satz-1b-Sweep (`satz1b_sweep`), die Satz-2-Exploration (`satz2_exploration`, EXPLIZIT nur Exploration, keine
Entscheidung der offenen Vermutung), der Proposition-1-Check (`reduction_check`, Korrektheits-Kette Punkt 1) und der Cliquenueberdeckungs-Qualitaetsvergleich (`cover_quality`)."""

import random
from dataclasses import dataclass

import cb_algorithm as A
import cb_constants as C
import cb_scenario as S


@dataclass
class Settings:
    view: str = "gnkb"                        # "gnkb" | "hyper" | "electrode" | "textbook"
    n: int = C.DEFAULT_N
    k: int = C.DEFAULT_K
    b: int = C.DEFAULT_B
    universe: int = C.DEFAULT_UNIVERSE
    k_hyper: int = C.DEFAULT_K_HYPER
    m_hyper: int = C.DEFAULT_M_HYPER
    grid: int = C.DEFAULT_GRID
    k_electrode: int = C.DEFAULT_K_ELECTRODE
    m_electrode: int = C.DEFAULT_M_ELECTRODE
    seed: int = C.DEFAULT_SEED


# --- G(n,k,b)-Analyse (Schritt 1) ---------------------------------------------------------------------------------------------------------------------------


@dataclass
class GnkbAnalysis:
    verts: list
    adj: list
    n_vertices: int
    perm_natural: list
    perm_random: list
    perm_cm: list
    perm_rcm: list
    bw_natural: int
    bw_random: int
    bw_cm: int
    bw_rcm: int
    bw_exact: object            # None, falls exact_bandwidth_layered das node_budget ueberschreitet
    bw_satz1a: object           # None, falls b < (n+k-1)/2 (Satz 1a nicht anwendbar)
    satz1a_applicable: bool
    cm_order: list


def analyse_gnkb(settings):
    verts, adj = S.gnkb_adjacency(settings.n, settings.k, settings.b)
    n_vertices = len(verts)
    natural = list(range(n_vertices))
    rnd = A.random_permutation(n_vertices, settings.seed) if n_vertices else []
    cm = A.cuthill_mckee(adj) if n_vertices else []
    rcm = A.reverse_cuthill_mckee(adj) if n_vertices else []
    cm_order = A.cuthill_mckee_order(adj) if n_vertices else []
    exact = A.exact_bandwidth_layered(adj, node_budget=C.APP_NODE_BUDGET) if n_vertices > 0 else None
    satz1a_applicable = settings.k >= 1 and 2 * settings.b >= settings.n + settings.k - 1
    satz1a_value = A.bandwidth_satz1a(settings.n, settings.k, settings.b) if satz1a_applicable else None
    return GnkbAnalysis(
        verts=verts, adj=adj, n_vertices=n_vertices, perm_natural=natural, perm_random=rnd, perm_cm=cm, perm_rcm=rcm,
        bw_natural=A.bandwidth(adj, natural) if n_vertices else 0, bw_random=A.bandwidth(adj, rnd) if n_vertices else 0,
        bw_cm=A.bandwidth(adj, cm) if n_vertices else 0, bw_rcm=A.bandwidth(adj, rcm) if n_vertices else 0,
        bw_exact=exact, bw_satz1a=satz1a_value, satz1a_applicable=satz1a_applicable, cm_order=cm_order,
    )


# --- Hypergraph-Analyse (Schritt 2/3): 2-Sektionsgraph, schwache Cliquen, chi_e ------------------------------------------------------------------------------


@dataclass
class HyperAnalysis:
    universe: int
    hyperedges: tuple
    two_section: list
    weg_adj: list
    chi_e_bruteforce: object     # None, falls m > BRUTEFORCE_COVER_LIMIT
    chi_e_proposition1: object   # chi_v(G~_H) ueber clique_cover_number
    chi_e_greedy: int
    chi_e_banded_dp: int
    cm_order_complement: list
    bandwidth_of_cm_complement: int
    steps_exact: int
    steps_greedy: int
    steps_banded_dp: int
    positions: object = None     # nur electrode-Ansicht: (n,2)-Array der Elektrodenzentren


def _cover_from_hyperedges(universe, hyperedges, positions=None):
    m = len(hyperedges)
    ts = A.two_section_graph(universe, hyperedges)
    weg = A.weak_edge_clique_graph(universe, hyperedges)
    chi_e_bf = A.weak_edge_clique_cover_bruteforce(universe, hyperedges) if m <= C.BRUTEFORCE_COVER_LIMIT else None
    chi_e_p1, steps_exact = A.clique_cover_number(weg, exact_limit=C.CHROM_EXACT_LIMIT) if m > 0 else (0, 0)
    comp = A.complement(weg) if m > 0 else []
    natural_order = list(range(m))
    greedy_res = A.greedy_color(comp, natural_order) if m > 0 else A.ColoringResult([], 0, 0, [], "greedy")
    cm_order_complement = A.cuthill_mckee_order(comp) if m > 0 else []
    bw_cm_complement = A.bandwidth(comp, A.cuthill_mckee(comp)) if m > 0 else 0
    dp_res = A.banded_coloring_dp(comp, cm_order_complement, bw_cm_complement) if m > 0 else A.BandedColoringResult([], 0, 0)
    return HyperAnalysis(
        universe=universe, hyperedges=tuple(hyperedges), two_section=ts, weg_adj=weg,
        chi_e_bruteforce=chi_e_bf, chi_e_proposition1=chi_e_p1, chi_e_greedy=greedy_res.k, chi_e_banded_dp=dp_res.k,
        cm_order_complement=cm_order_complement, bandwidth_of_cm_complement=bw_cm_complement,
        steps_exact=steps_exact, steps_greedy=greedy_res.steps, steps_banded_dp=dp_res.steps, positions=positions,
    )


def analyse_hyper(settings):
    universe, edges = S.random_k_uniform_hypergraph(settings.universe, settings.k_hyper, settings.m_hyper, settings.seed)
    return _cover_from_hyperedges(universe, edges)


def analyse_electrode(settings):
    universe, edges, positions = S.electrode_hypergraph(settings.grid, settings.k_electrode, settings.m_electrode, settings.seed)
    return _cover_from_hyperedges(universe, edges, positions=positions)


def analyse_textbook(settings):
    n, k, b, verts, adj = S.textbook_gnkb(C.TEXTBOOK_N, C.TEXTBOOK_K, C.TEXTBOOK_B)
    gnkb = analyse_gnkb(Settings(view="gnkb", n=n, k=k, b=b))
    return n, k, b, gnkb


def analyse(settings):
    if settings.view == "gnkb":
        return analyse_gnkb(settings)
    if settings.view == "hyper":
        return analyse_hyper(settings)
    if settings.view == "electrode":
        return analyse_electrode(settings)
    if settings.view == "textbook":
        return analyse_textbook(settings)
    raise ValueError(f"unbekannte Ansicht {settings.view}")


# --- Satz 1a: exakt gegen die Formel (Korrektheits-Kette Punkt 3) -------------------------------------------------------------------------------------------


def satz1a_check(cases=C.SATZ1A_CASES):
    """Fuer jedes (n,k,b)-Tripel (b >= (n+k-1)/2): `bandwidth_satz1a` gegen `exact_bandwidth_layered`. EIGENER NACHBAU, numerisch nachvollzogen - kein neuer Beweis."""
    rows = []
    for n, k, b in cases:
        verts, adj = S.gnkb_adjacency(n, k, b)
        exact = A.exact_bandwidth_layered(adj, node_budget=C.BATCH_NODE_BUDGET) if verts else None
        formula = A.bandwidth_satz1a(n, k, b)
        rows.append({"n": n, "k": k, "b": b, "n_vertices": len(verts), "exact": exact, "formula": formula, "match": exact == formula if exact is not None else None})
    return rows


# --- Satz 1b: gemessenes B(n,k,b) gegen k*C(b,k) ueber wachsendes n -------------------------------------------------------------------------------------------


def satz1b_sweep(k=C.SATZ1B_K, bs=C.SATZ1B_BS, ns=C.SATZ1B_NS):
    """Fuer festes k, mehrere b: B(n,k,b) (approximiert ueber Cuthill-McKee/Reverse-Cuthill-McKee, exakt wo machbar) ueber wachsendes n gegen die asymptotische Formel k*C(b,k) (Satz 1b, b=o(n)) -
    EIGENER NACHBAU, numerisch nachvollzogen, KEIN Gueltigkeitstest (die Formel gilt nur im Grenzwert n->unendlich)."""
    rows = []
    for b in bs:
        asymptotic = A.bandwidth_satz1b_asymptotic(0, k, b)
        for n in ns:
            if n < b:
                continue
            verts, adj = S.gnkb_adjacency(n, k, b)
            if not verts:
                continue
            cm = A.cuthill_mckee(adj)
            rcm = A.reverse_cuthill_mckee(adj)
            measured = min(A.bandwidth(adj, cm), A.bandwidth(adj, rcm))
            exact = A.exact_bandwidth_layered(adj, upper_bound=measured, node_budget=C.BATCH_NODE_BUDGET)
            best = exact if exact is not None else measured
            rows.append({"k": k, "b": b, "n": n, "n_vertices": len(verts), "measured": best, "asymptotic": asymptotic, "ratio": best / asymptotic if asymptotic else None})
    return rows


# --- Satz 2: Heuristik-Obergrenzen gegen die c1/c2/c3-Schranken (NUR Exploration, offene Vermutung) ------------------------------------------------------------


def satz2_exploration(k=C.SATZ2_K, betas=C.SATZ2_BETAS, ns=C.SATZ2_NS):
    """Fuer b~beta*n (beta fest, n wachsend): Heuristik-Obergrenze (Cuthill-McKee/Reverse-Cuthill-McKee) auf G(n,k,b) gegen die c1/c2/c3-Schranken aus Satz 2 (b~beta*n, offene Vermutung). NUR
    EXPLORATION mit endlichem n - entscheidet die Vermutung NICHT, unabhaengig davon, wie nah/fern die Werte liegen."""
    rows = []
    for beta in betas:
        c1 = A.satz2_c1(beta, k)
        c2 = A.satz2_c2(beta, k)
        c3 = A.satz2_c3(beta, k)
        for n in ns:
            b = max(0, min(n, round(beta * n)))
            verts, adj = S.gnkb_adjacency(n, k, b)
            if not verts:
                continue
            cm = A.cuthill_mckee(adj)
            rcm = A.reverse_cuthill_mckee(adj)
            measured = min(A.bandwidth(adj, cm), A.bandwidth(adj, rcm))
            scaled = measured / (n ** k) if n > 0 else None
            rows.append({"k": k, "beta": beta, "n": n, "b": b, "n_vertices": len(verts), "measured": measured, "measured_scaled": scaled,
                         "c1": c1, "c2": c2, "c3": c3, "lower_ref": max(c1, c2 + c3 / A._qr(beta)[0] ** (k - 1)), "upper_ref": c2 + c3})
    return rows


# --- Proposition 1: chi_e Brute-Force gegen chi_v(G~_H) (Korrektheits-Kette Punkt 1) -----------------------------------------------------------------------


def reduction_check(trials=C.REDUCTION_CHECK_TRIALS, k_universe=C.REDUCTION_CHECK_K_UNIVERSE, m_max=C.REDUCTION_CHECK_M_MAX, seed=C.DEFAULT_SEED):
    """chi_e(H) (Brute-Force, direkt aus der Definition) gegen chi_v(G~_H) (`clique_cover_number` auf `weak_edge_clique_graph`) auf `trials` zufaelligen kleinen k-uniformen Hypergraphen -
    Proposition 1 des Papers, EIGENER NACHBAU, numerisch nachvollzogen (kein neuer Beweis)."""
    rng = random.Random(int(seed) * 1_000_003 + 9001)
    rows = []
    for _ in range(trials):
        k, universe = rng.choice(k_universe)
        m = rng.randint(0, m_max)
        inst_seed = rng.randrange(10_000_000)
        universe_u, edges = S.random_k_uniform_hypergraph(universe, k, m, inst_seed)
        weg = A.weak_edge_clique_graph(universe_u, edges)
        chi_e_p1, _ = A.clique_cover_number(weg) if edges else (0, 0)
        chi_e_bf = A.weak_edge_clique_cover_bruteforce(universe_u, edges)
        rows.append({"k": k, "universe": universe_u, "m": len(edges), "chi_e_bruteforce": chi_e_bf, "chi_e_proposition1": chi_e_p1, "match": chi_e_bf == chi_e_p1})
    return rows


# --- Cliquenueberdeckungs-Qualitaet: exakt/Greedy/banded-DP auf groesseren Hypergraphen/Elektrodengitter -----------------------------------------------------


def cover_quality(hyper_settings=C.COVER_QUALITY_HYPER_SETTINGS):
    """`hyper_settings`: Liste von (universe, k, m, seed). Exakt (`clique_cover_number`) gegen Greedy (natuerliche Reihenfolge) gegen die bandbreitenbeschraenkte DP - ehrlich gemessen, in
    beide Richtungen (s. README "Befunde": die DP gewinnt auf manchen Instanzen, verliert auf anderen)."""
    rows = []
    for universe, k, m, seed in hyper_settings:
        universe_u, edges = S.random_k_uniform_hypergraph(universe, k, m, seed)
        a = _cover_from_hyperedges(universe_u, edges)
        rows.append({"universe": universe_u, "k": k, "m": len(edges), "seed": seed, "exact": a.chi_e_proposition1, "greedy": a.chi_e_greedy, "banded_dp": a.chi_e_banded_dp,
                     "bandwidth_of_order": a.bandwidth_of_cm_complement, "steps_greedy": a.steps_greedy, "steps_banded_dp": a.steps_banded_dp})
    return rows
