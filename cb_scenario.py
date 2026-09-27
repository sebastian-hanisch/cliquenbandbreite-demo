"""G(n,k,b) nach Engel und Hanisch (arXiv:1605.00450): Ecken sind die k-elementigen Teilmengen X von {0,...,n} mit max(X)-min(X) <= b; X,Y benachbart, wenn max(X u Y)-min(X u Y) <= b.
Zufaellige k-uniforme Hypergraphen (allgemeines Testfeld fuer die Cliquenueberdeckung, unabhaengig von der G(n,k,b)-Struktur) und ein Elektrodengitter-Beispiel (NEU, klein, synthetisch - NICHT
die komplexe Spike-Simulation aus `delay-graph-demo`, nur dessen `electrode_positions(grid)` wortgleich wiederverwendet). Lehrbuchbeispiel (4,2,3) von Hand.

**Elementarschritte** (das Aufwandsmass dieser Reihe, keine Laufzeit): wie in den Geschwister-Demos zaehlt jede angesehene Kante/jedes angesehene Paar 1."""

import itertools
import math
import random

import numpy as np


def electrode_positions(grid):
    """Zentren (0.5 + j_x, 0.5 + j_y), Elektrode j = grid * j_y + j_x (Zeile fuer Zeile) - wortgleiche Kopie aus `delay-graph-demo/dg_scenario.py` (NICHT die Spike-Simulation, nur diese eine,
    rein geometrische Funktion)."""
    jj = np.arange(grid * grid)
    return np.column_stack([0.5 + jj % grid, 0.5 + jj // grid])


# --- G(n,k,b) --------------------------------------------------------------------------------------------------------------------------------------------


def gnkb_vertices(n, k, b):
    """Sortierte Liste der k-elementigen Teilmengen X von {0,...,n} mit max(X)-min(X) <= b (jede Teilmenge als aufsteigend sortiertes Tupel; `itertools.combinations` liefert bereits
    lexikographisch sortierte Tupel, die Liste selbst ist also ebenfalls sortiert)."""
    n, k, b = int(n), int(k), int(b)
    if k < 0:
        raise ValueError("k darf nicht negativ sein")
    if k == 0:
        return [()] if b >= 0 else []
    if n + 1 < k:
        return []                                       # Sonderfall n<k: leere Eckenmenge
    return [X for X in itertools.combinations(range(n + 1), k) if X[-1] - X[0] <= b]


def gnkb_adjacency(n, k, b):
    """Nachbarschaftsliste ueber den Spannen-Test (direkt aus der Definition, keine Abkuerzung): X,Y benachbart, wenn max(X u Y)-min(X u Y) <= b. Gibt (verts, adj) zurueck."""
    verts = gnkb_vertices(n, k, b)
    m = len(verts)
    adj = [[] for _ in range(m)]
    for i in range(m):
        xi_min, xi_max = verts[i][0], verts[i][-1]
        for j in range(i + 1, m):
            xj_min, xj_max = verts[j][0], verts[j][-1]
            span_min = min(xi_min, xj_min)
            span_max = max(xi_max, xj_max)
            if span_max - span_min <= b:
                adj[i].append(j)
                adj[j].append(i)
    return verts, adj


def textbook_gnkb(n=4, k=2, b=3):
    """Die kleinste nichttriviale Instanz von Hand: (n,k,b)=(4,2,3) - Ecken/Kanten von Hand aufzaehlbar, s. README."""
    verts, adj = gnkb_adjacency(n, k, b)
    return n, k, b, verts, adj


# --- Zufaellige k-uniforme Hypergraphen --------------------------------------------------------------------------------------------------------------------


def random_k_uniform_hypergraph(universe, k, m, seed):
    """`m` verschiedene k-elementige Hyperkanten (sortierte Tupel) aus der Grundmenge {0,...,universe-1}, Duplikate vermieden (`random.Random`-Strom, Hauskonvention). Liefert (universe, edges)
    mit `edges` als sortiertes Tupel von sortierten Tupeln."""
    universe, k, m = int(universe), int(k), int(m)
    if k < 0 or universe < 0:
        raise ValueError("universe und k duerfen nicht negativ sein")
    max_m = math.comb(universe, k) if universe >= k else 0
    m = min(m, max_m)
    rng = random.Random(int(seed) * 1_000_003 + 7001)
    chosen = set()
    attempts = 0
    max_attempts = m * 50 + 200
    while len(chosen) < m and attempts < max_attempts:
        attempts += 1
        e = tuple(sorted(rng.sample(range(universe), k)))
        chosen.add(e)
    edges = tuple(sorted(chosen))
    return universe, edges


# --- Elektrodengitter-Beispiel (NEU) -----------------------------------------------------------------------------------------------------------------------


def electrode_hypergraph(grid, k, m, seed):
    """`grid x grid`-Elektrodenraster (`electrode_positions`, wortgleich kopiert); je `m` synthetische "Zellen" mit einem zufaelligen Zentrum irgendwo im Raster, deren Hyperkante die `k`
    naechstgelegenen Elektroden (euklidischer Abstand) sind - eine kleine, anschauliche, aber rein synthetische Illustration des Papers Motivationsbeispiels (Neuron -> Kontaktmenge), KEINE
    Rekonstruktion der komplexen Spike-Simulation aus `delay-graph-demo`. Liefert (universe, edges) wie `random_k_uniform_hypergraph`."""
    grid, k, m = int(grid), int(k), int(m)
    universe = grid * grid
    if k < 0 or k > universe:
        raise ValueError(f"k muss zwischen 0 und {universe} liegen")
    positions = electrode_positions(grid)
    rng = random.Random(int(seed) * 1_000_003 + 7331)
    chosen = set()
    edges = []
    attempts = 0
    max_attempts = m * 80 + 200
    while len(edges) < m and attempts < max_attempts:
        attempts += 1
        cx = rng.uniform(0.0, float(grid))
        cy = rng.uniform(0.0, float(grid))
        ranked = sorted(range(universe), key=lambda j: (positions[j][0] - cx) ** 2 + (positions[j][1] - cy) ** 2)
        e = tuple(sorted(ranked[:k]))
        if e not in chosen:
            chosen.add(e)
            edges.append(e)
    edges.sort()
    return universe, tuple(edges), positions
