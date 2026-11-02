"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import sbf_algorithm as A
import sbf_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_rook(r: list[int]):
    """Turmzahlen r_k: die Summanden, die nach dem Kürzen übrig bleiben (logarithmische Achse, weil sie stark wachsen)."""
    ks = [k for k, x in enumerate(r) if x]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ks, y=[A.log10_int(r[k]) for k in ks], name="Turmzahl r_k", marker_color=C.COLOR_MAIN))
    fig.update_xaxes(title_text="Zahl k der Türme", dtick=1)
    fig.update_yaxes(title_text="Turmzahl (Zehnerlogarithmus)")
    return _base(fig, 320)


def build_cost_distribution(poly: list[int], title: str = "Zahl der Hamiltonkreise"):
    """Zahl der Hamiltonkreise je Gesamtkosten (Koeffizienten des Kostenpolynoms)."""
    xs = [w for w, c in enumerate(poly) if c]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=xs, y=[poly[w] for w in xs], name=title, marker_color=C.COLOR_MAIN))
    fig.update_xaxes(title_text="Gesamtkosten des Kreises")
    fig.update_yaxes(title_text="Zahl der Hamiltonkreise")
    return _base(fig, 320)


def build_terms(rows: list[dict]):
    """Teilmengen verbotener Felder, nichtangreifende Teilmengen und Turmzahlen ungleich 0 (Zehnerlogarithmus)."""
    fig = go.Figure()
    names = [f"{r['Brett']}" for r in rows]
    fig.add_trace(go.Bar(x=names, y=[A.log10_int(r["Teilmengen 2^|F|"]) for r in rows], name="alle Teilmengen 2^|F|", marker_color=C.COLOR_ALL))
    fig.add_trace(go.Bar(x=names, y=[A.log10_int(r["nichtangreifend"]) for r in rows], name="nichtangreifend", marker_color=C.COLOR_LINE))
    fig.add_trace(go.Bar(x=names, y=[A.log10_int(r["Turmzahlen ungleich 0"]) for r in rows], name="Turmzahlen ungleich 0", marker_color=C.COLOR_MAIN))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Summanden (Zehnerlogarithmus)")
    return _base(fig, 360)


def build_hk(rows: list[dict]):
    """Rechenschritte des Siebs gegen Übergänge von Held–Karp, und gespeicherte Zahlen (Zehnerlogarithmus)."""
    fig = go.Figure()
    names = [str(r["n"]) for r in rows]
    fig.add_trace(go.Bar(x=names, y=[A.log10_int(r["Rechenschritte Sieb"]) for r in rows], name="Rechenschritte Sieb", marker_color=C.COLOR_LINE))
    fig.add_trace(go.Bar(x=names, y=[A.log10_int(r["Übergänge Held–Karp"]) for r in rows], name="Übergänge Held–Karp", marker_color=C.COLOR_MAIN))
    fig.add_trace(go.Bar(x=names, y=[A.log10_int(r["gespeicherte Zahlen Sieb"]) for r in rows], name="gespeicherte Zahlen Sieb", marker_color=C.COLOR_ALL))
    fig.add_trace(go.Bar(x=names, y=[A.log10_int(r["Zustände Held–Karp"]) for r in rows], name="gespeicherte Zustände Held–Karp", marker_color=C.COLOR_WARN))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Städte n")
    fig.update_yaxes(title_text="Anzahl (Zehnerlogarithmus)")
    return _base(fig, 360)


def build_float(rows: list[dict]):
    """Relative Abweichung des Gleitkomma-Siebs je k (Zehnerlogarithmus, 0 wird als 10^-17 gezeichnet)."""
    import math

    fig = go.Figure()
    ks = [r["k = n"] for r in rows]
    fig.add_trace(go.Scatter(x=ks, y=[math.log10(max(r["relative Abweichung"], 1e-17)) for r in rows], mode="lines+markers", name="relative Abweichung", line=dict(color=C.COLOR_WARN)))
    fig.add_hline(y=0, line=dict(color=C.COLOR_ALL, dash="dash"))
    fig.update_xaxes(title_text="k = n", dtick=5)
    fig.update_yaxes(title_text="relative Abweichung (Zehnerlogarithmus)")
    return _base(fig, 320)
