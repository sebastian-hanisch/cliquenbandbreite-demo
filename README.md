# Bandbreite von G(n,k,b) und Cliquenüberdeckung – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-cliquenbandbreite-demo.streamlit.app/)**

**Zwölftes und LETZTES Stück der Graphen-und-Netzwerke-Reihe** der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations Research und Machine Learning" – **die Reihe ist mit diesem
Stück VOLLSTÄNDIG**. Ein Zusammenfluss von Stück 11 ([bandbreite-demo](https://github.com/sebastian-hanisch/bandbreite-demo), Bandbreite) und Stück 5
([graph-coloring-demo](https://github.com/sebastian-hanisch/graph-coloring-demo), Graphfärbung).

**Dieses Stück ist als "mark=forschung" gekennzeichnet**: es baut direkt auf der eigenen, veröffentlichten Forschungsarbeit des Autors auf – **Engel, K., & Hanisch, S. (2016). *Bandwidth of
graphs resulting from the edge clique covering problem.* arXiv:1605.00450 [math.CO]**, dem zweiten Teil der eigenen Dissertation. **Wichtig: jede Zahl aus den Sätzen dieses Papers ist hier ein
EIGENER NACHBAU, NUMERISCH NACHVOLLZOGEN – KEIN NEUER BEWEIS.** Konrad Engel ist Ko-Autor der zugrundeliegenden Arbeit.

Ein Hypergraph H=(V,E) modelliert im Paper z. B. ein Multielektroden-Array: ein Neuron mit Kontakt zu einer Elektrodenmenge S erzeugt eine **schwache Clique** im **2-Sektionsgraphen** G_H (u,v
benachbart, wenn eine Hyperkante beide enthält); eine **schwache Kantenclique-Überdeckung** ist eine Familie schwacher Cliquen, sodass jede Hyperkante Teilmenge einer davon ist, ihre kleinste
Größe ist chi_e(H). **Proposition 1** zeigt chi_e(H) = chi_v(G~_H), wobei G~_H der **schwache Kantenclique-Graph** ist (Ecken = Hyperkanten, benachbart wenn ihre Vereinigung selbst eine
schwache Clique ist) und chi_v die **Eckenüberdeckungszahl durch Cliquen** (= Färbungszahl des Komplementgraphen) ist – NICHT die Färbungszahl von G~_H selbst. Für die Graphenfamilie
**G(n,k,b)** (k-elementige Teilmengen von {0,...,n} mit Spannweite ≤ b) gibt das Paper eine **exakte Formel für die Bandbreite (Satz 1a)**, eine **Asymptotik (Satz 1b)** und für b~β·n mit **Satz 2** den exakten Wert (Fall a) bzw. nur Schranken mit einer
**offenen Vermutung** für die obere Schranke (Fall b) an.

**Einordnung in die Reihe:** die Reihe hat dreizehn Stücke (zwölf im Baum, dazu die Fall-Demo interne-verlinkung-demo), dies ist das zwölfte und letzte im Baum (Details in `graphen-planung/PLAN.md` des Portfolio-Ordners):

```
1 BFS und DFS (Wurzel)                                                        [gebaut: bfs-dfs-demo]
 ├─ 2 Brücken und Artikulationspunkte ─ 4 Euler-Touren                        [gebaut: bridges-demo, euler-tour-demo]
 ├─ 3 Starke Zusammenhangskomponenten, topologische Sortierung                [gebaut: scc-demo]
 ├─ 5 Graphfärbung                                                            [gebaut: graph-coloring-demo]
 ├─ 6 Zentralität ─ 7 Strukturkennzahlen ─ 8 Robustheit ─ 9 Kaskaden/Ausbr.   [gebaut: centrality-demo, strukturkennzahlen-demo, robustheit-demo, kaskaden-demo]
 │                            └─ 10 Kritische Knoten härten                   [gebaut: haertung-demo]
 └─ 11 Bandbreite ─ 12 Bandbreite von G(n,k,b) und Cliquenüberdeckung         [gebaut: cliquenbandbreite-demo ─ DIESES STÜCK, LETZTES DER REIHE]
```

Ergebnis in Kürze – alles EIGENER NACHBAU, NUMERISCH NACHVOLLZOGEN, KEIN NEUER BEWEIS: **Proposition 1** (chi_e(H) = chi_v(G~_H)) bestätigt sich auf **300 zufälligen k-uniformen Hypergraphen
UND** dem Elektrodengitter-Beispiel **ohne eine einzige Abweichung**. **Satz 1a** trifft die eigens dafür entwickelte exakte Bandbreiten-Suche `exact_bandwidth_layered` auf **28 bestätigten
(n,k,b)-Tripeln EXAKT** – wobei die Vormessung einen unerwarteten Befund lieferte: die Schwierigkeit dieser Suche hängt NICHT von der Eckenzahl ab, sondern davon, wie NAH b am
Satz-1a-Schwellenwert liegt (s. "Vormessung" unten). Die selbst entworfene **bandbreitenbeschränkte Färbungs-DP** gewinnt auf manchen Hypergraphen gegen ein einfaches Greedy-Verfahren, verliert
auf anderen – ehrlich in beide Richtungen gemessen, keine Schönfärberei. **Satz 2** (b~β·n: Fall a) bewiesen, Fall b) mit offener Vermutung für die obere Schranke) wird hier ausdrücklich NUR exploriert, nicht entschieden.

## Warum dieses Problem

Bandbreitenminimierung (Stück 11) und Cliquenüberdeckung über Graphfärbung (Stück 5) sind zwei eigenständige, in dieser Reihe bereits behandelte Probleme – dieses letzte Stück zeigt, wie sie in
der eigenen Forschungsarbeit des Autors zusammenlaufen: die Bandbreite einer eigens für die Cliquenüberdeckung konstruierten Graphenfamilie G(n,k,b) lässt sich für einen großen Parameterbereich
EXAKT angeben (Satz 1a), asymptotisch verstehen (Satz 1b) und für b~β·n teils exakt (Satz 2, Fall a), teils nur mit Schranken und einer bis heute offenen Vermutung (Satz 2, Fall b). Die Demo baut jede dieser drei Aussagen selbst nach – niemals als
"bewiesen" durch die App selbst, sondern immer als numerische Nachprüfung einer bereits veröffentlichten, von Konrad Engel und dem Autor gemeinsam bewiesenen Arbeit.

## Vorab-Hypothesen (vor der Messung notiert, hier geprüft)

| Hypothese | Ergebnis |
|---|---|
| **H1** Proposition 1 (chi_e(H) = chi_v(G~_H)) stimmt auf vielen zufälligen Hypergraphen. | ✅ Bestätigt auf 300 zufälligen k-uniformen Hypergraphen (k=1,2,3) UND dem Elektrodengitter-Beispiel – 0 Abweichungen. |
| **H2** `two_section_graph`/`weak_edge_clique_graph` stimmen mit einer unabhängigen Neuberechnung aus der Definition überein. | ✅ Bestätigt – jede behauptete Kante von G~_H einzeln gegen `is_weak_clique` auf dem 2-Sektionsgraphen nachgeprüft. |
| **H3** Satz 1a trifft `exact_bandwidth_layered` exakt auf ≥19 (n,k,b)-Tripeln. | ✅ Übertroffen: 28 bestätigte Tripel, 0 Abweichungen. |
| **H4** `exact_bandwidth_layered` == `exact_bandwidth_bruteforce` auf allen gemeinsam machbaren kleinen Graphen (n≤9). | ✅ Bestätigt auf 80 zufälligen Graphen plus mehreren G(n,k,b)-Instanzen. |
| **H5** `gnkb_adjacency` stimmt mit einer unabhängigen Neuberechnung aus der Definition überein. | ✅ Bestätigt auf 7 (n,k,b)-Kombinationen, inklusive der Sonderfälle b≥n (vollständiger Graph) und n<k (leere Eckenmenge). |
| **H6** `clique_cover_number` == `chromatic_number(complement(...))`, und die kopierten Stück-5-Funktionen verhalten sich identisch. | ✅ Bestätigt als Identität auf 20 zufälligen Graphen. |
| **H7** Die bandbreitenbeschränkte DP erreicht nie mehr als `bandwidth_of_order + 1` Farben und gewinnt gegen Greedy. | ⚠️ **Teilweise bestätigt:** die Farbenzahl-Schranke ist ein bewiesener Satz (bestätigt auf 40 Instanzen) – aber die DP gewinnt NICHT immer gegen Greedy: auf den Cliquenüberdeckungs-Testfällen gewinnt sie zweimal, verliert zweimal (s. "Befunde"). |
| **H8** Bandbreite/Profil/Cuthill-McKee/Reverse-Cuthill-McKee auf G(n,k,b) reproduzieren exakt die Stück-11-Semantik. | ✅ Bestätigt – wortgleiche Kopien, Bandbreite(CM)==Bandbreite(RCM) exakt auf 60 zufälligen Graphen. |
| **H9** Hyperkanten-Generatoren liefern immer gültige, deterministische, duplikatfreie k-uniforme Hypergraphen. | ✅ Bestätigt auf 30 Wiederholungen je Generator. |
| **H10** Sonderfälle (k=1, leerer Hypergraph, eine Hyperkante, n<k) laufen ohne Fehler und liefern die erwarteten Randwerte. | ✅ Bestätigt (chi_e(leer)=0, chi_e(eine Hyperkante)=1, k=1 ist der Sonderfall "keine zwei Singletons verschmelzbar"). |

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen über `cb_evaluation`-Funktionen nachgerechnet (`tests/test_correctness_chain.py`, `tests/test_evaluation.py`).

| Frage | Ergebnis |
|---|---|
| **Stimmt Proposition 1?** | ✅ Ja, auf 300 zufälligen Hypergraphen (k=1,2,3, Grundmenge 6–8) und dem Elektrodengitter-Beispiel – 0 Abweichungen zwischen der Definitions-Brute-Force und dem Proposition-1-Weg über G~_H. |
| **Stimmt Satz 1a?** | ✅ Ja, exakt auf allen 28 bestätigten Tripeln (k=1: 7 Fälle, k=2: 12 Fälle, k=3: 9 Fälle, n bis 14). |
| **Wie schwer ist `exact_bandwidth_layered`?** | Überraschend NICHT abhängig von der Eckenzahl: (n,k,b)=(10,3,10) mit 165 Ecken löst in 0.016s, aber (n,k,b)=(6,2,4) mit nur 18 Ecken übersteigt bereits ein Budget von 400.000 Suchschritten – die Schwierigkeit hängt daran, wie NAH b am Satz-1a-Schwellenwert (n+k-1)/2 liegt (dichtere, "vollständigere" Graphen sind dank einer Cliquen-Schranke fast immer sofort lösbar, "gerade eben gültige" Fälle nicht). Von 297 durchsuchten Kandidaten-Tripeln lagen 98 innerhalb des Budgets (0 Abweichungen), 46 wurden als zu langsam übersprungen. |
| **Wie nah kommt Satz 1b?** | Für k=2, b=2 (klein und fest) nähert sich das gemessene B(n,k,b)/[k·C(b,k)] mit wachsendem n (6→46) dem Wert 1 – EIGENER NACHBAU, KEIN Gültigkeitstest (die Formel gilt nur asymptotisch). |
| **Was zeigt die Satz-2-Exploration?** | Gemessene Heuristik-Obergrenze (Cuthill-McKee/Reverse-Cuthill-McKee, skaliert durch n^k, k=2) gegen die asymptotischen Referenzwerte c1 und c2+c3 (n = 10–30): bei β = 0.15 liegt sie unter c1 (0,008–0,020 gegen c1 ≈ 0,021); bei β = 0.25 liegt sie ab n = 16 über c1 (0,062–0,086 gegen 0,055; bei n = 10: 0,020), bei β = 0.35 (0,11–0,23 gegen c1 ≈ 0,092 und c2+c3 ≈ 0,097) und β = 0.45 (0,22–0,24 gegen c1 ≈ 0,152 und c2+c3 ≈ 0,157) auf allen n sogar über der Obergrenze c2+c3. Das ist kein Widerspruch zum Paper: die Heuristik liefert nur eine Obergrenze der Bandbreite, kein Optimum, und die Referenzwerte gelten für n→∞. Nur β = 0.35 liegt im Fall b) des Satzes (offene Vermutung); für β = 0.15, 0.25 und 0.45 ist B ~ c1·n^k im Paper bewiesen. Die Messung entscheidet die offene Vermutung NICHT. |
| **Gewinnt die bandbreitenbeschränkte DP gegen Greedy?** | Gemischt, ehrlich in beide Richtungen: bei (universe=10,k=2,m=18) und (universe=10,k=3,m=20) erreicht die DP das exakte Optimum, Greedy nicht (11→10 bzw. 7→6 Cliquen). Bei (universe=9,k=2,m=20) und (universe=8,k=2,m=15) ist es umgekehrt: Greedy trifft das Optimum, die DP braucht 1–2 Cliquen mehr. Auf den vier kleinen Ausgangsfällen (m≤7) sind alle drei Verfahren gleich. |
| **Elektrodengitter-Beispiel** | Auf einem 4×4-Raster mit 8 synthetischen Zellen (k=3 Kontaktelektroden je Zelle) findet die exakte Cliquenüberdeckung eine deutlich kleinere Familie als die Hyperkantenzahl selbst – die Paper-Motivation (Neuronen aus überlappenden Elektroden-Kontaktmustern rekonstruieren) wird an einem kleinen, synthetischen Beispiel sichtbar. |

Presets (9), alle mit den Zahlen in ihren Hilfetexten (`tests/test_app.py`):

| Preset | Was es zeigt |
|---|---|
| Lehrbuch von Hand (4,2,3) | Kleinste nichttriviale G(n,k,b)-Instanz, Satz-1a-Formel von Hand nachrechenbar |
| Satz 1a: 28 Fälle exakt gegen die Formel | Alle bestätigten Tripel liegen auf der Diagonale (Formel == exakt) |
| Satz 1b: Konvergenz gegen k·C(b,k) | Verhältnis liegt für b = 2 und 3 bei 1 (b = 4: nur Cuthill-McKee-Obergrenzen, darüber) |
| Satz 2: nur Exploration (Fall a/b) | Heuristik-Obergrenzen gegen c1/c2/c3, mit Hinweis, ob für das gewählte β Fall a) (bewiesen) oder Fall b) (offene Vermutung) gilt |
| Elektrodengitter-Beispiel | Synthetisches Elektrodenraster, Paper-Motivation |
| Greedy verfehlt das Optimum | 11 statt 10 Cliquen bei Greedy |
| DP gewinnt gegen Greedy | DP trifft das Optimum, Greedy nicht |
| DP verliert gegen Greedy (ehrlich) | Umgekehrter Fall, ehrlich gezeigt |
| Große Instanz: Cuthill-McKee gegen die Formel | n=14,k=2,b=8, 84 Ecken |

