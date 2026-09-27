"""Plotly-Figuren: 1 G(n,k,b) und seine Bandbreite (Ecken als Intervalle auf einer Zahlengeraden, Bandbreite-Balken), 2 Von der Hyperkante zur Clique (2-Sektionsgraph, schwacher
Kantenclique-Graph G~_H), 3 Cliquenueberdeckung im Vergleich (exakt/Greedy/DP, Aufwand der DP), 4 Asymptotik/Vermutung (Satz 1a exakt gegen Formel, Satz-1b-Verhaeltnis, Satz-2-Exploration -
DEUTLICH als offene Frage beschriftet). Alle Achsen fest (`fixedrange`), Referenzlinien mit `annotation=dict(bgcolor="white")` (Pflicht-Checkliste dieser Reihe)."""

import math

import plotly.graph_objects as go

TEAL, ORANGE, BLUE, RED, PURPLE, GREY, LIGHT, GREEN = "#2F6B65", "#f58518", "#4c78a8", "#e45756", "#7b3fbf", "#b7bec7", "#e8ebee", "#54a24b"


def circular_layout(n):
    if n <= 0:
        return []
    return [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)) for i in range(n)]


def _base_layout(fig, height=380, title=None):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30 if title else 10, b=10), showlegend=False, plot_bgcolor="white",
                       title=dict(text=title, x=0.01, font=dict(size=13)) if title else None)
    return fig


def _corners_trace(xs, ys, pad=0.4):
    return go.Scatter(x=[min(xs) - pad, max(xs) + pad], y=[min(ys) - pad, max(ys) + pad], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False)


# --- 1 · G(n,k,b) und seine Bandbreite ------------------------------------------------------------------------------------------------------------------


def build_gnkb_intervals(verts, perm, title):
    """Jede Ecke (ein k-Tupel) als waagerechter Balken von min(X) bis max(X), auf der y-Achse nach ihrer Position `perm` sortiert - benachbarte Ecken (im Sinn der Bandbreite) liegen bei einer
    guten Nummerierung nah beieinander UND haben ueberlappende Intervalle."""
    n = len(verts)
    fig = go.Figure()
    order = sorted(range(n), key=lambda i: perm[i])
    for row, i in enumerate(order):
        X = verts[i]
        fig.add_trace(go.Scatter(x=[X[0], X[-1]], y=[row, row], mode="lines", line=dict(color=TEAL, width=6),
                                  hovertext=f"{X}: Position {perm[i]}", hoverinfo="text", showlegend=False))
    fig.update_layout(height=max(220, 16 * n), margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="white", title=dict(text=title, x=0.02, font=dict(size=13)))
    fig.update_xaxes(title="Element der Grundmenge {0,...,n}", fixedrange=True, gridcolor=LIGHT)
    fig.update_yaxes(title="Position", fixedrange=True, autorange="reversed")
    return fig


def build_bandwidth_bars(values):
    """`values`: {label: Zahl oder None}."""
    labels = [k for k, v in values.items() if v is not None]
    ys = [values[k] for k in labels]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=ys, marker_color=[TEAL, ORANGE, BLUE, RED, PURPLE][: len(labels)], text=ys, textposition="outside"))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(title="Bandbreite", range=[0, max(ys) * 1.25 if ys else 1], autorange=False, fixedrange=True, gridcolor=LIGHT)
    return fig


# --- 2 · Von der Hyperkante zur Clique -------------------------------------------------------------------------------------------------------------------


def build_two_section_graph(universe_size, two_section_adj, hyperedges, positions=None):
    """2-Sektionsgraph: Ecken = Grundmenge, Kanten = 2-Sektions-Kanten (aus gemeinsamen Hyperkanten). `positions`, falls gegeben (Elektrodengitter), nutzt die echten Elektrodenzentren,
    sonst ein Kreislayout. Knoten-Hovertext zeigt, in welchen Hyperkanten die Ecke vorkommt."""
    if positions is not None:
        xy = [(float(positions[i][0]), float(positions[i][1])) for i in range(universe_size)]
    else:
        xy = circular_layout(universe_size)
    fig = go.Figure()
    ex, ey = [], []
    for u in range(universe_size):
        for v in two_section_adj[u]:
            if v > u:
                ex += [xy[u][0], xy[v][0], None]
                ey += [xy[u][1], xy[v][1], None]
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines", line=dict(color=GREY, width=1.2), hoverinfo="skip", showlegend=False))
    membership = [[j for j, e in enumerate(hyperedges) if u in e] for u in range(universe_size)]
    hover = [f"Ecke {u}: Hyperkanten {membership[u]}" for u in range(universe_size)]
    fig.add_trace(go.Scatter(x=[p[0] for p in xy], y=[p[1] for p in xy], mode="markers+text", text=[str(u) for u in range(universe_size)], textposition="top center",
                              marker=dict(size=14, color=TEAL, line=dict(color="white", width=1)), hovertext=hover, hoverinfo="text", showlegend=False))
    if xy:
        fig.add_trace(_corners_trace([p[0] for p in xy], [p[1] for p in xy]))
    fig.update_xaxes(visible=False, fixedrange=True, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, fixedrange=True)
    return _base_layout(fig, 380, "2-Sektionsgraph G_H (Ecken = Grundmenge)")


