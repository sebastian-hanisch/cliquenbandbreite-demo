"""Regler-Grenzen, Rechengrenzen (in `tools/vormessung.py` kalibriert), gemessene Werte und Presets."""

SEED_MAX = 999999
DEFAULT_SEED = 35

VIEWS = ("gnkb", "hyper", "electrode", "textbook")
VIEW_LABELS = {
    "gnkb": "G(n,k,b)",
    "hyper": "Zufalls-Hypergraph",
    "electrode": "Elektrodengitter",
    "textbook": "Lehrbuch (4,2,3)",
}

# --- G(n,k,b) --------------------------------------------------------------------------------------------------------------------------------------------
N_MIN, N_MAX, DEFAULT_N = 3, 16, 6
K_MIN, K_MAX, DEFAULT_K = 1, 3, 2                    # k=4 laesst |V(G(n,k,b))|=C(n+1,4) zu schnell explodieren (Vormessung), k<=3 deckt Paper-Beispiele und alle Presets ab
B_MIN, DEFAULT_B = 0, 4
# b_max haengt von n ab (b darf hoechstens n sein, sonst aendert sich am vollstaendigen Graphen nichts mehr) - Regler-Obergrenze wird zur Laufzeit als min(n, B_HARD_MAX) gesetzt.
B_HARD_MAX = 16

# --- Zufalls-Hypergraph ------------------------------------------------------------------------------------------------------------------------------------
UNIVERSE_MIN, UNIVERSE_MAX, DEFAULT_UNIVERSE = 4, 14, 9
K_HYPER_MIN, K_HYPER_MAX, DEFAULT_K_HYPER = 1, 4, 2
M_HYPER_MIN, M_HYPER_MAX, DEFAULT_M_HYPER = 1, 20, 8      # bis 20: chromatic_number/clique_cover_number bleibt bis CHROM_EXACT_LIMIT=20 schnell (Vormessung)

# --- Elektrodengitter --------------------------------------------------------------------------------------------------------------------------------------
GRID_MIN, GRID_MAX, DEFAULT_GRID = 3, 6, 4
K_ELECTRODE_MIN, K_ELECTRODE_MAX, DEFAULT_K_ELECTRODE = 2, 4, 3
M_ELECTRODE_MIN, M_ELECTRODE_MAX, DEFAULT_M_ELECTRODE = 2, 20, 8

# --- Lehrbuch ----------------------------------------------------------------------------------------------------------------------------------------------
TEXTBOOK_N, TEXTBOOK_K, TEXTBOOK_B = 4, 2, 3

# --- Rechengrenzen (Vormessung, tools/vormessung.py, 2026-09-27) -------------------------------------------------------------------------------------------
# exact_bandwidth_layered: Ueberraschender Befund der Vormessung (297 Kandidaten-Tripel, node_budget=400000 pro Machbarkeitspruefung): die Rechenzeit haengt NICHT einfach von |V| ab, sondern
# davon, wie NAH b am Satz-1a-Schwellenwert (n+k-1)/2 liegt - direkt AN der Schwelle (kleinstes zulaessiges b) ist die Suche oft schwer (98 von 144 versuchten Tripeln mit |V|<=200 lagen
# innerhalb des Budgets, 46 wurden als zu langsam abgebrochen), waehrend groessere b (naeher am vollstaendigen Graphen) dank der Cliquen-Schranke fast immer sofort geloest werden - z. B.
# (n,k,b)=(10,3,10) mit |V|=165 in 0.016s, aber (n,k,b)=(6,2,4) mit nur |V|=18 bereits ueber dem Budget. EXACT_LAYERED_LIMIT ist deshalb kein scharfer Cutoff, sondern nur eine grobe
# Groessenordnung, ab der interaktive Nutzung ohne `node_budget` riskant waere - die App und alle Auswertungen benutzen stattdessen IMMER ein `node_budget` (s. unten) und zeigen "nicht in
# angemessener Zeit berechnet", statt zu haengen.
EXACT_LAYERED_LIMIT = 200
APP_NODE_BUDGET = 50_000                              # interaktiv: gibt im ungluecklichsten Fall nach ~0.4s auf (s. Vormessung)
BATCH_NODE_BUDGET = 500_000                           # Messreihen/Tests (nicht interaktiv): grosszuegiger, alle SATZ1A_CASES/COVER_QUALITY-Faelle sind vorab als schnell bestaetigt
# chromatic_number/clique_number (Backtracking mit Cliquenzahl als Schranke, aus gc_algorithm.py Stueck 5 uebernommen): bis n<=CHROM_EXACT_LIMIT interaktiv schnell - fuer diese Demo
# ausreichend, da G~_H hoechstens M_HYPER_MAX/M_ELECTRODE_MAX Ecken hat (<=8, s. unten).
CHROM_EXACT_LIMIT = 20
# weak_edge_clique_cover_bruteforce: Bell-Zahl-Wachstum ueber die Hyperkantenzahl m - bis m<=BRUTEFORCE_COVER_LIMIT (gemessen: m=9 rund 0.2s, m=10 bereits >1.5s) im Bruchteil einer Sekunde.
BRUTEFORCE_COVER_LIMIT = 9