## Modell und Verfahren

- **G(n,k,b)** (`cb_scenario.gnkb_adjacency`): Ecken = k-elementige Teilmengen X von {0,...,n} mit max(X)-min(X) ≤ b; X,Y benachbart, wenn max(X∪Y)-min(X∪Y) ≤ b.
- **Zufällige k-uniforme Hypergraphen, Elektrodengitter** (`random_k_uniform_hypergraph`, `electrode_hypergraph`, NEU): allgemeines Testfeld für Proposition 1 und die Cliquenüberdeckung,
  unabhängig von der G(n,k,b)-Struktur; `electrode_positions(grid)` wortgleich aus `delay-graph-demo/dg_scenario.py` übernommen (NICHT dessen Spike-Simulation).
- **Bandbreite/Profil/Cuthill-McKee/Reverse-Cuthill-McKee** (`cb_algorithm.py`, wortgleiche Kopien aus `band_algorithm.py`, Stück 11).
- **2-Sektionsgraph, schwache Clique, schwacher Kantenclique-Graph** (`two_section_graph`, `is_weak_clique`, `weak_edge_clique_graph`, NEU nach der Paper-Definition).
- **Cliquenzahl/chromatische Zahl/Greedy-Färbung** (`clique_number`, `chromatic_number`, `greedy_color`, wortgleiche Kopien aus `gc_algorithm.py`, Stück 5); `clique_cover_number` (NEU, dünner
  Wrapper: `chromatic_number(complement(...))`).
