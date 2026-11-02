"""PDF-Export der aktuellen Aufgabe mit den Rechenwegen und den ersten Werten (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

from sbf_evaluation import Analysis, verdict_answers, way_rows

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "ⁿ": "^n", "²": "^2", "ₖ": "k", "∞": "unendlich",
            "⁻": "-", "⁰": "0", "¹": "1", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "ₙ": "n"}


def _s(text) -> str:
    out = str(text)
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Siebformel: alles minus Verbotenes"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    s = a.settings
    if s.task == "Zuordnung":
        what = f"Zuordnung, {s.board}, {a.n_eff} x {a.n_eff}" + (f", Anteil verbotener Felder {s.share} %, Seed {s.seed}" if s.board == "Zufallsbrett" else "")
    else:
        what = f"Rundreise, {a.n_eff} Städte, Anteil vorhandener Kanten {s.share} %, Kosten 1 bis {s.r}, Seed {s.seed}"
    pdf.multi_cell(0, 5, _s(f"{what}. Alles gerechnet, keine Messdaten."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 5, _s(verdict_answers(a)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    widths = (30, 70, 40, 25, 25)
    heads = ("Frage", "Weg", "Ergebnis", "Schritte", "Prüfung")
    keys = ("Frage", "Weg", "Ergebnis", "Schritte", "Prüfung")
    for h, w in zip(heads, widths):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    for row in way_rows(a):
        for key, w in zip(keys, widths):
            pdf.cell(w, 5.5, _s(row[key])[:38], border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: siebformel-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
