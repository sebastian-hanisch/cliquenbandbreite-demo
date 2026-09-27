"""Kern-Algorithmen: Bandbreite/Profil/Cuthill-McKee (wortgleiche Kopien aus `band_algorithm.py`, Stueck 11), 2-Sektionsgraph/schwache Clique/schwacher Kantenclique-Graph (nach Engel und
Hanisch, arXiv:1605.00450), Faerbung/Cliquenzahl/Cliquenueberdeckung (wortgleiche Kopien aus `gc_algorithm.py`, Stueck 5), eine neue, echte exakte Bandbreiten-Suche
(`exact_bandwidth_layered`, Branch-and-Bound mit erzwungenen Platzierungen), die geschlossene Satz-1a-Formel und die selbst entworfene bandbreitenbeschraenkte Faerbungs-DP.

**Zentrale Definitionen aus dem Paper** (woertlich, s. README "Literatur"): der **2-Sektionsgraph** G_H eines Hypergraphen H=(V,E) hat u~v genau dann, wenn eine Hyperkante beide enthaelt. Eine
**schwache Clique** ist eine Teilmenge, die in G_H eine Clique bildet. Eine **schwache Kantenclique-Ueberdeckung** ist eine Familie schwacher Cliquen, sodass jede Hyperkante Teilmenge einer der
Cliquen ist; ihre kleinste Familiengroesse ist chi_e(H). Der **schwache Kantenclique-Graph** G~_H hat als Ecken die Hyperkanten von H; e,e' sind benachbart, wenn e u e' selbst eine schwache
Clique ist. **Proposition 1**: chi_e(H) = chi_v(G~_H), wobei chi_v die EckenUEBERDECKUNGSZAHL DURCH CLIQUEN ist (= Faerbungszahl des KOMPLEMENTGRAPHEN), NICHT die Faerbungszahl von G~_H selbst.

**Jede Zahl aus den Saetzen dieses Papers ist ein eigener Nachbau, numerisch nachvollzogen - kein neuer Beweis.**"""

import itertools
import math
import random
from collections import deque
from dataclasses import dataclass


# --- Bandbreite/Profil (wortgleiche Kopien aus band_algorithm.py, Stueck 11) ------------------------------------------------------------------------------


def bandwidth(adj, perm):
    """max |perm[u]-perm[v]| ueber alle Kanten (jede Kante wird von beiden Enden aus gesehen - das aendert nur die Zahl der Vergleiche, nicht das Maximum)."""
    b = 0
    for u in range(len(adj)):
        pu = perm[u]
        for v in adj[u]:
            d = pu - perm[v]
            if d < 0:
                d = -d
            if d > b:
                b = d
    return b


def profile(adj, perm):
    """Sum_v (perm[v] - min{perm[u] : u~v, perm[u] <= perm[v]}) je Knoten (0, wenn kein solcher Nachbar existiert)."""
    total = 0
    for v in range(len(adj)):
        pv = perm[v]
        best = None
        for u in adj[v]:
            pu = perm[u]
            if pu <= pv and (best is None or pu < best):
                best = pu
        if best is not None:
            total += pv - best
    return total


def random_permutation(n, seed):
    """Eine zufaellige Permutation von 0..n-1 (Hauskonvention `random.Random(seed*1_000_003+salt)`) - nur als Vergleichsgroesse fuer die sichtbare Bandbreiten-Nummerierung."""
    rng = random.Random(int(seed) * 1_000_003 + 6421)
    perm = list(range(n))
    rng.shuffle(perm)
    return perm