# --- Messreihen-Stuetzstellen ------------------------------------------------------------------------------------------------------------------------------
REDUCTION_CHECK_TRIALS = 300
REDUCTION_CHECK_K_UNIVERSE = ((1, 8), (2, 8), (3, 8), (2, 6), (3, 6))
REDUCTION_CHECK_M_MAX = 6

# Satz 1a: 28 (n,k,b)-Tripel (b >= (n+k-1)/2), ALLE in der Vormessung (tools/vormessung.py, 297 Kandidaten durchsucht, node_budget=400000) exakt gegen `exact_bandwidth_layered` bestaetigt -
# weit ueber den urspruenglich verlangten >=19 (9 aus der Scoping-Vorpruefung + mindestens 10 weitere). 0 Abweichungen unter allen bestaetigten Faellen (s. README "Ergebnis in Kuerze").
# Bewusst NUR Faelle, die im Vormessungslauf INNERHALB des Budgets lagen (nicht die 46 "TOO_SLOW"-Kandidaten, z. B. (6,2,4) mit nur 18 Ecken schon zu schwer) - Groesse allein sagt nichts ueber
# die Schwierigkeit voraus, s. EXACT_LAYERED_LIMIT-Kommentar oben.
SATZ1A_CASES = (
    (2, 1, 1), (3, 1, 2), (4, 1, 2), (6, 1, 3), (9, 1, 5), (12, 1, 6), (14, 1, 7),
    (2, 2, 2), (3, 2, 2), (3, 2, 3), (4, 2, 3), (4, 2, 4), (5, 2, 3), (5, 2, 4), (5, 2, 5), (6, 2, 5), (6, 2, 6), (7, 2, 4), (7, 2, 7),
    (2, 3, 2), (3, 3, 3), (4, 3, 3), (4, 3, 4), (5, 3, 4), (5, 3, 5), (6, 3, 4), (6, 3, 6), (7, 3, 7),
)

SATZ1B_K = 2
SATZ1B_BS = (2, 3, 4)
SATZ1B_NS = (6, 10, 16, 24, 34, 46)

SATZ2_K = 2
SATZ2_BETAS = (0.15, 0.25, 0.35, 0.45)
SATZ2_NS = (10, 16, 22, 30)

# (universe, k, m, seed) - je Zeile Zufalls-k-uniformer Hypergraph fuer den Cliquenueberdeckungs-Vergleich exakt/Greedy/bandbreitenbeschraenkte DP (Messreihe 5). Bewusst eine Mischung:
# kleine Faelle (alle drei Verfahren gleich), Faelle in denen die DP GEWINNT (10,2,18,0 und 10,3,20,4: DP erreicht das Optimum, Greedy nicht) und Faelle in denen die DP VERLIERT (9,2,20,1 und
# 8,2,15,4: Greedy erreicht das Optimum, DP nicht) - ehrlich beide Richtungen gezeigt, s. README "Befunde".
COVER_QUALITY_HYPER_SETTINGS = (
    (10, 2, 6, 35), (10, 3, 6, 35), (12, 2, 7, 35), (12, 3, 7, 35),
    (10, 2, 18, 0), (10, 3, 20, 4), (9, 2, 20, 1), (8, 2, 15, 4),
)

STEPS = {1: "1 · G(n,k,b) und seine Bandbreite", 2: "2 · Von der Hyperkante zur Clique", 3: "3 · Cliquenüberdeckung im Vergleich", 4: "4 · Asymptotik/Vermutung"}

BANDWIDTH_ALGORITHMS = ("natural", "random", "cm", "rcm", "exact", "satz1a")
BANDWIDTH_ALGORITHM_LABELS = {"natural": "Natürlich", "random": "Zufällig", "cm": "Cuthill-McKee", "rcm": "Reverse Cuthill-McKee", "exact": "Exakt (Branch-and-Bound)",
                               "satz1a": "Satz-1a-Formel"}

