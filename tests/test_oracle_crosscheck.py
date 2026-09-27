"""Gegenprobe gegen unabhaengige Bibliotheken (networkx, scipy) - NUR als Test-Suite-Orakel, s. requirements-dev.txt; die App selbst importiert weder networkx noch scipy."""

import random

import networkx as nx
import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import reverse_cuthill_mckee as scipy_rcm

import cb_algorithm as A


def _random_adj_and_graph(n, p, seed):
    rng = random.Random(seed)
    adj = [[] for _ in range(n)]
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i].append(j)
                adj[j].append(i)
                g.add_edge(i, j)
    return adj, g


def test_clique_number_matches_networkx_on_random_graphs():
    for trial in range(30):
        n = random.Random(trial).randint(1, 12)
        p = random.Random(trial + 1).uniform(0.1, 0.8)
        adj, g = _random_adj_and_graph(n, p, trial)
        ours, _ = A.clique_number(adj)
        expected = max((len(c) for c in nx.find_cliques(g)), default=0)
        assert ours == expected


def _to_scipy_bandwidth(adj):
    n = len(adj)
    if n == 0:
        return 0
    rows, cols = [], []
    for u in range(n):
        for v in adj[u]:
            rows.append(u)
            cols.append(v)
    mat = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    perm = scipy_rcm(mat, symmetric_mode=True)
    inv = np.empty(n, dtype=int)
    inv[perm] = np.arange(n)
    return A.bandwidth(adj, list(inv))


def test_cuthill_mckee_bandwidth_is_never_worse_than_a_generous_multiple_of_scipys_rcm_bandwidth():
    """Beide sind Cuthill-McKee-Varianten auf demselben Graphen - sie muessen nicht bitidentisch sein (Tiebreak-Regeln unterscheiden sich), aber in derselben Groessenordnung liegen. Als
    harte, plattformunabhaengige Gegenprobe: unsere Bandbreite darf niemals kleiner sein als scipy's (das waere ein Fehler in unserer Bandbreiten-BERECHNUNG selbst, nicht nur eine andere
    Heuristik-Wahl), und nicht mehr als das Doppelte plus 2 groesser."""
    for trial in range(20):
        n = random.Random(trial).randint(3, 20)
        p = random.Random(trial + 2).uniform(0.1, 0.5)
        adj, _g = _random_adj_and_graph(n, p, trial)
        if not any(adj):
            continue
        ours = A.bandwidth(adj, A.cuthill_mckee(adj))
        scipy_bw = _to_scipy_bandwidth(adj)
        assert ours <= 2 * scipy_bw + 2


def test_exact_bandwidth_layered_never_exceeds_scipy_rcm_bandwidth():
    """Die exakte Suche muss (per Definition des Optimums) hoechstens so groß sein wie JEDE gueltige Heuristik-Bandbreite, auch scipy's eigene."""
    for trial in range(20):
        n = random.Random(trial).randint(1, 12)
        p = random.Random(trial + 3).uniform(0.15, 0.6)
        adj, _g = _random_adj_and_graph(n, p, trial)
        exact = A.exact_bandwidth_layered(adj)
        scipy_bw = _to_scipy_bandwidth(adj)
        assert exact <= scipy_bw