def build_weg_graph(weg_adj, hyperedges):
    """Der schwache Kantenclique-Graph G~_H: Ecken = Hyperkanten (als Tupel beschriftet), Kanten = `weg_adj`."""
    m = len(hyperedges)
    xy = circular_layout(m)
    fig = go.Figure()
    ex, ey = [], []
    for i in range(m):
        for j in weg_adj[i]:
            if j > i:
                ex += [xy[i][0], xy[j][0], None]
                ey += [xy[i][1], xy[j][1], None]
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines", line=dict(color=ORANGE, width=1.6), hoverinfo="skip", showlegend=False))
    labels = [str(e) for e in hyperedges]
    fig.add_trace(go.Scatter(x=[p[0] for p in xy], y=[p[1] for p in xy], mode="markers+text", text=[str(i) for i in range(m)], textposition="top center",
                              marker=dict(size=14, color=ORANGE, line=dict(color="white", width=1)), hovertext=labels, hoverinfo="text", showlegend=False))
    if xy:
        fig.add_trace(_corners_trace([p[0] for p in xy], [p[1] for p in xy]))
    fig.update_xaxes(visible=False, fixedrange=True, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, fixedrange=True)
    return _base_layout(fig, 380, "Schwacher Kantenclique-Graph G~_H (Ecken = Hyperkanten)")


# --- 3 · Cliquenueberdeckung im Vergleich ----------------------------------------------------------------------------------------------------------------


def build_cover_comparison_bars(exact, greedy, banded_dp):
    labels = ["Exakt", "Greedy", "Bandbreitenbeschränkte DP"]
    values = [exact, greedy, banded_dp]
    colors = [GREEN, BLUE, TEAL]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=values, marker_color=colors, text=values, textposition="outside"))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(title="Zahl der Cliquen (chi_e)", range=[0, max(values) * 1.3 if values else 1], autorange=False, fixedrange=True, gridcolor=LIGHT)
    return fig


def build_cover_quality_chart(rows):
    """Exakt/Greedy/DP ueber mehrere Hypergraph-Einstellungen (Messreihe 5) - je Instanz drei Balken nebeneinander."""
    labels = [f"u={r['universe']},k={r['k']},m={r['m']}" for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Exakt", x=labels, y=[r["exact"] for r in rows], marker_color=GREEN))
    fig.add_trace(go.Bar(name="Greedy", x=labels, y=[r["greedy"] for r in rows], marker_color=BLUE))
    fig.add_trace(go.Bar(name="Bandbreitenbeschränkte DP", x=labels, y=[r["banded_dp"] for r in rows], marker_color=TEAL))
    fig.update_layout(height=380, barmode="group", margin=dict(l=10, r=10, t=20, b=60), legend=dict(orientation="h", y=1.15), plot_bgcolor="white")
    fig.update_xaxes(fixedrange=True, tickangle=-30)
    fig.update_yaxes(title="chi_e", fixedrange=True, gridcolor=LIGHT)
    return fig


def build_dp_effort_chart(rows):
    """Aufwand (Elementarschritte) von Greedy gegen die bandbreitenbeschraenkte DP ueber die Bandbreite der benutzten Reihenfolge."""
    xs = [r["bandwidth_of_order"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[r["steps_greedy"] for r in rows], mode="markers", marker=dict(size=10, color=BLUE), name="Greedy"))
    fig.add_trace(go.Scatter(x=xs, y=[r["steps_banded_dp"] for r in rows], mode="markers", marker=dict(size=10, color=TEAL, symbol="x"), name="Bandbreitenbeschränkte DP"))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h", y=1.15), plot_bgcolor="white")
    fig.update_xaxes(title="Bandbreite der benutzten Reihenfolge", fixedrange=True)
    fig.update_yaxes(title="Elementarschritte", fixedrange=True, gridcolor=LIGHT)
    return fig


# --- 4 · Asymptotik/Vermutung -----------------------------------------------------------------------------------------------------------------------------


def build_satz1a_scatter(rows):
    """Satz-1a-Formel gegen `exact_bandwidth_layered` ueber alle bestaetigten (n,k,b)-Tripel - liegt auf der Diagonale, wenn Formel und exakte Suche uebereinstimmen (Korrektheits-Kette
    Punkt 3)."""
    xs = [r["formula"] for r in rows if r["exact"] is not None]
    ys = [r["exact"] for r in rows if r["exact"] is not None]
    top = max(xs + ys) * 1.08 if xs else 1
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, top], y=[0, top], mode="lines", line=dict(color=GREY, width=1.2, dash="dot"), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(size=8, color=TEAL, opacity=0.75), hoverinfo="skip", showlegend=False))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="white",
                       title=dict(text="Satz-1a-Formel gegen exakte Suche (eigener Nachbau, numerisch nachvollzogen)", x=0.02, font=dict(size=13)))
    fig.update_xaxes(title="Formel", range=[0, top], autorange=False, fixedrange=True)
    fig.update_yaxes(title="Exakt (Branch-and-Bound)", range=[0, top], autorange=False, fixedrange=True, gridcolor=LIGHT)
    return fig