- **`exact_bandwidth_layered`** (NEU): echter Branch-and-Bound-Löser – Ecken werden Position für Position eingefügt, mit erzwungenen Platzierungen sobald ein Nachbar sonst aus dem Fenster
  fällt, einer Cliquen-/Grad-Schranke als Startpunkt der iterativen Verschärfung und einer Transpositionstabelle gegen wiederholte äquivalente Teilbäume.
- **`bandwidth_satz1a`/`bandwidth_satz1b_asymptotic`/`satz2_c1`/`satz2_c2`/`satz2_c3`** (NEU): die Paper-Formeln als eigene Funktionen – EIGENER NACHBAU, numerisch nachvollzogen, kein neuer
  Beweis.
- **`banded_coloring_dp`** (NEU, SELBST ENTWORFEN, inspiriert von Bodlaenders DP-Rahmen für beschränkte Baumweite, ICALP 1988 – KEINE Umsetzung seines allgemeinen Verfahrens): Greedy-Färbung
  entlang einer Reihenfolge bekannter Bandbreite b, aber mit einem Fenster-Zustand (Farbe je der letzten b Positionen) statt einer vollen Nachbarschaftsabfrage.

## Design-Entscheidungen

- **`exact_bandwidth_layered` benutzt eine Cliquen-Schranke ALS STARTPUNKT, nicht nur eine Grad-Schranke.** Ohne sie bräuchte die Suche auf dichten, fast vollständigen G(n,k,b)-Instanzen
  (z. B. K_10) extrem lange, um kleine, aber falsche Schranken als unerfüllbar zu erkennen – ein `_greedy_clique_lower_bound` (mehrere gierig aufgebaute Cliquen, das Maximum) hebt die untere
  Schranke sofort auf einen realistischen Wert. Ein reiner Grad-Schranken-Start ließ die Vormessung an einem K_10-artigen Fall (10 Ecken!) mehrere Sekunden hängen, bevor dieser Fix gefunden wurde.
