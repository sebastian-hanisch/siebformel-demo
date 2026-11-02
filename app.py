"""Siebformel – alles zählen, das Verbotene abziehen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 7 der Reihe „Abzählen und erzeugende Funktionen“: Die Siebformel (Inklusion–Exklusion) für Zuordnungen mit verbotenen Feldern (Turmzahlen, Ménage-Zahlen, Ryser), Hamiltonkreise über Spaziergänge
und TSP mit Polynomgewichten; gegen Held–Karp (Stück 4) und Aufzählen geprüft; das Sieb spart Speicher, nicht Zeit, und braucht ganze Zahlen.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sbf_constants as C
from sbf_evaluation import (
    Settings,
    analyse,
    big_text,
    de,
    float_check,
    float_rows,
    hk_check,
    hk_rows,
    legendre_play,
    machines_play,
    menage_check,
    menage_rows,
    sci_text,
    share_of_all,
    share_text,
    terms_rows,
    time_experiment,
    tsp_experiment,
    verdict_answers,
    verdict_float,
    verdict_hk,
    verdict_legendre,
    verdict_machines,
    verdict_menage,
    verdict_terms,
    verdict_time,
    verdict_tsp,
    way_rows,
)
from sbf_layout import dunkles_design, kopf_css
from sbf_pdf_export import build_pdf
from sbf_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from sbf_visualization import build_cost_distribution, build_float, build_hk, build_rook, build_terms

st.set_page_config(page_title="Siebformel – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _terms():
    return terms_rows()


@st.cache_data(show_spinner=False)
def _menage():
    rows = menage_rows()
    return rows, menage_check(rows)


@st.cache_data(show_spinner=False)
def _hk():
    rows = hk_rows()
    return rows, hk_check(rows)


@st.cache_data(show_spinner=False)
def _tsp(seed):
    return tsp_experiment(seed)


@st.cache_data(show_spinner=False)
def _float():
    rows = float_rows()
    return rows, float_check(rows)


@st.cache_data(show_spinner=False)
def _legendre(limit, divisors):
    return legendre_play(limit, divisors)


@st.cache_data(show_spinner=False)
def _machines(n, k):
    return machines_play(n, k)


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sbf_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("➖ Siebformel – alles zählen, das Verbotene abziehen")
st.markdown(
    """
