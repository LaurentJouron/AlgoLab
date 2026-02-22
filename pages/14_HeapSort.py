import streamlit as st
import plotly.graph_objects as go
import random, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Heap Sort — Graphix", page_icon="🌲", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithme ────────────────────────────────────────────────────────────────

def heap_sort_steps(arr):
    a = arr.copy()
    n = len(a)
    steps = []

    def record(phase, heap_end, active=None, desc=""):
        steps.append({"arr": a.copy(), "heap_end": heap_end,
                      "active": active or [], "phase": phase, "desc": desc})

    def heapify(n_heap, i):
        largest, left, right = i, 2*i+1, 2*i+2
        if left  < n_heap and a[left]  > a[largest]: largest = left
        if right < n_heap and a[right] > a[largest]: largest = right
        if largest != i:
            record("build", n_heap, [i, largest],
                   f"Sift-down : échange <b>{a[i]}</b> ↔ <b>{a[largest]}</b> — parent trop petit")
            a[i], a[largest] = a[largest], a[i]
            heapify(n_heap, largest)

    record("build", n, [], "Tableau initial — on va construire le max-heap")
    for i in range(n//2 - 1, -1, -1):
        heapify(n, i)
        record("build", n, [i], f"Heapify à l'index {i} — racine actuelle = <b>{a[0]}</b>")

    record("build", n, [0], f"✅ Max-heap construit — la racine <b>{a[0]}</b> est le plus grand élément")

    for i in range(n-1, 0, -1):
        record("extract", i+1, [0, i],
               f"Extraction : <b>{a[0]}</b> (max) échangé avec la position {i}")
        a[0], a[i] = a[i], a[0]
        heapify(i, 0)
        if i > 1:
            record("extract", i, [0], f"Sift-down — tas réduit à {i} éléments, nouvelle racine = <b>{a[0]}</b>")

    record("done", 0, list(range(n)), "✅ Tableau entièrement trié !")
    return steps

# ── Visualisation arbre ───────────────────────────────────────────────────────

def make_tree_traces(arr, heap_end, active):
    n = min(heap_end, len(arr), 15)
    if n == 0:
        return [go.Scatter(x=[None], y=[None], mode='markers', showlegend=False)]

    pos = {}
    def place(i, x, y, spread):
        if i >= n: return
        pos[i] = (x, y)
        if 2*i+1 < n: place(2*i+1, x - spread, y - 1.8, spread * 0.55)
        if 2*i+2 < n: place(2*i+2, x + spread, y - 1.8, spread * 0.55)
    place(0, 0, 0, 4.0)

    traces = []
    for i in pos:
        for child in [2*i+1, 2*i+2]:
            if child in pos:
                x0,y0 = pos[i]; x1,y1 = pos[child]
                traces.append(go.Scatter(x=[x0,x1,None], y=[y0,y1,None], mode='lines',
                                         line=dict(color='#334155', width=1.5),
                                         hoverinfo='none', showlegend=False))

    nodes = sorted(pos.keys())
    nx = [pos[i][0] for i in nodes]
    ny = [pos[i][1] for i in nodes]
    nc = ["#f59e0b" if i in active else "#7c3aed" for i in nodes]
    ns = [32 if i in active else 26 for i in nodes]
    nt = [str(arr[i]) for i in nodes]

    traces.append(go.Scatter(x=nx, y=ny, mode='markers+text',
                             marker=dict(size=ns, color=nc, line=dict(color='#0a0a0f', width=2)),
                             text=nt, textposition='middle center',
                             textfont=dict(size=10, color='white', family='Space Mono'),
                             hoverinfo='none', showlegend=False))
    return traces

# ── Figure animée ─────────────────────────────────────────────────────────────

def make_animated_fig(steps):
    def bar_colors(s):
        colors = []
        for i in range(len(s["arr"])):
            if s["phase"] == "done":       colors.append("#10b981")
            elif i in s["active"]:         colors.append("#f59e0b")
            elif i < s["heap_end"]:        colors.append("#7c3aed")
            else:                          colors.append("#10b981")
        return colors

    def make_traces(s):
        return [go.Bar(x=list(range(len(s["arr"]))), y=s["arr"],
                       marker=dict(color=bar_colors(s), line=dict(color='#0a0a0f', width=1)),
                       text=s["arr"], textposition='outside',
                       textfont=dict(size=10, color='#e2e8f0', family='Space Mono'),
                       showlegend=False)]

    s0 = steps[0]
    fig = go.Figure(
        data=make_traces(s0),
        layout=go.Layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            font=dict(color='#e2e8f0', family='DM Sans'),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor='#1e1e2e', zeroline=False),
            margin=dict(l=20, r=20, t=60, b=90), height=370, bargap=0.12,
            annotations=[dict(x=0.5, y=1.10, xref='paper', yref='paper', text=s0["desc"],
                              showarrow=False, font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')],
            updatemenus=[dict(type="buttons", showactive=False, y=-0.25, x=0.5, xanchor="center",
                buttons=[
                    dict(label="▶  Démarrer", method="animate",
                         args=[None, dict(frame=dict(duration=600, redraw=True),
                                         transition=dict(duration=200, easing="cubic-in-out"),
                                         fromcurrent=True, mode="immediate")]),
                    dict(label="⏸  Pause", method="animate",
                         args=[[None], dict(frame=dict(duration=0, redraw=False),
                                            mode="immediate", transition=dict(duration=0))]),
                ],
                font=dict(color="#e2e8f0", family="Space Mono", size=12),
                bgcolor="#1e1e2e", bordercolor="#334155")],
            sliders=[dict(active=0,
                currentvalue=dict(prefix="Étape : ", font=dict(color="#94a3b8", family="Space Mono", size=11),
                                  visible=True, xanchor="center"),
                pad=dict(t=50, b=5), len=0.9, x=0.05,
                bgcolor="#111118", bordercolor="#1e1e2e", tickcolor="#334155",
                font=dict(color="#64748b", size=9),
                steps=[dict(method="animate",
                            args=[[f"hs{k}"], dict(mode="immediate", frame=dict(duration=600, redraw=True),
                                                   transition=dict(duration=200))],
                            label=str(k)) for k in range(len(steps))])],
        ),
        frames=[go.Frame(name=f"hs{k}", data=make_traces(s),
                         layout=go.Layout(annotations=[dict(x=0.5, y=1.10, xref='paper', yref='paper',
                                                            text=s["desc"], showarrow=False,
                                                            font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')]))
                for k, s in enumerate(steps)],
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);color:#a78bfa;">🌲 HEAP SORT</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Tri par Tas (Heap Sort)</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Deux phases : <b>Phase 1</b> — construire un max-heap (arbre où chaque parent ≥ ses enfants). <b>Phase 2</b> — extraire le maximum (racine) et le placer à la fin, puis reconstruire le heap. Résultat : tableau trié en O(n log n) garanti.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    n_size = st.slider("Taille du tableau", 6, 16, 10)
    seed   = st.slider("Graine", 0, 99, 42)

    if st.button("🎲 Nouveau tableau aléatoire", use_container_width=True):
        st.session_state.hs_arr  = random.sample(range(1, 99), n_size)
        st.session_state.hs_seed = -1  # marque comme manuel

    if "hs_arr" not in st.session_state or len(st.session_state.hs_arr) != n_size:
        random.seed(seed)
        st.session_state.hs_arr = random.sample(range(1, 99), n_size)

    arr   = st.session_state.hs_arr
    steps = heap_sort_steps(arr)

    n_build   = sum(1 for s in steps if s["phase"] == "build")
    n_extract = sum(1 for s in steps if s["phase"] == "extract")

    st.markdown(f'<span class="complexity-badge">O(n log n) — toujours</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{n_build} étapes build + {n_extract} extractions</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🧠 Les deux phases")
    st.markdown("""
    <div class="info-box" style="border-left-color:#7c3aed; font-size:0.82rem;">
    <b>Phase 1 — Build Heap</b><br>
    On parcourt le tableau de droite à gauche en appliquant <b>sift-down</b> sur chaque nœud non-feuille. Résultat : un max-heap valide.<br><br>
    <b>Phase 2 — Extract</b><br>
    On échange la racine (max) avec le dernier élément, on réduit le tas d'un élément, et on rétablit la propriété heap avec <b>sift-down</b>.<br><br>
    <b>Sift-down</b> : descend un élément jusqu'à sa position correcte en l'échangeant avec son plus grand enfant.
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 🎨 Légende barres")
    st.markdown("🟣 **Violet** — Éléments encore dans le tas")
    st.markdown("🟡 **Jaune** — Éléments en cours d'échange")
    st.markdown("🟢 **Vert** — Triés définitivement")

with col_viz:
    st.markdown("##### 📊 Animation — Barres")
    st.markdown("*Appuie sur **▶ Démarrer** ou déplace le slider pour naviguer étape par étape*")
    fig = make_animated_fig(steps)
    st.plotly_chart(fig, use_container_width=True, key=f"hs_anim_{seed}_{n_size}")

    st.markdown("---")
    st.markdown("##### 🌲 Structure du tas — Vue arbre")
    st.markdown("*Le slider ci-dessous est indépendant — il montre l'arbre à n'importe quelle étape*")
    step_tree = st.slider("Étape (vue arbre)", 0, len(steps)-1, 0, key="hs_tree_step")
    s = steps[step_tree]
    st.markdown(f'<div class="info-box" style="border-left-color:#7c3aed;">{s["desc"]}</div>', unsafe_allow_html=True)

    tree_traces = make_tree_traces(s["arr"], s["heap_end"], s["active"])
    fig2 = go.Figure(data=tree_traces)
    fig2.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        margin=dict(l=20, r=20, t=10, b=20), height=300,
    )
    st.plotly_chart(fig2, use_container_width=True, key=f"hs_tree_{step_tree}")
    st.markdown(f'<div style="color:#64748b;font-size:0.75rem;font-family:Space Mono,monospace;">Affiche les {min(s["heap_end"], 15)} premiers nœuds du tas</div>', unsafe_allow_html=True)
