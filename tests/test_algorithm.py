"""Bandbreite/Profil/Cuthill-McKee (Regression gegen Stueck 11s Semantik, Korrektheits-Kette Punkt 8), Faerbung/Cliquenzahl/Cliquenueberdeckung (Punkt 6), 2-Sektionsgraph/schwache Clique
(Punkt 2), bandbreitenbeschraenkte DP (Punkt 7)."""

import itertools
import random

import cb_algorithm as A


def _random_adj(n, p, seed):
    rng = random.Random(seed)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i].append(j)
                adj[j].append(i)
    return adj


# --- Bandbreite/Profil/CM/RCM (Punkt 8: dieselbe Semantik wie Stueck 11) --------------------------------------------------------------------------------


def test_bandwidth_matches_independent_definition():
    for trial in range(60):
        n = random.Random(trial).randint(1, 10)
        adj = _random_adj(n, 0.4, trial + 500)
        perm = A.random_permutation(n, trial)
        edges = [(u, v) for u in range(n) for v in adj[u] if u < v]
        expected = max((abs(perm[u] - perm[v]) for u, v in edges), default=0)
        assert A.bandwidth(adj, perm) == expected


def test_profile_matches_independent_definition():
    for trial in range(60):
        n = random.Random(trial + 1).randint(1, 10)
        adj = _random_adj(n, 0.4, trial + 700)
        perm = A.random_permutation(n, trial)
        total = 0
        for v in range(n):
            candidates = [perm[u] for u in adj[v] if perm[u] <= perm[v]]
            if candidates:
                total += perm[v] - min(candidates)
        assert A.profile(adj, perm) == total


def test_cm_and_rcm_are_valid_permutations_even_with_multiple_components():
    for trial in range(30):
        n = random.Random(trial).randint(2, 15)
        adj = _random_adj(n, 0.15, trial + 900)
        cm = A.cuthill_mckee(adj)
        rcm = A.reverse_cuthill_mckee(adj)
        assert sorted(cm) == list(range(n))
        assert sorted(rcm) == list(range(n))


def test_bandwidth_cm_equals_bandwidth_rcm_always():
    """Mathematischer Fakt (kein Messwert): Bandbreite(RCM) = Bandbreite(CM), da |п(u)-п(v)| = |(n-1-п(u))-(n-1-п(v))|."""
    for trial in range(60):
        n = random.Random(trial).randint(1, 15)
        adj = _random_adj(n, random.Random(trial + 1).uniform(0.05, 0.6), trial)
        cm = A.cuthill_mckee(adj)
        rcm = A.reverse_cuthill_mckee(adj)
        assert A.bandwidth(adj, cm) == A.bandwidth(adj, rcm)


def test_exact_bandwidth_bruteforce_matches_independent_permutation_search():
    for trial in range(25):
        n = random.Random(trial).randint(1, 7)
        adj = _random_adj(n, 0.4, trial + 11)
        edges = [(u, v) for u in range(n) for v in adj[u] if u < v]
        if not edges:
            assert A.exact_bandwidth_bruteforce(adj) == 0
            continue
        best = min(max(abs(perm[u] - perm[v]) for u, v in edges) for perm in itertools.permutations(range(n)))
        assert A.exact_bandwidth_bruteforce(adj) == best


# --- 2-Sektionsgraph/schwache Clique (Korrektheits-Kette Punkt 2) ---------------------------------------------------------------------------------------


def test_two_section_graph_matches_independent_definition():
    hyperedges = [(0, 1, 2), (2, 3), (4, 5, 0)]
    universe = 6
    ts = A.two_section_graph(universe, hyperedges)
    expected = [set() for _ in range(universe)]
    for e in hyperedges:
        for i in range(len(e)):
            for j in range(len(e)):
                if i != j:
                    expected[e[i]].add(e[j])
    assert [set(a) for a in ts] == expected


def test_is_weak_clique_matches_is_clique_semantics():
    ts = [[1, 2], [0, 2], [0, 1], []]
    assert A.is_weak_clique(ts, [0, 1, 2]) is True
    assert A.is_weak_clique(ts, [0, 1, 3]) is False
    assert A.is_weak_clique(ts, []) is True
    assert A.is_weak_clique(ts, [0]) is True


def test_weak_edge_clique_graph_matches_independent_recomputation():
    universe = 6
    hyperedges = [(0, 1), (1, 2), (0, 1, 2), (3, 4), (5,)]
    weg = A.weak_edge_clique_graph(universe, hyperedges)
    ts = A.two_section_graph(universe, hyperedges)
    m = len(hyperedges)
    expected = [[] for _ in range(m)]
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            union = sorted(set(hyperedges[i]) | set(hyperedges[j]))
            adjset = [set(a) for a in ts]
            is_clique = all(v in adjset[u] for x, u in enumerate(union) for v in union[x + 1:])
            if is_clique:
                expected[i].append(j)
    assert [sorted(a) for a in weg] == [sorted(a) for a in expected]


def test_single_hyperedge_is_always_its_own_weak_clique():
    """Ein einzelnes Hyperkanten-Element bildet per Konstruktion immer eine Clique im 2-Sektionsgraphen - wichtig fuer die Terminierung von weak_edge_clique_cover_bruteforce."""
    ts = A.two_section_graph(5, [(0, 1, 2, 3)])
    assert A.is_weak_clique(ts, [0, 1, 2, 3]) is True


# --- Faerbung/Cliquenzahl/Cliquenueberdeckung (Korrektheits-Kette Punkt 6) ------------------------------------------------------------------------------