def build_satz1b_chart(rows):
    """Gemessenes B(n,k,b)/[k*C(b,k)] ueber wachsendes n, je b eine Kurve - naehert sich 1, je groesser n bei festem (kleinem) b wird (Satz 1b, b=o(n)); EIGENER NACHBAU, kein Gueltigkeitstest."""
    fig = go.Figure()
    bs = sorted(set(r["b"] for r in rows))
    colors = [TEAL, ORANGE, BLUE, RED, PURPLE]
    for i, b in enumerate(bs):
        sub = [r for r in rows if r["b"] == b]
        fig.add_trace(go.Scatter(x=[r["n"] for r in sub], y=[r["ratio"] for r in sub], mode="lines+markers", line=dict(color=colors[i % len(colors)], width=2),
                                  marker=dict(size=7), name=f"b={b}"))
    fig.add_hline(y=1.0, line=dict(color=GREY, width=1.2, dash="dot"), annotation_text="Verhältnis 1 (asymptotisch)", annotation_position="bottom right",
                  annotation=dict(bgcolor="white"))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h", y=1.15), plot_bgcolor="white")
    fig.update_xaxes(title="n", fixedrange=True)
    fig.update_yaxes(title="B(n,k,b) / [k·C(b,k)]", fixedrange=True, gridcolor=LIGHT)
    return fig


def build_satz2_chart(rows, beta):
    """Heuristik-Obergrenze (skaliert durch n^k) gegen die c1/c2/c3-Referenzwerte fuer EIN beta ueber wachsendes n - DEUTLICH als Exploration mit endlichem n beschriftet, KEINE Entscheidung der
    offenen Vermutung."""
    sub = [r for r in rows if r["beta"] == beta]
    ns = [r["n"] for r in sub]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[r["measured_scaled"] for r in sub], mode="lines+markers", line=dict(color=TEAL, width=2.4), marker=dict(size=8),
                              name="Heuristik-Obergrenze (gemessen)/n^k"))
    if sub:
        fig.add_hline(y=sub[0]["c1"], line=dict(color=BLUE, width=1.4, dash="dash"), annotation_text="c1", annotation_position="top left", annotation=dict(bgcolor="white"))
        fig.add_hline(y=sub[0]["upper_ref"], line=dict(color=RED, width=1.4, dash="dash"), annotation_text="c2+c3 (Obergrenze)", annotation_position="bottom left",
                      annotation=dict(bgcolor="white"))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=1.18), plot_bgcolor="white",
                       title=dict(text=f"NUR Exploration (beta={beta}, endliches n) - entscheidet die offene Vermutung NICHT", x=0.02, font=dict(size=12, color=RED)))
    fig.update_xaxes(title="n", fixedrange=True)
    fig.update_yaxes(title="Wert / n^k", fixedrange=True, gridcolor=LIGHT)
    return fig