def _bfs_distances(adj, s):
    n = len(adj)
    dist = [-1] * n
    dist[s] = 0
    queue = deque([s])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def pseudo_peripheral(adj, candidates=None):
    """George und Liu (1979, ACM TOMS 5(3), 284-295) - wortgleiche Kopie aus `band_algorithm.py`, Stueck 11."""
    nodes = list(candidates) if candidates is not None else list(range(len(adj)))
    if len(nodes) == 1:
        return nodes[0]
    start = min(nodes, key=lambda v: (len(adj[v]), v))
    dist = _bfs_distances(adj, start)
    ecc = max(dist[v] for v in nodes)
    current = start
    while True:
        last_level = [v for v in nodes if dist[v] == ecc]
        candidate = min(last_level, key=lambda v: (len(adj[v]), v))
        if candidate == current:
            return current
        cdist = _bfs_distances(adj, candidate)
        cecc = max(cdist[v] for v in nodes)
        if cecc <= ecc:
            return candidate
        current = candidate
        dist = cdist
        ecc = cecc


def _component_of(adj, seed_node):
    seen = {seed_node}
    order = [seed_node]
    dq = deque([seed_node])
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                order.append(v)
                dq.append(v)
    return order


def cuthill_mckee_order(adj, start=None):
    """wortgleiche Kopie aus `band_algorithm.py`, Stueck 11 (dort `cuthill_mckee_order`)."""
    n = len(adj)
    visited = [False] * n
    order = []
    first = True
    while len(order) < n:
        seed_node = next(v for v in range(n) if not visited[v])
        comp = _component_of(adj, seed_node)
        if first and start is not None:
            if start not in comp:
                raise ValueError("start liegt nicht in der ersten (kleinstindizierten) Komponente")
            s = start
        else:
            s = pseudo_peripheral(adj, comp)
        first = False
        visited[s] = True
        order.append(s)
        dq = deque([s])
        while dq:
            u = dq.popleft()
            nbrs = sorted((v for v in adj[u] if not visited[v]), key=lambda v: (len(adj[v]), v))
            for v in nbrs:
                visited[v] = True
                order.append(v)
                dq.append(v)
    return order


def cuthill_mckee(adj, start=None):
    """wortgleiche Kopie aus `band_algorithm.py`, Stueck 11."""
    order = cuthill_mckee_order(adj, start)
    n = len(order)
    perm = [0] * n
    for pos, node in enumerate(order):
        perm[node] = pos
    return perm


def reverse_cuthill_mckee(adj, start=None):
    """wortgleiche Kopie aus `band_algorithm.py`, Stueck 11."""
    cm = cuthill_mckee(adj, start)
    n = len(cm)
    return [n - 1 - p for p in cm]


def exact_bandwidth_bruteforce(adj):
    """wortgleiche Kopie aus `band_algorithm.py`, Stueck 11 - probiert ALLE n! Permutationen durch, nur fuer sehr kleine n (Referenz fuer `exact_bandwidth_layered`, Korrektheits-Kette Punkt 4)."""
    n = len(adj)
    if n <= 1:
        return 0
    edges = [(u, v) for u in range(n) for v in adj[u] if u < v]
    if not edges:
        return 0
    best = None
    for perm in itertools.permutations(range(n)):
        b = 0
        for u, v in edges:
            d = perm[u] - perm[v]
            if d < 0:
                d = -d
            if d > b:
                b = d
            if best is not None and b >= best:
                break
        if best is None or b < best:
            best = b
    return best


# --- Neue, echte exakte Bandbreiten-Suche (Branch-and-Bound mit erzwungenen Platzierungen) ------------------------------------------------------------------