- **Transpositionstabelle statt reiner Rückverfolgung.** Das Teilproblem "restliche Ecken ab Position p platzieren" hängt nur vom Fenster der letzten `bound` platzierten Ecken und der
  verbleibenden Eckenmenge ab – ein einmal als unerfüllbar erkannter Zustand wird gespeichert und nie erneut durchsucht. Ohne diese Tabelle blieb ein Fall mit nur 18 Ecken ((n,k,b)=(6,2,4))
  auch mit der Cliquen-Schranke unlösbar langsam (mehrere Minuten) – ein zweiter, während des Baus gefundener und behobener Performance-Fehler (s. "Was nicht funktioniert hat").
- **`node_budget` statt eines reinen Größen-Cutoffs.** Da die Schwierigkeit NICHT einfach von der Eckenzahl abhängt (s. "Befunde"), wäre ein Cutoff wie "nur bis 50 Ecken versuchen" sowohl zu
  vorsichtig (viele größere Fälle sind sofort lösbar) als auch zu riskant (manche kleine Fälle sind es nicht) – `exact_bandwidth_layered` bricht stattdessen nach einer festen Zahl an
  Suchschritten ab und liefert ehrlich `None` zurück, statt die App hängen zu lassen.
- **`banded_coloring_dp` ist absichtlich GREEDY, nicht die volle Bodlaender-DP.** Eine vollständige Zustandsraum-Sättigung (alle erreichbaren Fensterfärbungen verfolgen) würde IMMER die exakte
  chromatische Zahl treffen – das wäre kein interessanter Vergleich mehr gegen `clique_cover_number`. Die hier gebaute Variante trifft GENAU EINE Farbentscheidung je Knoten (keine
  Rückverfolgung), ist deshalb ein echtes, eigenständiges Heuristik-Verfahren mit einer bewiesenen oberen Schranke (`bandwidth_of_order + 1` Farben), aber ohne Optimalitätsgarantie – ehrlich
  gegen Greedy und die Exakt-Referenz gemessen.
