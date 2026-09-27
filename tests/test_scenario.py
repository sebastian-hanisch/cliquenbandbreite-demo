"""G(n,k,b)-Konstruktion (Korrektheits-Kette Punkt 5, 10), Hypergraph-Generatoren (Punkt 9)."""

import itertools

import cb_scenario as S


def _independent_gnkb_adjacency(n, k, b):
    """Unabhaengige Neuberechnung direkt aus der Definition (KEINE Wiederverwendung von `cb_scenario.gnkb_adjacency`), fuer den Regressionstest."""
    verts = [X for X in itertools.combinations(range(n + 1), k) if max(X) - min(X) <= b]
    idx = {v: i for i, v in enumerate(verts)}
    adj = [[] for _ in verts]
    for X in verts:
        for Y in verts:
            if X == Y:
                continue
            u = set(X) | set(Y)
            if max(u) - min(u) <= b:
                adj[idx[X]].append(idx[Y])
    return verts, adj


def test_gnkb_vertices_matches_definition_directly():
    for n, k, b in [(4, 2, 3), (6, 3, 4), (5, 1, 2), (8, 2, 5)]:
        verts = S.gnkb_vertices(n, k, b)
        expected = [X for X in itertools.combinations(range(n + 1), k) if X[-1] - X[0] <= b]
        assert verts == expected


def test_gnkb_adjacency_matches_independent_recomputation():
    for n, k, b in [(3, 2, 2), (4, 2, 3), (5, 2, 4), (5, 3, 3), (6, 1, 2), (6, 3, 5), (7, 2, 2)]:
        verts, adj = S.gnkb_adjacency(n, k, b)
        ind_verts, ind_adj = _independent_gnkb_adjacency(n, k, b)
        assert verts == ind_verts
        assert [sorted(a) for a in adj] == [sorted(a) for a in ind_adj]


def test_gnkb_special_case_b_at_least_n_is_complete_graph():
    """Sonderfall (Korrektheits-Kette Punkt 10): b >= n macht JEDES Paar benachbart (die maximale Spannweite in {0,...,n} ist n)."""
    n, k = 6, 2
    verts, adj = S.gnkb_adjacency(n, k, n)
    m = len(verts)
    assert m == __import__("math").comb(n + 1, k)
    assert all(len(a) == m - 1 for a in adj)


def test_gnkb_special_case_k_equals_1_is_a_distance_band_graph():
    """Sonderfall k=1: G(n,1,b) - Ecken sind Einzelelemente 0..n, X,Y benachbart genau dann, wenn |X-Y| <= b (direkt nachrechenbar)."""
    n, b = 8, 3
    verts, adj = S.gnkb_adjacency(n, 1, b)
    assert verts == [(i,) for i in range(n + 1)]
    for i in range(n + 1):
        expected_neighbors = sorted(j for j in range(n + 1) if j != i and abs(i - j) <= b)
        assert sorted(adj[i]) == expected_neighbors


def test_gnkb_special_case_n_less_than_k_is_empty():
    verts, adj = S.gnkb_adjacency(2, 5, 3)
    assert verts == []
    assert adj == []


def test_gnkb_k_zero_is_a_single_empty_tuple_vertex():
    verts = S.gnkb_vertices(4, 0, 0)
    assert verts == [()]


def test_random_k_uniform_hypergraph_is_deterministic_and_valid():
    for trial in range(20):
        universe, edges = S.random_k_uniform_hypergraph(8, 2, 5, seed=trial)
        universe2, edges2 = S.random_k_uniform_hypergraph(8, 2, 5, seed=trial)
        assert edges == edges2                                  # Determinismus
        assert len(set(edges)) == len(edges)                     # keine Duplikate
        assert all(len(e) == 2 for e in edges)                   # k-uniform
        assert all(e == tuple(sorted(e)) for e in edges)         # sortierte Tupel
        assert all(0 <= v < universe for e in edges for v in e)


def test_random_k_uniform_hypergraph_caps_m_at_the_maximum_possible():
    universe, edges = S.random_k_uniform_hypergraph(4, 2, 100, seed=1)
    assert len(edges) == 6                                       # C(4,2) = 6, mehr verschiedene 2-Teilmengen gibt es nicht


def test_electrode_positions_matches_delay_graph_demo_formula():
    grid = 4
    pos = S.electrode_positions(grid)
    assert pos.shape == (16, 2)
    assert list(pos[0]) == [0.5, 0.5]
    assert list(pos[5]) == [1.5, 1.5]                            # Elektrode 5 = grid*1+1 -> j_x=1,j_y=1


def test_electrode_hypergraph_is_deterministic_and_k_uniform():
    for trial in range(10):
        universe, edges, positions = S.electrode_hypergraph(4, 3, 6, seed=trial)
        universe2, edges2, positions2 = S.electrode_hypergraph(4, 3, 6, seed=trial)
        assert edges == edges2
        assert universe == 16
        assert len(set(edges)) == len(edges)
        assert all(len(e) == 3 for e in edges)
        assert all(e == tuple(sorted(e)) for e in edges)


def test_textbook_gnkb_is_4_2_3():
    n, k, b, verts, adj = S.textbook_gnkb()
    assert (n, k, b) == (4, 2, 3)
    assert verts == S.gnkb_vertices(4, 2, 3)
