"""Vormessung (2026-09-27): kalibriert die Konstanten in `cb_constants.py`.

1) Sucht (n,k,b)-Tripel mit b >= (n+k-1)/2 (Satz 1a anwendbar) und bestaetigt sie gegen `exact_bandwidth_layered` (node_budget begrenzt die Suche pro Tripel - ein UEBERRASCHENDER Befund: die
   Schwierigkeit haengt NICHT einfach von |V(G(n,k,b))| ab, sondern davon, wie NAH b am Schwellenwert liegt, s. `cb_constants.EXACT_LAYERED_LIMIT`). Die 28 Tripel in
   `cb_constants.SATZ1A_CASES` sind eine Teilmenge der hier bestaetigten Faelle.
2) Sucht Hypergraph-Einstellungen (universe,k,m,seed), auf denen sich Greedy/Exakt/bandbreitenbeschraenkte DP sichtbar unterscheiden, fuer `cb_constants.COVER_QUALITY_HYPER_SETTINGS`.
3) Misst die Rechenzeit von `weak_edge_clique_cover_bruteforce` ueber die Hyperkantenzahl m (Bell-Zahl-Wachstum) fuer `cb_constants.BRUTEFORCE_COVER_LIMIT`.

Nicht Teil der automatisierten Tests (Laufzeit mehrere Minuten) - Ergebnis bereits in `cb_constants.py` eingetragen, hier zur Nachvollziehbarkeit."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cb_algorithm as A                                                                                                          # noqa: E402
import cb_scenario as S                                                                                                           # noqa: E402


def search_satz1a_cases(n_max=15, node_budget=400_000, time_budget_s=100):
    t_start = time.time()
    triples = [(n, k, b) for n in range(2, n_max + 1) for k in range(1, 4) for b in range(0, n + 1) if k <= n + 1 and 2 * b >= n + k - 1]
    print(f"Kandidaten-Tripel: {len(triples)}")
    good, too_slow, bad = [], [], []
    for n, k, b in triples:
        if time.time() - t_start > time_budget_s:
            print("Zeitbudget erreicht, Suche vorzeitig beendet")
            break
        verts, adj = S.gnkb_adjacency(n, k, b)
        if not verts:
            continue
        t0 = time.time()
        exact = A.exact_bandwidth_layered(adj, node_budget=node_budget)
        dt = time.time() - t0
        formula = A.bandwidth_satz1a(n, k, b)
        if exact is None:
            too_slow.append((n, k, b, len(verts)))
        elif exact == formula:
            good.append((n, k, b, len(verts), dt))
        else:
            bad.append((n, k, b, len(verts), exact, formula))
    print(f"bestaetigt: {len(good)}, zu langsam (uebersprungen): {len(too_slow)}, ABWEICHUNGEN: {len(bad)}")
    for x in bad:
        print("MISMATCH", x)
    return good, too_slow, bad


def search_cover_quality_gaps(settings_grid, seeds=range(6)):
    found = []
    for universe, k, m in settings_grid:
        for seed in seeds:
            universe_u, edges = S.random_k_uniform_hypergraph(universe, k, m, seed)
            if len(edges) < 3:
                continue
            weg = A.weak_edge_clique_graph(universe_u, edges)
            exact, _ = A.clique_cover_number(weg, exact_limit=20)
            comp = A.complement(weg)
            greedy_k = A.greedy_color(comp, list(range(len(edges)))).k
            cm_order = A.cuthill_mckee_order(comp)
            bw = A.bandwidth(comp, A.cuthill_mckee(comp))
            dp_k = A.banded_coloring_dp(comp, cm_order, bw).k
            if exact != greedy_k or exact != dp_k or greedy_k != dp_k:
                found.append((universe, k, len(edges), seed, exact, greedy_k, dp_k))
    return found


def measure_bruteforce_cover_limit(universe=10, k=2, seed=3, m_values=range(6, 12)):
    for m in m_values:
        universe_u, edges = S.random_k_uniform_hypergraph(universe, k, m, seed)
        t0 = time.time()
        A.weak_edge_clique_cover_bruteforce(universe_u, edges)
        print(f"m={len(edges)}: {time.time() - t0:.3f}s")


if __name__ == "__main__":
    print("=== Satz 1a: gueltige Tripel suchen und bestaetigen ===")
    search_satz1a_cases()
    print("\n=== Cliquenueberdeckung: Faelle mit sichtbarem Greedy/DP/Exakt-Unterschied ===")
    for row in search_cover_quality_gaps([(8, 2, 15), (9, 2, 20), (10, 2, 18), (10, 3, 20)]):
        print(row)
    print("\n=== weak_edge_clique_cover_bruteforce: Rechenzeit ueber m ===")
    measure_bruteforce_cover_limit()