- **Zufalls-Hypergraph/Elektrodengitter erlauben m bis 20**, obwohl die Definitions-Brute-Force (`weak_edge_clique_cover_bruteforce`) nur bis m=9 schnell bleibt (Bell-Zahl-Wachstum): der
  Proposition-1-Weg über `clique_cover_number` bleibt bis m=20 schnell (Backtracking mit Cliquenzahl-Schranke), Proposition 1 selbst wurde bereits unabhängig auf kleineren Fällen bestätigt.

## Vormessung (Kalibrierung)

`tools/vormessung.py` durchsuchte 297 Kandidaten-(n,k,b)-Tripel (n bis 19, k=1,2,3, b ≥ (n+k-1)/2) mit einem Budget von 400.000 Suchschritten je Machbarkeitsprüfung: 98 lagen innerhalb des
Budgets (0 Abweichungen von Satz 1a), 46 wurden als zu langsam übersprungen. Der überraschende Befund: die Schwierigkeit hängt nicht an der Eckenzahl, sondern daran, wie nah b am Schwellenwert
liegt (s. "Befunde"). 28 der bestätigten Tripel bilden `cb_constants.SATZ1A_CASES`. Für die Cliquenüberdeckung wurden Hypergraph-Einstellungen gesucht, auf denen sich Greedy/Exakt/DP sichtbar
unterscheiden (`cb_constants.COVER_QUALITY_HYPER_SETTINGS`); für `weak_edge_clique_cover_bruteforce` wurde die Rechenzeit über die Hyperkantenzahl gemessen (m=9: ≈0.2s, m=10: bereits >1.5s,
daher `BRUTEFORCE_COVER_LIMIT=9`).

