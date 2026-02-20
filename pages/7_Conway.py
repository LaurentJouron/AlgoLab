import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Jeu de la Vie — Graphix", page_icon="🧬", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithme ────────────────────────────────────────────────────────────────

def next_generation(grid):
    n_rows, n_cols = grid.shape
    new_grid = np.zeros_like(grid)
    for r in range(n_rows):
        for c in range(n_cols):
            neighbors = int(np.sum(grid[max(0,r-1):r+2, max(0,c-1):c+2])) - int(grid[r, c])
            if grid[r, c] == 1:
                new_grid[r, c] = 1 if neighbors in (2, 3) else 0
            else:
                new_grid[r, c] = 1 if neighbors == 3 else 0
    return new_grid

def compute_generations(grid, n_gen):
    frames_data = [grid.copy()]
    alive_counts = [int(np.sum(grid))]
    g = grid.copy()
    for _ in range(n_gen):
        g = next_generation(g)
        frames_data.append(g.copy())
        alive_counts.append(int(np.sum(g)))
    return frames_data, alive_counts

# ── Patterns célèbres ─────────────────────────────────────────────────────────

def make_grid(rows, cols, pattern, seed=42):
    grid = np.zeros((rows, cols), dtype=int)
    cr, cc = rows // 2, cols // 2

    if pattern == "Aléatoire":
        rng = np.random.default_rng(seed)
        grid = rng.integers(0, 2, size=(rows, cols))

    elif pattern == "Planeur (Glider)":
        g = [(0,1),(1,2),(2,0),(2,1),(2,2)]
        for dr, dc in g:
            grid[cr-1+dr][cc-1+dc] = 1

    elif pattern == "Oscillateur (Blinker)":
        for dc in range(-1, 2):
            grid[cr][cc+dc] = 1

    elif pattern == "Canon de Gosper":
        # Gosper Glider Gun — pattern classique
        cells = [
            (5,1),(5,2),(6,1),(6,2),
            (5,11),(6,11),(7,11),(4,12),(8,12),(3,13),(9,13),(3,14),(9,14),
            (6,15),(4,16),(8,16),(5,17),(6,17),(7,17),(6,18),
            (3,21),(4,21),(5,21),(3,22),(4,22),(5,22),(2,23),(6,23),
            (1,25),(2,25),(6,25),(7,25),
            (3,35),(4,35),(3,36),(4,36),
        ]
        for r, c in cells:
            if 0 <= r < rows and 0 <= c < cols:
                grid[r][c] = 1

    elif pattern == "Ruche (Beehive)":
        hive = [(0,1),(0,2),(1,0),(1,3),(2,1),(2,2)]
        for dr, dc in hive:
            grid[cr-1+dr][cc-2+dc] = 1

    elif pattern == "Vaisseau spatial (LWSS)":
        lwss = [(0,1),(0,4),(1,0),(2,0),(2,4),(3,0),(3,1),(3,2),(3,3)]
        for dr, dc in lwss:
            grid[cr-1+dr][cc-2+dc] = 1

    return grid

def make_heatmap_trace(g):
    return go.Heatmap(
        z=g.tolist(),
        colorscale=[[0, "#0f172a"], [1, "#06b6d4"]],
        showscale=False, xgap=1, ygap=1,
        zmin=0, zmax=1,
    )

def make_animated_fig(frames_data, alive_counts, n_gen):
    fig = go.Figure(
        data=[make_heatmap_trace(frames_data[0])],
        layout=go.Layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            font=dict(color='#e2e8f0', family='DM Sans'),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, autorange='reversed'),
            margin=dict(l=10, r=10, t=55, b=80),
            height=460,
            annotations=[dict(
                x=0.5, y=1.08, xref='paper', yref='paper',
                text=f"Génération 0 — <b>{alive_counts[0]}</b> cellules vivantes",
                showarrow=False,
                font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')],
            updatemenus=[dict(
                type="buttons", showactive=False, y=-0.18, x=0.5, xanchor="center",
                buttons=[
                    dict(label="▶  Démarrer", method="animate",
                         args=[None, dict(frame=dict(duration=150, redraw=True),
                                         transition=dict(duration=50),
                                         fromcurrent=True, mode="immediate")]),
                    dict(label="⏸  Pause", method="animate",
                         args=[[None], dict(frame=dict(duration=0, redraw=False),
                                            mode="immediate", transition=dict(duration=0))]),
                ],
                font=dict(color="#e2e8f0", family="Space Mono", size=12),
                bgcolor="#1e1e2e", bordercolor="#334155",
            )],
            sliders=[dict(
                active=0,
                currentvalue=dict(prefix="Génération : ", font=dict(color="#94a3b8", family="Space Mono", size=11),
                                  visible=True, xanchor="center"),
                pad=dict(t=45, b=5), len=0.9, x=0.05,
                bgcolor="#111118", bordercolor="#1e1e2e", tickcolor="#334155",
                font=dict(color="#64748b", size=9),
                steps=[dict(method="animate",
                            args=[[f"cw{k}"], dict(mode="immediate", frame=dict(duration=150, redraw=True),
                                                   transition=dict(duration=50))],
                            label=str(k)) for k in range(n_gen+1)],
            )],
        ),
        frames=[
            go.Frame(
                name=f"cw{k}",
                data=[make_heatmap_trace(frames_data[k])],
                layout=go.Layout(annotations=[dict(
                    x=0.5, y=1.08, xref='paper', yref='paper',
                    text=f"Génération {k} — <b>{alive_counts[k]}</b> cellules vivantes",
                    showarrow=False,
                    font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')])
            )
            for k in range(n_gen+1)
        ],
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;">🧬 JEU DE LA VIE</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Jeu de la Vie de Conway</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Un automate cellulaire où des structures complexes émergent de 4 règles simples. Chaque cellule naît, survit ou meurt selon le nombre de voisins vivants.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    pattern = st.selectbox("Pattern initial", [
        "Planeur (Glider)", "Canon de Gosper", "Vaisseau spatial (LWSS)",
        "Oscillateur (Blinker)", "Ruche (Beehive)", "Aléatoire"
    ])
    rows    = st.slider("Lignes",       20, 60, 40)
    cols    = st.slider("Colonnes",     20, 80, 60)
    n_gen   = st.slider("Générations",  10, 100, 40)
    seed    = st.slider("Graine (aléatoire)", 0, 99, 42) if pattern == "Aléatoire" else 42

    grid = make_grid(rows, cols, pattern, seed)
    frames_data, alive_counts = compute_generations(grid, n_gen)

    st.markdown(f'<span class="complexity-badge">O(n×m) par génération</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">Grille {rows}×{cols} · {n_gen} générations</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📋 Les 4 règles")
    st.markdown("""
    <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
    1. Cellule vivante avec <b>&lt; 2 voisins</b> → meurt (sous-population)<br>
    2. Cellule vivante avec <b>2 ou 3 voisins</b> → survit<br>
    3. Cellule vivante avec <b>&gt; 3 voisins</b> → meurt (surpopulation)<br>
    4. Cellule morte avec <b>exactement 3 voisins</b> → naît (reproduction)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📊 Évolution")
    max_alive = max(alive_counts)
    min_alive = min(alive_counts)
    st.metric("Max cellules vivantes", max_alive)
    st.metric("Min cellules vivantes", min_alive)

with col_viz:
    fig = make_animated_fig(frames_data, alive_counts, n_gen)
    st.plotly_chart(fig, width='stretch', key=f"cw_{pattern}_{rows}_{cols}_{n_gen}_{seed}")