def _degree_lower_bound(adj):
    """max_v ceil(deg(v)/2): jeder Knoten mit Grad d braucht auf beiden Seiten seiner Position zusammen mindestens d belegte Nachbarpositionen innerhalb der Bandbreite B, also 2B >= d
    (Standard-Schranke fuer die Bandbreite)."""
    n = len(adj)
    if n == 0:
        return 0
    return max((len(adj[v]) + 1) // 2 for v in range(n))


def _greedy_clique_lower_bound(adj):
    """Eine (nicht notwendig groesste) Clique per gierigem Aufbau von einigen hochgradigen Startknoten aus: eine Clique der Groesse q braucht q PAARWEISE VERSCHIEDENE Positionen, ihre kleinste
    erreichbare Spannweite ist q-1 - also B >= q-1 (Standard-Schranke). Wichtig fuer dichte/fast vollstaendige G(n,k,b)-Instanzen (z. B. b nahe n): ohne diese Schranke muesste die
    Zwangs-Platzierungs-Suche in `_bandwidth_feasible` erst viele zu kleine, aber erst spaet als unerfuellbar erkannte Schranken B durchprobieren (s. Vormessung tools/vormessung.py) - mit dieser
    Schranke startet die iterative Verschaerfung direkt nahe am wahren Optimum."""
    n = len(adj)
    if n == 0:
        return 0
    adjset = [set(a) for a in adj]
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    best = 1
    for start in order[: min(n, 6)]:
        clique = [start]
        candidates = set(adjset[start])
        for v in order:
            if v in candidates:
                clique.append(v)
                candidates &= adjset[v]
        if len(clique) > best:
            best = len(clique)
    return best


class _BudgetExceeded(Exception):
    pass


def _bandwidth_feasible(adj, bound, node_budget=None):
    """Testet, ob eine Nummerierung mit Bandbreite <= `bound` existiert (Positionen 0..n-1 nacheinander vergeben, Rueckverfolgung). Erzwungene Platzierung: hat ein bereits platzierter Knoten u
    an Position p-bound noch einen unplatzierten Nachbarn v, MUSS v jetzt (Position p) platziert werden - sonst wuerde |p'-p_u| > bound fuer jede spaetere Position p'>p. Zwei verschiedene derart
    erzwungene Knoten an derselben Position => sofort unerfuellbar. Kandidatenreihenfolge sonst: zuerst Knoten mit einem bereits platzierten Nachbarn (haelt die aktive Front eng), danach nach
    Index. Transpositionstabelle (Speicherzustaende): das Teilproblem "restliche Knoten `remaining` ab Position p platzieren" haengt NUR vom Fenster der letzten `bound` platzierten Knoten und
    von `remaining` ab (fruehere Platzierungen ausserhalb des Fensters sind entweder schon erledigt oder haetten bereits eine Zwangs-Platzierung ausgeloest) - ein einmal als unerfuellbar erkannter
    Zustand (Fenster, remaining) wird gespeichert und nie erneut durchsucht (verhindert das exponentielle Wiederholen aequivalenter Teilbaeume bei dichten, fast symmetrischen Graphen wie
    G(n,k,b), s. Vormessung tools/vormessung.py)."""
    n = len(adj)
    if n == 0:
        return True
    pos_of = [-1] * n
    placed_at = [-1] * n
    remaining = set(range(n))
    fail_memo = set()
    budget = [node_budget] if node_budget is not None else None

    def backtrack(p):
        if budget is not None:
            budget[0] -= 1
            if budget[0] <= 0:
                raise _BudgetExceeded()
        if p == n:
            return True
        forced = None
        for u in range(n):
            pu = pos_of[u]
            if pu != -1 and p - pu == bound:
                for v in adj[u]:
                    if pos_of[v] == -1:
                        if forced is None:
                            forced = v
                        elif forced != v:
                            return False
        state = None
        if forced is None:
            state = (tuple(placed_at[max(0, p - bound):p]), frozenset(remaining))
            if state in fail_memo:
                return False
            cand_list = sorted(remaining, key=lambda v: (0 if any(pos_of[u] != -1 for u in adj[v]) else 1, v))
        else:
            cand_list = [forced]
        for v in cand_list:
            if all(p - pos_of[u] <= bound for u in adj[v] if pos_of[u] != -1):
                pos_of[v] = p
                placed_at[p] = v
                remaining.discard(v)
                if backtrack(p + 1):
                    return True
                remaining.add(v)
                pos_of[v] = -1
                placed_at[p] = -1
        if state is not None:
            fail_memo.add(state)
        return False

    return backtrack(0)


def exact_bandwidth_layered(adj, upper_bound=None, node_budget=None):
    """NEUER, echter Branch-and-Bound-Loeser fuer die exakte Bandbreite: Ecken werden Position fuer Position eingefuegt (Rueckverfolgung bei Sackgasse), mit erzwungenen Platzierungen sobald ein
    Nachbar sonst aus dem Fenster faellt und einer Transpositionstabelle gegen wiederholte aequivalente Teilbaeume (`_bandwidth_feasible`). Iterative Verschaerfung: beginnend bei max(Grad-Schranke,
    Cliquen-Schranke) wird B = LB, LB+1, ... probiert, bis ein B zulaessig ist - das erste zulaessige B ist die exakte Bandbreite. `upper_bound`, falls gegeben, deckelt die Suche nach oben (z. B.
    ein bekannter Heuristik-Wert); ohne Angabe wird die beste von Cuthill-McKee/Reverse-Cuthill-McKee als Obergrenze verwendet. `node_budget`, falls gegeben, bricht eine einzelne Machbarkeitspruefung
    nach so vielen Rekursionsschritten ab und laesst die Funktion `None` liefern (fuer die Vormessung, die groessere Instanzen ausschliessen soll, statt beliebig lange zu suchen - s.
    `tools/vormessung.py`); ohne Angabe (Standard, so wie die App sie benutzt) wird immer zu Ende gerechnet. Klar unterschieden von `exact_bandwidth_bruteforce` (volle Permutation, nur n<=9):
    dieser Loeser reicht dank der Zwangs-Platzierungen und der Transpositionstabelle deutlich weiter (s. `cb_constants.EXACT_LAYERED_LIMIT`, in der Vormessung kalibriert)."""
    n = len(adj)
    if n <= 1:
        return 0
    if not any(adj[v] for v in range(n)):
        return 0
    if upper_bound is None:
        cm = cuthill_mckee(adj)
        rcm = reverse_cuthill_mckee(adj)
        upper_bound = min(bandwidth(adj, cm), bandwidth(adj, rcm))
    lo = max(_degree_lower_bound(adj), _greedy_clique_lower_bound(adj) - 1)
    try:
        for bound in range(lo, upper_bound + 1):
            if _bandwidth_feasible(adj, bound, node_budget):
                return bound
    except _BudgetExceeded:
        return None
    return upper_bound


# --- Satz 1a/1b (eigener Nachbau, numerisch nachvollzogen, kein neuer Beweis) ---------------------------------------------------------------------------


def bandwidth_satz1a(n, k, b):
    """Geschlossene Formel aus Satz 1a des Papers (b >= (n+k-1)/2): B(G_(n,k,b)) = ceil([(n+1)*C(b,k-1) - (k-1)*C(b+1,k) + C(2b-n+1,k) - 2] / 2). EIGENER NACHBAU, numerisch nachvollzogen (s.
    Korrektheits-Kette Punkt 3), kein neuer Beweis."""
    n, k, b = int(n), int(k), int(b)
    if k < 1:
        raise ValueError("k muss mindestens 1 sein")
    if 2 * b < n + k - 1:
        raise ValueError("Satz 1a gilt nur fuer b >= (n+k-1)/2")
    term = (n + 1) * math.comb(b, k - 1) - (k - 1) * math.comb(b + 1, k) + math.comb(2 * b - n + 1, k) - 2
    return math.ceil(term / 2)


def bandwidth_satz1b_asymptotic(n, k, b):
    """Asymptotische Formel aus Satz 1b (b=o(n)): k*C(b,k), nur als Vergleichsgroesse - KEIN Gueltigkeitstest, da asymptotisch (n->unendlich). EIGENER NACHBAU, numerisch nachvollzogen."""
    k, b = int(k), int(b)
    return k * math.comb(b, k)


def satz2_c1(beta, k):
    """c1(beta,k) = beta^k * (k - (k-1)/q) / k!, mit q,r aus 1 = q*beta + r (0<=r<beta, q>=2 ganzzahlig). EIGENER NACHBAU von Satz 2, numerisch nachvollzogen - die Vermutung selbst bleibt
    offen (s. README "Grenzen")."""
    q, _r = _qr(beta)
    return beta ** k * (k - (k - 1) / q) / math.factorial(k)


def satz2_c2(beta, k):
    q, _r = _qr(beta)
    return beta ** (k - 1) * (k - (k - 1) * beta) / ((q + 1) * math.factorial(k))


def satz2_c3(beta, k):
    q, r = _qr(beta)
    return (beta - r) ** k * q ** (k - 1) / ((q + 1) * math.factorial(k))


def _qr(beta):
    """1 = q*beta + r mit q ganzzahlig >= 2, 0 <= r < beta (q = ceil(1/beta), r = 1 - q*beta)."""
    beta = float(beta)
    if not (0 < beta < 1):
        raise ValueError("beta muss in (0,1) liegen")
    q = math.ceil(1.0 / beta)
    if q < 2:
        q = 2
    r = 1.0 - q * beta
    return q, r


# --- Faerbung/Cliquenzahl/Cliquenueberdeckung (wortgleiche Kopien aus gc_algorithm.py, Stueck 5) -----------------------------------------------------------


def clique_number(adj, exact_limit=None):
    """wortgleiche Kopie aus `gc_algorithm.py`, Stueck 5."""
    n = len(adj)
    if exact_limit is not None and n > exact_limit:
        return None, 0
    if n == 0:
        return 0, 0
    adjset = [set(a) for a in adj]
    best = [0]
    steps = [0]

    def expand(candidates, size):
        steps[0] += 1
        if not candidates:
            if size > best[0]:
                best[0] = size
            return
        if size + len(candidates) <= best[0]:
            return
        v = next(iter(candidates))
        rest = candidates - {v}
        expand(candidates & adjset[v], size + 1)
        if size + len(rest) > best[0]:
            expand(rest, size)

    expand(set(range(n)), 0)
    return best[0], steps[0]


def chromatic_number(adj, exact_limit=None):
    """wortgleiche Kopie aus `gc_algorithm.py`, Stueck 5."""
    n = len(adj)
    if exact_limit is not None and n > exact_limit:
        return None, 0
    if n == 0:
        return 0, 0
    omega, omega_steps = clique_number(adj, exact_limit)
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    total_steps = [omega_steps]

    def try_k(k):
        colors = [-1] * n

        def backtrack(i, max_used):
            total_steps[0] += 1
            if i == n:
                return True
            v = order[i]
            forbidden = {colors[u] for u in adj[v] if colors[u] != -1}
            hi = min(max_used + 1, k - 1)
            for c in range(hi + 1):
                if c in forbidden:
                    continue
                colors[v] = c
                if backtrack(i + 1, max(max_used, c)):
                    return True
                colors[v] = -1
            return False

        return backtrack(0, -1)

    k = max(omega, 1)
    while not try_k(k):
        k += 1
    return k, total_steps[0]


def greedy_color(adj, order, method="greedy"):
    """wortgleiche Kopie aus `gc_algorithm.py`, Stueck 5."""
    n = len(adj)
    colors = [-1] * n
    steps = 0
    events = []
    for v in order:
        steps += 1
        used = set()
        for u in adj[v]:
            steps += 1
            if colors[u] != -1:
                used.add(colors[u])
        c = 0
        while c in used:
            c += 1
        colors[v] = c
        events.append(("color", v, c))
    k = (max(colors) + 1) if colors else 0
    return ColoringResult(colors, k, steps, events, method)


@dataclass
class ColoringResult:
    colors: list
    k: int
    steps: int
    events: list
    method: str = ""


def complement(adj):
    """wortgleiche Kopie aus `gc_algorithm.py`, Stueck 5: u,v benachbart genau dann, wenn sie es in `adj` NICHT sind."""
    n = len(adj)
    adjset = [set(a) for a in adj]
    return [[u for u in range(n) if u != v and u not in adjset[v]] for v in range(n)]


def color_classes(colors):
    """wortgleiche Kopie aus `gc_algorithm.py`, Stueck 5."""
    classes = {}
    for v, c in enumerate(colors):
        classes.setdefault(c, []).append(v)
    return [sorted(vs) for vs in classes.values()]


def is_clique(adj, nodes):
    """wortgleiche Kopie aus `gc_algorithm.py`, Stueck 5."""
    adjset = [set(a) for a in adj]
    return all(v in adjset[u] for i, u in enumerate(nodes) for v in nodes[i + 1:])


def clique_cover_number(adj, exact_limit=None):
    """chi_v(G) = chi(complement(G)) - die EckenUEBERDECKUNGSZAHL DURCH CLIQUEN, dünner Wrapper (NEU): das ist chi_v aus Proposition 1 des Papers. Gibt (chi_v, steps) zurueck."""
    return chromatic_number(complement(adj), exact_limit)


# --- Schwacher Kantenclique-Graph (nach Engel und Hanisch) ---------------------------------------------------------------------------------------------------


def two_section_graph(universe_size, hyperedges):
    """Der 2-Sektionsgraph G_H: u,v benachbart, wenn eine Hyperkante beide enthaelt (woertliche Definition aus dem Paper)."""
    adj = [set() for _ in range(universe_size)]
    for e in hyperedges:
        for i in range(len(e)):
            for j in range(i + 1, len(e)):
                u, v = e[i], e[j]
                adj[u].add(v)
                adj[v].add(u)
    return [sorted(s) for s in adj]


def is_weak_clique(two_section_adj, nodes):
    """Prueft, ob `nodes` eine Clique im 2-Sektionsgraphen bildet (Anpassung von `is_clique` aus Stueck 5) - per Definition ist genau das eine schwache Clique von H."""
    adjset = [set(a) for a in two_section_adj]
    nodes = list(nodes)
    return all(v in adjset[u] for i, u in enumerate(nodes) for v in nodes[i + 1:])


def weak_edge_clique_graph(universe_size, hyperedges):
    """Der schwache Kantenclique-Graph G~_H: Ecken = Hyperkanten-Indizes; e,e' benachbart, wenn e u e' selbst eine schwache Clique ist (direkte Umsetzung der Paper-Definition, ueber
    `two_section_graph`/`is_weak_clique` unabhaengig von jeder Bruteforce-Referenz)."""
    ts = two_section_graph(universe_size, hyperedges)
    m = len(hyperedges)
    adj = [[] for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            union = sorted(set(hyperedges[i]) | set(hyperedges[j]))
            if is_weak_clique(ts, union):
                adj[i].append(j)
                adj[j].append(i)
    return adj


def weak_edge_clique_cover_bruteforce(universe_size, hyperedges, max_cliques=None):
    """Brute-Force-Referenz fuer chi_e(H) DIREKT aus der Definition (unabhaengig von G~_H/Proposition 1): probiert alle Partitionen der Hyperkanten in <= `max_cliques` Gruppen (restricted-
    growth-Strings, um Permutationen gleicher Partitionen zu vermeiden); eine Gruppe ist zulaessig, wenn die Vereinigung ihrer Hyperkanten eine schwache Clique ist (das ist notwendig UND
    hinreichend: die kleinste Clique, die alle Hyperkanten der Gruppe als Teilmenge enthaelt, ist ihre Vereinigung - zusaetzliche Ecken koennten fehlende Kanten im 2-Sektionsgraphen nicht
    reparieren). Das kleinste zulaessige c ist chi_e(H). Nur fuer kleine Hypergraphen gedacht (Bell-Zahl-Wachstum), s. `cb_constants.BRUTEFORCE_COVER_LIMIT`."""
    m = len(hyperedges)
    if m == 0:
        return 0
    ts = two_section_graph(universe_size, hyperedges)
    hyperedge_sets = [set(e) for e in hyperedges]
    if max_cliques is None:
        max_cliques = m

    def feasible(c):
        assignment = [0] * m

        def backtrack(i, used_labels):
            if i == m:
                groups = {}
                for idx, lab in enumerate(assignment):
                    groups.setdefault(lab, set()).update(hyperedge_sets[idx])
                return all(is_weak_clique(ts, sorted(g)) for g in groups.values())
            for lab in range(min(used_labels + 1, c)):
                assignment[i] = lab
                if backtrack(i + 1, max(used_labels, lab + 1)):
                    return True
            return False

        return backtrack(0, 0)

    for c in range(1, max_cliques + 1):
        if feasible(c):
            return c
    return max_cliques


# --- Selbst entworfene bandbreitenbeschraenkte Faerbungs-DP (NEU, eigenes Verfahren) ---------------------------------------------------------------------


@dataclass
class BandedColoringResult:
    colors: list
    k: int
    steps: int


def banded_coloring_dp(adj, order, bandwidth_of_order):
    """SELBST ENTWORFENES Verfahren (inspiriert von Bodlaenders DP-Rahmen fuer beschraenkte Baumweite/Bandbreite, ICALP 1988 - KEINE Umsetzung seines allgemeinen Verfahrens, s. README
    "Grenzen"): faerbt die Knoten entlang `order`, aber der Zustand je Schritt ist NUR ein Fenster der letzten `bandwidth_of_order` Positionen (Farbe je Fensterposition) statt einer vollen
    Nachbarschaftsabfrage - da die Bandbreite von `order` (per Definition/Voraussetzung) garantiert, dass JEDER Nachbar hoechstens `bandwidth_of_order` Positionen zurueckliegt, reicht dieses
    Fenster aus, um fuer jeden Knoten die kleinste zulaessige Farbe unter den TATSAECHLICH benachbarten Fensterknoten zu waehlen. Zustandsraum (Farbenzahl)^bandwidth_of_order - exponentiell in
    der Bandbreite, aber polynomiell in n (kein Backtracking, ein einziger Durchlauf). WICHTIG (Ehrlichkeit, Korrektheits-Kette Punkt 7): das ist ein GREEDY-Verfahren (eine einzige, nie
    zurueckgenommene Farbwahl je Knoten) und deshalb - wie jedes Greedy-Verfahren - unter Umstaenden schlechter als das globale Optimum `clique_cover_number`; es gewinnt NICHT automatisch gegen
    eine andere Greedy-Reihenfolge. Bewiesen (Satz, kein Messwert): die benutzte Farbenzahl ueberschreitet NIE `bandwidth_of_order + 1` (im Fenster koennen hoechstens `bandwidth_of_order`
    bereits gefaerbte Nachbarn liegen, es bleibt also immer eine Farbe aus {0,...,bandwidth_of_order} frei) - UND das Verfahren liefert, weil `bandwidth_of_order` >= der tatsaechlichen
    Bandbreite von `order` jeden echten Nachbarn ins Fenster zieht, GENAU dieselbe Faerbung wie `greedy_color(adj, order)` fuer dieselbe Reihenfolge (der Fenster-Zustand ist nur eine
    speichereffizientere Umsetzung derselben Regel, kein anderes Ergebnis)."""
    n = len(adj)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    b = int(bandwidth_of_order)
    colors = [-1] * n
    steps = 0
    for i, v in enumerate(order):
        used = set()
        for u in adj[v]:
            steps += 1
            pu = pos[u]
            if pu < i and i - pu <= b:
                c = colors[u]
                if c != -1:
                    used.add(c)
        c = 0
        while c in used:
            c += 1
        colors[v] = c
        steps += 1
    k = (max(colors) + 1) if colors else 0
    return BandedColoringResult(colors, k, steps)