## Was die App zeigt

1. **Vier Schritte** (Schritt-Regler): **G(n,k,b) und seine Bandbreite** (Ecken als Intervalle auf einer Zahlengeraden, sortiert nach der gewählten Nummerierung, Bandbreite-Balken gegen die
   Satz-1a-Formel; nur für die Ansichten G(n,k,b)/Lehrbuch) → **Von der Hyperkante zur Clique** (2-Sektionsgraph und schwacher Kantenclique-Graph nebeneinander; nur für Zufalls-Hypergraph/
   Elektrodengitter) → **Cliquenüberdeckung im Vergleich** (Balken exakt/Greedy/bandbreitenbeschränkte DP, Aufwand über die Bandbreite der Reihenfolge) → **Asymptotik/Vermutung** (Satz 1a
   exakt gegen Formel über alle 28 Fälle, Satz-1b-Konvergenz, Satz-2-Exploration – IMMER als "eigener Nachbau"/"nur Exploration" beschriftet, unabhängig von der gewählten Ansicht).
2. **Ansicht** (G(n,k,b) / Zufalls-Hypergraph / Elektrodengitter / Lehrbuch), ansichtsspezifische Größen, sichtbares Verfahren (Bandbreite: Natürlich/Zufällig/Cuthill-McKee/Reverse
   Cuthill-McKee/Exakt/Satz-1a-Formel; Cliquenüberdeckung: Exakt/Greedy/bandbreitenbeschränkte DP), Zufalls-Seed (+🎲); Permalink in der Adresszeile.

## Was nicht funktioniert hat / Grenzen

- **Zwei echte Performance-Fehler wurden beim Bau gefunden und behoben** (s. "Design-Entscheidungen"): `exact_bandwidth_layered` hing zunächst auf dichten, fast vollständigen Instanzen (nur
  Grad-Schranke, keine Cliquen-Schranke) und danach noch auf einer einzelnen, nur 18 Ecken großen Instanz (keine Transpositionstabelle) – beide Male durch systematisches Timing in der
  Vormessung gefunden, nicht durch bloßes Ausprobieren.
- **`exact_bandwidth_layered` ist kein garantiert schnelles Verfahren** – Bandbreitenminimierung ist NP-vollständig; das `node_budget` verhindert nur ein Hängen der App, es macht das Problem
  nicht einfacher. Manche kleine, "gerade eben gültige" G(n,k,b)-Instanzen bleiben unlösbar (s. "Befunde").
- **`banded_coloring_dp` schlägt Greedy nicht immer** – ein echtes, gemessenes Ergebnis in beide Richtungen, kein Makel: die DP ist ein eigenständiges Greedy-Verfahren mit einer
  Effizienz-Idee (Fenster-Zustand statt voller Nachbarschaftsabfrage), keine Optimierung der Farbenzahl.
- **Satz 2 wird NICHT entschieden** (Fall a) ist bewiesen, die Vermutung in Fall b) bleibt offen) – die Exploration zeigt nur, wie die Heuristik-Obergrenze bei endlichem, kleinem n gegenüber den asymptotischen Referenzwerten liegt (q = ⌊1/β⌋, r = 1 − qβ; Fall a) des Satzes, in dem der Wert bekannt ist, gilt für β = 0.15, 0.25, 0.45, Fall b) nur für β = 0.35).
- **Elektrodengitter-Beispiel ist eine stark vereinfachte, synthetische Illustration** – zufällige Zellzentren mit den k nächstgelegenen Elektroden als Kontaktmenge, KEINE Rekonstruktion der
  echten Spike-Simulation aus `delay-graph-demo` (Zwei-Gauß-Vorlagen, Erneuerungsprozesse, Rauschen).