**Der umgekehrte Weg.** Stück 3 bis 6 haben Strukturen **aufgebaut**. Bei **Verboten** ist es oft einfacher, erst **alles** zu zählen und dann das Verbotene abzuziehen: Die Zahl der Objekte ohne eine von $k$ Eigenschaften ist
$\\sum_{S} (-1)^{|S|}\\, N(S)$ über alle Teilmengen $S$ der Eigenschaften, mit $N(S)$ = Zahl der Objekte, die mindestens die Eigenschaften in $S$ haben (**Inklusion–Exklusion**).
Die Summanden wachsen mit $2^k$; die Struktur kürzt sie: bei Zuordnungen mit verbotenen Feldern auf wenige **Turmzahlen**, bei Hamiltonkreisen auf Spaziergänge in Teilmengen der Städte.
Das Sieb braucht **ganze Zahlen**: die Summanden sind riesig und löschen sich fast aus.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Siebformel", expanded=True):
    st.markdown(
        """
1. **Zuordnung mit verbotenen Feldern:** $n$ Aufgaben auf $n$ Maschinen, einige Paare verboten. Wer eine Menge $S$ nichtangreifender verbotener Paare erzwingt, hat noch $(n-|S|)!$ Zuordnungen; die Zahl der Mengen mit $k$ Paaren ist die **Turmzahl** $r_k$. Ergebnis: $\\sum_k (-1)^k\\, r_k\\, (n-k)!$.
2. **Hamiltonkreis:** Zähle geschlossene **Spaziergänge** der Länge $n$ von Stadt 0, die nur Städte aus einer Teilmenge $S$ benutzen (leicht: Vektor mal Matrix). Ein Spaziergang, der alle $n$ Städte besucht, ist ein Hamiltonkreis. Sieb über $S$: $\\sum_S (-1)^{n-|S|}\\, W(S)$.
3. **TSP:** Jede Kante bekommt das Gewicht $z^{\\text{Kosten}}$; der Koeffizient von $z^w$ zählt die Hamiltonkreise mit Kosten $w$.
4. **Gegenproben:** Aufzählen, die Teilmengen-DP (Held–Karp aus Stück 4, Permanente) und Formeln; das Sieb muss denselben Wert liefern.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Aufgabe**")
    task = st.selectbox("Aufgabe", list(C.TASKS), key="task_select", help="Zuordnung: Aufgaben auf Maschinen mit verbotenen Paaren. Rundreise: Hamiltonkreise und kleinste Kosten in einem gerichteten Graphen (Start in Stadt 0).")
    board = st.selectbox("Brett (nur Zuordnung)", list(C.BOARDS), key="board_select", help="Welche Paare verboten sind: zufällig, die Hauptdiagonale (Derangements), Diagonale plus Nebendiagonale (Ménage), keines oder alle.")
    n = st.slider("Größe n", *bounds("n_slider"), key="n_slider", help=f"Aufgaben und Maschinen beziehungsweise Städte (die Rundreise hat höchstens {C.TOUR_N_MAX}).")
    share = st.slider("Anteil in %", *bounds("share_slider"), key="share_slider", help="Zufallsbrett: Anteil verbotener Felder. Rundreise: Anteil vorhandener Kanten.")
    r = st.slider("Kostenbereich r (Rundreise)", *bounds("r_slider"), key="r_slider", help=f"Kosten liegen zwischen 1 und r (höchstens {C.R_MAX}; das Kostenpolynom hat Grad n·r).")
    seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)

sync_query_params({"task_select": task, "board_select": board, "n_slider": int(n), "share_slider": int(share), "r_slider": int(r), "seed_input": int(seed)})

settings = Settings(task, board, int(n), int(share), int(r), int(seed))
a = _analysis(settings)
for note in a.notes:
    st.info(note)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
info = a.info
m1, m2, m3, m4 = st.columns(4)
if task == "Zuordnung":
    m1.metric("Zuordnungen ohne verbotenes Feld", big_text(info["value"]), help="Permutationen, die kein verbotenes Feld treffen: die Permanente der erlaubten Felder.")
    m2.metric("Anteil an allen Zuordnungen", share_text(share_of_all(a)), help="Anteil an allen n! Permutationen.")
    m3.metric("Teilmengen verbotener Felder", big_text(info["subsets"]), help="2^|F|: so viele Summanden hätte das Sieb über alle Teilmengen verbotener Felder.")
    m4.metric("Summanden mit Turmzahlen", str(info["nonzero"]), help="Turmzahlen ungleich 0: so viele Summanden bleiben nach dem Kürzen.")
    st.plotly_chart(build_rook(info["rook"]), width="stretch", key="main_chart")
    st.caption("Die Turmzahlen r_k (Zehnerlogarithmus): so viele Möglichkeiten gibt es, k nicht schlagende Türme auf verbotene Felder zu stellen. Nur diese Summanden bleiben im Sieb.")
else:
    best = info["best"]
    m1.metric("Hamiltonkreise", big_text(info["cycles"]), help="Gerichtete Rundreisen ab Stadt 0 über alle Städte.")
    m2.metric("Kleinste Kosten", str(best[0]) if best[1] else "–", help="Kosten des billigsten Hamiltonkreises; – wenn es keinen gibt.")
    m3.metric("Zahl der billigsten", big_text(best[1]), help="Wie viele Hamiltonkreise die kleinsten Kosten erreichen.")
    m4.metric("Teilmengen im Sieb", big_text(info["subsets"]), help="2^(n−1): so viele Teilmengen der Städte durchläuft das Sieb.")
    st.plotly_chart(build_cost_distribution(info["poly"]), width="stretch", key="main_chart")
    st.caption("Zahl der Hamiltonkreise je Gesamtkosten: die Koeffizienten des Kostenpolynoms aus dem Sieb.")

with st.expander("Die Instanz ansehen"):
    if task == "Zuordnung":
        n_eff = a.n_eff
        forbidden = info["forbidden"]
        st.dataframe([{"Aufgabe": i + 1, **{f"M{j + 1}": ("verboten" if (i, j) in forbidden else "erlaubt") for j in range(n_eff)}} for i in range(n_eff)], hide_index=True, width="stretch")
        st.caption(f"{info['cells']} verbotene Paare von {n_eff * n_eff}.")
    else:
        st.dataframe([{"von \\ nach": i + 1, **{str(j + 1): ("–" if c is None else c) for j, c in enumerate(row)}} for i, row in enumerate(info["cost"])], hide_index=True, width="stretch")
        st.caption(f"Kosten der gerichteten Verbindungen; – heißt: keine Verbindung ({info['arcs']} von {a.n_eff * (a.n_eff - 1)} Kanten vorhanden).")

if st.button("📄 PDF der aktuellen Aufgabe erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="siebformel.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wann ist „alles minus Verbotenes“ besser als „aufbauen“?")
verdict(verdict_answers(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Dieselben Zahlen auf allen Wegen")
st.caption(f"Die eingestellte Aufgabe auf allen Wegen, die für sie gelten: das Sieb in seinen Fassungen, die Teilmengen-DP (Permanente beziehungsweise Held–Karp, Stück 4), Formeln und Aufzählen "
           f"(Zuordnung bis n = {C.ENUM_ASSIGN_N}, Rundreise bis n = {C.ENUM_TOUR_N}). Das Sieb über Feldmengen läuft nur bis {C.FIELD_SIEVE_MAX} verbotene Felder.")
if a.problems:
    st.error("Die Rechenwege widersprechen sich: " + "; ".join(a.problems))
else:
    st.success("Alle gerechneten Wege geben je Frage dieselbe Zahl.")
st.dataframe(way_rows(a), hide_index=True, width="stretch")

st.markdown("---")

st.subheader("🔬 Experiment 2: Die Summanden schrumpfen")
st.caption("Das Sieb über alle Teilmengen verbotener Felder hat 2^|F| Summanden; nur die nichtangreifenden Mengen tragen bei, und die Turmzahlen fassen sie nach der Zahl k der Türme zusammen. Darunter die Ménage-Zahlen (Diagonale plus Nebendiagonale).")
terms = _terms()
st.plotly_chart(build_terms(terms), width="stretch", key="terms_chart")
st.dataframe([{**r, "Teilmengen 2^|F|": big_text(r["Teilmengen 2^|F|"]), "nichtangreifend": big_text(r["nichtangreifend"]), "Zuordnungen": big_text(r["Zuordnungen"])} for r in terms], hide_index=True, width="stretch")
verdict(verdict_terms(terms))
menage, menage_problems = _menage()
st.dataframe([{"n": r["n"], "Ménage-Zahl (Sieb mit Turmzahlen)": big_text(r["Ménage-Zahl (Sieb mit Turmzahlen)"]), "Formel der Turmzahlen": big_text(r["Formel der Turmzahlen"]),
               "Aufzählen": "–" if r["Aufzählen"] is None else big_text(r["Aufzählen"]), "Turmzahlen ungleich 0": r["Turmzahlen ungleich 0"]} for r in menage], hide_index=True, width="stretch")
verdict(verdict_menage(menage, menage_problems))

st.markdown("---")

st.subheader("🔬 Experiment 3: Sieb gegen Held–Karp")
st.caption("Hamiltonkreise im vollständigen Digraphen: das Sieb über Spaziergänge gegen den Held–Karp-Zähler aus Stück 4, exakt gezählte Schritte und gespeicherte Zahlen. Die Zeit messen Sie auf Klick; sie ist eine Messung dieses Rechners.")
hk, hk_problems = _hk()
st.plotly_chart(build_hk(hk), width="stretch", key="hk_chart")
st.dataframe([{"n": r["n"], "Hamiltonkreise": big_text(r["Hamiltonkreise"]), "Teilmengen im Sieb": big_text(r["Teilmengen im Sieb"]), "Rechenschritte Sieb": big_text(r["Rechenschritte Sieb"]),
               "gespeicherte Zahlen Sieb": r["gespeicherte Zahlen Sieb"], "Zustände Held–Karp": big_text(r["Zustände Held–Karp"]), "Übergänge Held–Karp": big_text(r["Übergänge Held–Karp"]),
               "Schritte Sieb : Held–Karp": de(r["Schritte Sieb : Held–Karp"], 1)} for r in hk], hide_index=True, width="stretch")
verdict(verdict_hk(hk, hk_problems))
if st.button("⏱️ Zeit messen", key="time_run"):
    st.session_state["time_res"] = time_experiment()
timing = st.session_state.get("time_res")
if timing:
    st.dataframe([{"n": r["n"], "Sieb (Sekunden)": de(r["Sieb (Sekunden)"], 3), "Held–Karp (Sekunden)": de(r["Held–Karp (Sekunden)"], 3)} for r in timing], hide_index=True, width="stretch")
    verdict(verdict_time(timing))

st.markdown("---")

st.subheader("🔬 Experiment 4: TSP mit Polynomgewichten")
st.caption(f"{C.TSP_N} Städte, alle Kanten, Kosten 1 bis {C.TSP_R} (der Seed kommt aus der Seitenleiste). Jede Kante trägt das Gewicht z^Kosten; das Sieb liefert die Zahl der Hamiltonkreise je Gesamtkosten, "
           "Held–Karp mit einem Paar aus Kosten und Zahl der besten (Stück 4) und Aufzählen dienen als Gegenprobe.")
tsp = _tsp(int(seed))
st.plotly_chart(build_cost_distribution(tsp["poly"]), width="stretch", key="tsp_chart")
st.dataframe([{"Weg": "Sieb mit Polynomgewichten", "Kleinste Kosten und Zahl der besten": f"{tsp['best'][0]}, {big_text(tsp['best'][1])} Mal", "Rechenschritte": big_text(tsp["ops"])},
              {"Weg": "Held–Karp (Paar-Semiring)", "Kleinste Kosten und Zahl der besten": f"{tsp['hk'][0]}, {big_text(tsp['hk'][1])} Mal", "Rechenschritte": "–"},
              {"Weg": "Aufzählen aller Reihenfolgen", "Kleinste Kosten und Zahl der besten": f"{tsp['brute'][0]}, {big_text(tsp['brute'][1])} Mal", "Rechenschritte": big_text(tsp["brute_steps"])}], hide_index=True, width="stretch")
verdict(verdict_tsp(tsp))

st.markdown("---")

st.subheader("🔬 Experiment 5: Exakt rechnen")
st.caption("Surjektionen von k auf k Maschinen (Ergebnis k!) über das Sieb Σ(−1)^(k−j)·C(k,j)·j^k, einmal mit ganzen Zahlen und einmal in Gleitkomma. Die größten Summanden sind viel größer als das Ergebnis und löschen sich fast aus.")
flt, flt_problems = _float()
st.plotly_chart(build_float(flt), width="stretch", key="float_chart")
st.dataframe([{"k = n": r["k = n"], "exakt (k!)": big_text(r["exakt (k!)"]), "Gleitkomma": sci_text(r["Gleitkomma"]), "relative Abweichung": sci_text(r["relative Abweichung"]), "größter Summand": sci_text(r["größter Summand"])} for r in flt],
             hide_index=True, width="stretch")
verdict(verdict_float(flt, flt_problems))

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: Zahlen ohne Teiler und Aufgaben ohne leere Maschine")
st.caption("Zwei kleine Siebe zum Ausprobieren: wie viele Zahlen bis N durch keinen gewählten Teiler teilbar sind (Legendre), und wie viele Zuordnungen von n Aufgaben auf k Maschinen keine Maschine leer lassen.")
p1, p2 = st.columns(2)
play_limit = p1.slider("Zahlen von 1 bis N", C.PLAY_LIMIT_MIN, C.PLAY_LIMIT_MAX, C.PLAY_LIMIT_DEFAULT, key="play_limit", help="Obergrenze der gezählten Zahlen.")
play_div = p2.multiselect("Teiler", list(C.PLAY_DIVISORS), default=list(C.PLAY_DIVISORS_DEFAULT), key="play_divisors", help="Gezählt werden die Zahlen, die durch keinen dieser Teiler teilbar sind.")
leg = _legendre(int(play_limit), tuple(play_div) or (2,))
verdict(verdict_legendre(leg))
q1, q2 = st.columns(2)
play_n = q1.slider("Aufgaben n", 1, C.PLAY_MAX, 10, key="play_n", help="Zahl der Aufgaben.")
play_k = q2.slider("Maschinen k", 1, C.PLAY_MAX, 3, key="play_k", help="Zahl der Maschinen.")
mach = _machines(int(play_n), int(play_k))
verdict(verdict_machines(mach))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Verbote sind Eigenschaften, deren Schnitt man zählen kann** | Bei Zuordnungen kann man „mindestens diese Paare“ zählen (die Fakultät der übrigen Zeilen, wenn die Paare nichtangreifend sind); bei Verboten ohne so einfache Zählung (zum Beispiel Nachbarschaften in einem Graphen) wird jeder Summand selbst schwer. | – |
| **Die Summanden werden exakt addiert** | In Gleitkomma löscht sich das Sieb aus: Abweichung bis 2,8·10⁴ bei k = 40 (Experiment 5). Die App rechnet mit ganzen Zahlen. | – |
| **Das Sieb ist schneller als Aufbauen** | Nicht bei Hamiltonkreisen: das Sieb braucht etwa das Dreizehnfache an Rechenschritten bei n = 10 (Experiment 3) und spart nur Speicher. | Stück 4: Held–Karp |
| **Kosten sind kleine ganze Zahlen** | Das Kostenpolynom hat Grad n·r; die App begrenzt r auf {C.R_MAX} und n auf {C.TOUR_N_MAX}. Größere Kosten brauchen eine andere Rechnung. | – |
| **Nur gerichtete Kreise ab Stadt 0** | Ein ungerichteter Kreis zählt in beide Richtungen doppelt; Björklunds Verfahren für ungerichtete Hamiltonkreise ist nicht Teil der Demo. | Ausblick |
| **Die Teilmengen passen in die Rechenzeit** | Das Sieb über Spaziergänge hat 2^(n−1) Teilmengen (n ≤ {C.TOUR_N_MAX}), das Sieb über Feldmengen 2^|F| (nur bis {C.FIELD_SIEVE_MAX} Felder). | Stück 13: Entscheidungsdiagramme |
| **Zuordnungen nur zählen** | Die Permanente ist #P-schwer; das Ryser-Sieb hat 2ⁿ−1 Summanden, ist also bis n = {C.N_MAX} ohne Mühe, aber nicht allgemein schnell. | Komplexitätslinie |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Siebformel.** Seien $A_1, \dots, A_k$ Eigenschaften von Objekten einer Menge $U$ und $N(S)$ die Zahl der Objekte mit allen Eigenschaften $A_i$, $i \in S$. Die Zahl der Objekte ohne jede Eigenschaft ist
$$\sum_{S \subseteq \{1, \dots, k\}} (-1)^{|S|}\, N(S).$$

**Zuordnungen mit verbotenen Feldern.** Für eine Menge $S$ verbotener Felder gilt $N(S) = (n - |S|)!$, wenn die Felder in verschiedenen Zeilen und Spalten liegen (nichtangreifend), sonst $0$. Mit den Turmzahlen $r_k$ (Zahl der nichtangreifenden $k$-Mengen) ist die Zahl der Zuordnungen
$$\sum_{k=0}^{n} (-1)^k\, r_k\, (n-k)!.$$
Hauptdiagonale: $r_k = \binom{n}{k}$, also $D_n = \sum_k (-1)^k \binom{n}{k} (n-k)!$. Ménage-Brett (Diagonale plus Nebendiagonale, zyklisch): $r_k = \frac{2n}{2n-k}\binom{2n-k}{k}$.

**Ryser.** Für eine 0/1-Matrix $A$ ist die Zahl der Zuordnungen $\operatorname{perm}(A) = \sum_{S \subseteq \{1, \dots, n\}} (-1)^{n-|S|} \prod_{i=1}^{n} \sum_{j \in S} a_{ij}$, also $2^n - 1$ Summanden statt $n!$ Permutationen.

**Hamiltonkreise.** Sei $W(S)$ die Zahl der geschlossenen Spaziergänge der Länge $n$ von der Stadt $0$, die nur Städte aus $S \cup \{0\}$ benutzen. Dann ist die Zahl der Hamiltonkreise
$$\sum_{S \subseteq V \setminus \{0\}} (-1)^{n-1-|S|}\, W(S).$$
Jede $W(S)$ ist das Element $(0,0)$ von $A_S^n$ ($A_S$ die Nachbarschaftsmatrix auf $S \cup \{0\}$); gerechnet wird mit einem Vektor, also mit $n$ gespeicherten Zahlen.

**TSP.** Jede Kante $(i, j)$ erhält das Gewicht $z^{c_{ij}}$. Das Sieb liefert dann $\sum_w h_w z^w$ mit $h_w$ = Zahl der Hamiltonkreise mit Kosten $w$; die kleinsten Kosten sind der kleinste Exponent mit $h_w > 0$, die Zahl der besten Kreise ist $h_w$ dort.

**Surjektionen.** $k!\,S(n,k) = \sum_{j=0}^{k} (-1)^{k-j} \binom{k}{j}\, j^n$ (k + 1 Summanden). **Legendre.** Zahlen bis $N$ ohne Teiler $d_1, \dots, d_m$: $\sum_{S} (-1)^{|S|} \lfloor N / \operatorname{kgV}(S) \rfloor$.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
H. J. Ryser: *Combinatorial Mathematics*, Carus Mathematical Monographs 14, 1963 (Permanente als Sieb).
J. Riordan: *An Introduction to Combinatorial Analysis*, Wiley, 1958 (Turmpolynome, Ménage-Zahlen).
R. M. Karp: *Dynamic programming meets the principle of inclusion and exclusion*, Operations Research Letters 1 (2), 1982, S. 49–51 (Sieb statt Teilmengen-DP).
A. Björklund: *Determinant sums for undirected Hamiltonicity*, FOCS 2010 (Ausblick, nicht Teil der Demo).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