def test_clique_cover_number_is_chromatic_number_of_complement():
    for trial in range(20):
        n = random.Random(trial).randint(1, 9)
        adj = _random_adj(n, 0.4, trial + 300)
        expected, _ = A.chromatic_number(A.complement(adj))
        got, _ = A.clique_cover_number(adj)
        assert got == expected


def test_greedy_color_is_a_proper_coloring():
    for trial in range(30):
        n = random.Random(trial).randint(1, 12)
        adj = _random_adj(n, 0.3, trial + 400)
        order = list(range(n))
        random.Random(trial).shuffle(order)
        result = A.greedy_color(adj, order)
        for u in range(n):
            for v in adj[u]:
                assert result.colors[u] != result.colors[v]


def test_chromatic_number_never_exceeds_greedy_and_is_at_least_clique_number():
    for trial in range(20):
        n = random.Random(trial).randint(1, 9)
        adj = _random_adj(n, 0.4, trial + 600)
        chi, _ = A.chromatic_number(adj)
        omega, _ = A.clique_number(adj)
        greedy_k = A.greedy_color(adj, list(range(n))).k
        assert omega <= chi <= greedy_k


def test_color_classes_are_cliques_in_the_complement_of_the_colored_graph():
    """Jede Farbklasse einer gueltigen Faerbung von complement(adj) ist eine Clique in `adj` (Grundlage der Cliquenueberdeckung ueber Faerbung)."""
    for trial in range(15):
        n = random.Random(trial).randint(2, 8)
        adj = _random_adj(n, 0.5, trial + 200)
        comp = A.complement(adj)
        # eine tatsaechliche Faerbung ueber Greedy in einer guten Reihenfolge nachbauen (nur fuer den Cliquentest, chi(comp) selbst wird hier nicht gebraucht)
        order = sorted(range(n), key=lambda v: -len(comp[v]))
        greedy_result = A.greedy_color(comp, order)
        for cls in A.color_classes(greedy_result.colors):
            assert A.is_clique(adj, cls)


def test_is_clique_matches_definition():
    adj = [[1, 2], [0, 2], [0, 1], []]
    assert A.is_clique(adj, [0, 1, 2]) is True
    assert A.is_clique(adj, [0, 1, 3]) is False
    assert A.is_clique(adj, []) is True
    assert A.is_clique(adj, [0]) is True


def test_complement_is_involution():
    for trial in range(10):
        n = random.Random(trial).randint(1, 8)
        adj = _random_adj(n, 0.4, trial + 100)
        assert [sorted(a) for a in A.complement(A.complement(adj))] == [sorted(a) for a in adj]


# --- Bandbreitenbeschraenkte DP (Korrektheits-Kette Punkt 7) --------------------------------------------------------------------------------------------


def test_banded_coloring_dp_matches_greedy_color_for_the_same_order():
    """Da der Fenster-Zustand jeden ECHTEN Nachbarn erfasst (Bandbreite der Reihenfolge <= Fenstergroesse per Voraussetzung), liefert die DP GENAU dieselbe Faerbung wie
    `greedy_color(adj, order)` fuer dieselbe Reihenfolge - keine Naeherung, ein mathematischer Fakt dieser Konstruktion."""
    for trial in range(30):
        n = random.Random(trial).randint(1, 12)
        adj = _random_adj(n, 0.35, trial + 800)
        order = list(range(n))
        random.Random(trial + 1).shuffle(order)
        perm = [0] * n
        for i, v in enumerate(order):
            perm[v] = i
        bw_of_order = A.bandwidth(adj, perm)
        dp_result = A.banded_coloring_dp(adj, order, bw_of_order)
        greedy_result = A.greedy_color(adj, order)
        assert dp_result.colors == greedy_result.colors
        assert dp_result.k == greedy_result.k


def test_banded_coloring_dp_never_uses_more_than_bandwidth_plus_one_colors():
    """Satz (kein Messwert): im Fenster koennen hoechstens `bandwidth_of_order` bereits gefaerbte echte Nachbarn liegen, es bleibt also immer eine Farbe aus {0,...,bandwidth_of_order} frei."""
    for trial in range(40):
        n = random.Random(trial).randint(1, 14)
        adj = _random_adj(n, random.Random(trial + 2).uniform(0.1, 0.7), trial + 250)
        order = list(range(n))
        random.Random(trial + 3).shuffle(order)
        perm = [0] * n
        for i, v in enumerate(order):
            perm[v] = i
        bw_of_order = A.bandwidth(adj, perm)
        dp_result = A.banded_coloring_dp(adj, order, bw_of_order)
        assert dp_result.k <= bw_of_order + 1


def test_banded_coloring_dp_is_a_proper_coloring():
    for trial in range(20):
        n = random.Random(trial).randint(1, 10)
        adj = _random_adj(n, 0.3, trial + 350)
        order = list(range(n))
        perm = list(range(n))
        bw_of_order = A.bandwidth(adj, perm)
        dp_result = A.banded_coloring_dp(adj, order, bw_of_order)
        for u in range(n):
            for v in adj[u]:
                assert dp_result.colors[u] != dp_result.colors[v]


# --- Sonderfaelle (Korrektheits-Kette Punkt 10) ----------------------------------------------------------------------------------------------------------


def test_empty_graph_special_cases():
    assert A.bandwidth([], []) == 0
    assert A.chromatic_number([])[0] == 0
    assert A.clique_cover_number([])[0] == 0
    assert A.exact_bandwidth_layered([]) == 0
    assert A.two_section_graph(0, []) == []
    assert A.weak_edge_clique_graph(3, []) == []


def test_weak_edge_clique_cover_bruteforce_empty_and_single_hyperedge():
    assert A.weak_edge_clique_cover_bruteforce(5, []) == 0
    assert A.weak_edge_clique_cover_bruteforce(5, [(0, 1, 2)]) == 1