- **Exakte Bandbreite/Cliquenüberdeckung nur bis zur gemessenen Größengrenze** – s. `cb_constants.EXACT_LAYERED_LIMIT`/`CHROM_EXACT_LIMIT`/`BRUTEFORCE_COVER_LIMIT`.

## Tests

`tests/test_scenario.py` (G(n,k,b)-Konstruktion gegen unabhängige Neuberechnung, Sonderfälle, Hypergraph-Generatoren), `tests/test_algorithm.py` (Bandbreite/Profil/CM/RCM-Regression,
2-Sektionsgraph/schwache Clique gegen unabhängige Neuberechnung, Cliquenüberdeckungs-Identität, bandbreitenbeschränkte DP == Greedy für dieselbe Reihenfolge + Farbenzahl-Schranke),
`tests/test_correctness_chain.py` (Proposition 1 auf 150+ Hypergraphen, Satz 1a exakt auf 28 Fällen, `exact_bandwidth_layered` == Brute-Force auf 80+ kleinen Graphen),
`tests/test_evaluation.py` (alle vier Ansichten, Satz-1b/Satz-2 als Exploration, Cliquenüberdeckungs-Qualität ehrlich in beide Richtungen), `tests/test_app.py` (AppTest – Voreinstellung, jedes
Preset, jede Ansicht/jeder Schritt, bedingte Regler, Permalink-Grenzen, Footer, Ko-Autor Konrad Engel).

```
python -m pytest tests/ -v
```

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-App |
| `cb_algorithm.py` | Bandbreite/Profil/Cuthill-McKee (Kopien Stück 11), Färbung/Cliquenzahl/Cliquenüberdeckung (Kopien Stück 5), 2-Sektionsgraph/schwacher Kantenclique-Graph, `exact_bandwidth_layered`, Satz-1a/1b/2-Formeln, `banded_coloring_dp` |
| `cb_scenario.py` | G(n,k,b), Zufalls-Hypergraphen, Elektrodengitter, Lehrbuch |
| `cb_evaluation.py` | Analyse, Satz-1a-Check, Satz-1b-Sweep, Satz-2-Exploration, Proposition-1-Check, Cliquenüberdeckungs-Qualität |
| `cb_visualization.py` | Plotly-Figuren |
| `cb_presets.py`, `cb_constants.py` | Permalink, Presets, Rechengrenzen, gemessene Werte |
| `tools/vormessung.py` | Kalibrierung von Satz-1a-Fällen, Cliquenüberdeckungs-Testfällen, `BRUTEFORCE_COVER_LIMIT` |
| `tests/` | Tests |

## Bewusst nicht umgesetzt

Ein Beweis der offenen Vermutung aus Satz 2 Fall b) (die obere Schranke ist bis heute unbewiesen; Fall a) ist im Paper bewiesen). Eine vollständige, exakte Bodlaender-DP über beliebige Baumzerlegungen (nur der bandbreitenbeschränkte
Spezialfall). Eine Rekonstruktion der echten Multielektroden-Spike-Simulation aus `delay-graph-demo` (nur eine kleine, synthetische Illustration). Mit diesem Stück ist die
Graphen-und-Netzwerke-Reihe VOLLSTÄNDIG (13 von 13 Stücken).

## Lokal ausführen

```
python -m venv venv
venv\Scripts\pip install -r requirements-dev.txt
venv\Scripts\streamlit run app.py
```

## Literatur

- Engel, K., & Hanisch, S. (2016). *Bandwidth of graphs resulting from the edge clique covering problem.* arXiv:1605.00450 [math.CO].
- Cuthill, E., & McKee, J. (1969). *Reducing the bandwidth of sparse symmetric matrices.* Proceedings of the 24th National Conference ACM, 157–172.
- George, A., & Liu, J. W. H. (1979). *An implementation of a pseudoperipheral node finder.* ACM Transactions on Mathematical Software 5(3), 284–295.
- Papadimitriou, C. H. (1976). *The NP-completeness of the bandwidth minimization problem.* Computing 16(3), 263–270.
- Unger, W. (1998). *The complexity of the approximation of the bandwidth problem.* 39th IEEE FOCS, 82–91.
- Bodlaender, H. L. (1988). *Dynamic programming on graphs with bounded treewidth.* ICALP 1988.

Gebaut mit Streamlit, Plotly, NumPy und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Graphen und Netzwerke: BFS bis Cliquenbandbreite](https://sebastianhanisch.net/konzepte-graphen-netzwerke.html).
