"""Die zentrale Korrektheits-Kette des Plans, gebuendelt: Proposition 1 (Punkt 1), Satz 1a exakt (Punkt 3), exact_bandwidth_layered gegen exact_bandwidth_bruteforce (Punkt 4)."""

import random

import cb_algorithm as A
import cb_constants as C
import cb_evaluation as ev
import cb_scenario as S


# --- Punkt 1: Proposition 1 - chi_e(H) (Brute-Force ueber die Definition) == chi_v(G~_H) (Proposition-1-Weg) -----------------------------------------------


def test_proposition1_on_at_least_100_random_hypergraphs():
    rows = ev.reduction_check(trials=150)
    assert len(rows) == 150
    mismatches = [r for r in rows if not r["match"]]
    assert mismatches == []


def test_proposition1_on_the_electrode_textbook_example():
    universe, edges, positions = S.electrode_hypergraph(4, 3, 6, seed=35)
    weg = A.weak_edge_clique_graph(universe, edges)
    chi_e_p1, _ = A.clique_cover_number(weg)
    chi_e_bf = A.weak_edge_clique_cover_bruteforce(universe, edges)
    assert chi_e_p1 == chi_e_bf


def test_proposition1_holds_for_k_equals_1_hyperedges_too():
    """k=1: jede Hyperkante ist ein Singleton; zwei Singletons {a},{b} sind nur dann zu einer schwachen Clique vereinbar, wenn eine (groessere) Hyperkante beide enthaelt - bei rein
    einelementigen Hyperkanten also NIE, chi_e sollte also gleich der Hyperkantenzahl sein."""
    universe, edges = S.random_k_uniform_hypergraph(8, 1, 5, seed=3)
    weg = A.weak_edge_clique_graph(universe, edges)
    chi_e_p1, _ = A.clique_cover_number(weg)
    chi_e_bf = A.weak_edge_clique_cover_bruteforce(universe, edges)
    assert chi_e_p1 == chi_e_bf == len(edges)


# --- Punkt 2: two_section_graph/is_weak_clique/weak_edge_clique_graph gegen unabhaengige Neuberechnung (s. tests/test_algorithm.py) - hier zusaetzlich auf realen Hypergraphen ------------------


def test_every_claimed_edge_of_weg_is_independently_verified_as_a_weak_clique():
    rng = random.Random(4242)
    for _ in range(40):
        k = rng.choice([2, 3])
        universe = rng.randint(k, 9)
        m = rng.randint(2, 6)
        seed = rng.randrange(1_000_000)
        universe_u, edges = S.random_k_uniform_hypergraph(universe, k, m, seed)
        ts = A.two_section_graph(universe_u, edges)
        weg = A.weak_edge_clique_graph(universe_u, edges)
        for i in range(len(edges)):
            for j in weg[i]:
                union = sorted(set(edges[i]) | set(edges[j]))
                assert A.is_weak_clique(ts, union) is True


# --- Punkt 3: Satz 1a EXAKT auf >=19 (n,k,b)-Tripeln ------------------------------------------------------------------------------------------------------


def test_satz1a_holds_exactly_on_all_confirmed_cases():
    assert len(C.SATZ1A_CASES) >= 19
    rows = ev.satz1a_check()
    assert len(rows) == len(C.SATZ1A_CASES)
    for r in rows:
        assert r["exact"] is not None, f"Fall {(r['n'], r['k'], r['b'])} hat das Rechenbudget ueberschritten - sollte nicht in SATZ1A_CASES stehen"
        assert r["exact"] == r["formula"], f"Abweichung bei {(r['n'], r['k'], r['b'])}: exakt {r['exact']} != Formel {r['formula']}"


def test_bandwidth_satz1a_rejects_b_below_the_threshold():
    import pytest
    with pytest.raises(ValueError):
        A.bandwidth_satz1a(10, 3, 1)                    # b=1 << (10+3-1)/2=6


def test_bandwidth_satz1b_asymptotic_is_k_times_choose_b_k():
    import math
    assert A.bandwidth_satz1b_asymptotic(999, 2, 5) == 2 * math.comb(5, 2)
    assert A.bandwidth_satz1b_asymptotic(999, 3, 6) == 3 * math.comb(6, 3)


# --- Punkt 4: exact_bandwidth_layered == exact_bandwidth_bruteforce auf allen gemeinsam machbaren kleinen Graphen (n<=9) ------------------------------------


def test_exact_bandwidth_layered_matches_bruteforce_on_small_graphs():
    rng = random.Random(777)
    for trial in range(80):
        n = rng.randint(1, 9)
        p = rng.uniform(0.1, 0.9)
        adj = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p:
                    adj[i].append(j)
                    adj[j].append(i)
        bf = A.exact_bandwidth_bruteforce(adj)
        layered = A.exact_bandwidth_layered(adj)
        assert layered == bf, f"n={n} adj={adj} bruteforce={bf} layered={layered}"


def test_exact_bandwidth_layered_matches_bruteforce_on_gnkb_small_instances():
    for n, k, b in [(3, 1, 1), (4, 2, 2), (4, 2, 3), (5, 2, 2), (3, 3, 2), (5, 1, 1)]:
        verts, adj = S.gnkb_adjacency(n, k, b)
        if len(verts) > 9:
            continue
        assert A.exact_bandwidth_layered(adj) == A.exact_bandwidth_bruteforce(adj)


def test_exact_bandwidth_layered_on_complete_graphs_is_n_minus_1():
    for n in [1, 2, 5, 8, 10, 13]:
        adj = [[j for j in range(n) if j != i] for i in range(n)]
        assert A.exact_bandwidth_layered(adj) == max(0, n - 1)


def test_exact_bandwidth_layered_node_budget_returns_none_gracefully_instead_of_hanging():
    verts, adj = S.gnkb_adjacency(6, 2, 4)                # ein in der Vormessung als "zu langsam" identifizierter Fall
    result = A.exact_bandwidth_layered(adj, node_budget=1000)
    assert result is None