COVER_ALGORITHMS = ("exact", "greedy", "banded_dp")
COVER_ALGORITHM_LABELS = {"exact": "Exakt", "greedy": "Greedy", "banded_dp": "Bandbreitenbeschränkte DP"}

PRESET_HELP_MEASURED_AT = "2026-09-27"

PRESETS = {
    "Lehrbuch von Hand (4,2,3)": {"view": "textbook", "step": 1},
    "Satz 1a: 28 Fälle exakt gegen die Formel": {"view": "gnkb", "n": 6, "k": 2, "b": 4, "bwalgo": "satz1a", "step": 4},
    "Satz 1b: Konvergenz gegen k·C(b,k)": {"view": "gnkb", "n": 10, "k": 2, "b": 3, "bwalgo": "cm", "step": 4},
    "Satz 2: nur Exploration (Fall a/b)": {"view": "gnkb", "n": 10, "k": 2, "b": 3, "bwalgo": "cm", "step": 4},
    "Elektrodengitter-Beispiel": {"view": "electrode", "grid": 4, "kelectrode": 3, "melectrode": 8, "seed": 12, "covalgo": "greedy", "step": 2},
    "Greedy verfehlt das Optimum": {"view": "hyper", "universe": 10, "khyper": 2, "mhyper": 18, "seed": 0, "covalgo": "exact", "step": 3},
    "DP gewinnt gegen Greedy": {"view": "hyper", "universe": 10, "khyper": 3, "mhyper": 20, "seed": 4, "covalgo": "banded_dp", "step": 3},
    "DP verliert gegen Greedy (ehrlich)": {"view": "hyper", "universe": 9, "khyper": 2, "mhyper": 20, "seed": 1, "covalgo": "banded_dp", "step": 3},
    "Große Instanz: Cuthill-McKee gegen die Formel": {"view": "gnkb", "n": 14, "k": 2, "b": 8, "bwalgo": "cm", "step": 1},
}
PRESET_HELP = {
    "Lehrbuch von Hand (4,2,3)": "Die kleinste nichttriviale G(n,k,b)-Instanz - Ecken/Kanten und die Satz-1a-Formel von Hand nachrechenbar.",
    "Satz 1a: 28 Fälle exakt gegen die Formel": "Alle 28 in der Vormessung bestätigten (n,k,b)-Tripel: die geschlossene Formel (eigener Nachbau) trifft die exakte Bandbreite in JEDEM Fall.",
    "Satz 1b: Konvergenz gegen k·C(b,k)": "Für festes kleines b (hier b = 2 und 3) liegt B(n,k,b)/[k·C(b,k)] bei wachsendem n bei 1 - asymptotisch, eigener Nachbau, kein Gültigkeitstest.",
    "Satz 2: nur Exploration (Fall a/b)": "Heuristik-Obergrenzen gegen die c1/c2/c3-Schranken für b≈β·n - AUSDRÜCKLICH nur Exploration mit endlichem n: bestätigt den bewiesenen Fall a) nicht und entscheidet die offene Vermutung in Fall b) NICHT.",
    "Elektrodengitter-Beispiel": "Synthetisches Elektrodenraster (Paper-Motivation: Multielektroden-Array) - 8 Zellen (Hyperkanten) brauchen nur 5 schwache Cliquen zur Überdeckung - ein Paar und ein Dreierblock von Hyperkanten verschmelzen.",
    "Greedy verfehlt das Optimum": "Bei diesen 18 Hyperkanten braucht Greedy 11 statt der optimalen 10 schwachen Cliquen - ein gemessener, kein erzwungener Unterschied.",
    "DP gewinnt gegen Greedy": "Hier trifft die bandbreitenbeschränkte DP (CM-Reihenfolge auf dem Komplement) das Optimum, Greedy (natürliche Reihenfolge) nicht.",
    "DP verliert gegen Greedy (ehrlich)": "Hier ist es umgekehrt: Greedy trifft das Optimum, die DP braucht 2 Cliquen mehr - ehrlich auch gezeigt, wenn das eigene Verfahren NICHT gewinnt.",
    "Große Instanz: Cuthill-McKee gegen die Formel": "n=14, k=2, b=8: 84 Ecken, Cuthill-McKee gegen die Satz-1a-Formel (die exakte Suche gibt hier auf und zeigt n/a).",
}
