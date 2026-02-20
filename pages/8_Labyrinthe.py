import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random, collections, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Labyrinthe — Graphix", page_icon="🌀", layout="wide")
inject_css()
sidebar_nav()

# ── Génération : DFS récursif (Perfect Maze) ─────────────────────────────────

def generate_maze(rows, cols, seed=42):
    """Génère un labyrinthe parfait par DFS. Retourne la grille et les étapes."""
    rng = random.Random(seed)
    # Grille de murs : 1 = mur, 0 = chemin
    # On travaille sur une grille 2*rows+1 x 2*cols+1
    h, w = 2*rows+1, 2*cols+1
    grid = np.ones((h, w), dtype=int)

    visited = set()
    gen_steps = []  # snapshots de la grille pendant la génération

    def cell_to_grid(r, c):
        return 2*r+1, 2*c+1

    def carve(r, c):
        visited.add((r, c))
        gr, gc = cell_to_grid(r, c)
        grid[gr][gc] = 0
        directions = [(0,1),(0,-1),(1,0),(-1,0)]
        rng.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                # Abattre le mur entre (r,c) et (nr,nc)
                grid[gr+dr][gc+dc] = 0
                gen_steps.append(grid.copy())
                carve(nr, nc)

    carve(0, 0)
    # Entrée et sortie
    grid[0][1] = 0
    grid[h-1][w-2] = 0

    return grid, gen_steps, h, w

# ── Résolution : BFS ──────────────────────────────────────────────────────────

def solve_maze_bfs(grid, h, w):
    start = (0, 1)
    end   = (h-1, w-2)
    queue = collections.deque([(start, [start])])
    visited = {start}
    solve_steps = []

    while queue:
        (r, c), path = queue.popleft()
        solve_steps.append({"visited": set(visited), "current": (r,c), "path": list(path)})

        if (r, c) == end:
            return solve_steps, path

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))

    return solve_steps, []

# ── Frames ────────────────────────────────────────────────────────────────────

def grid_to_heatmap(grid, visited=None, current=None, solution=None, phase="gen"):
    h, w = grid.shape
    z = np.zeros((h, w))

    for r in range(h):
        for c in range(w):
            z[r][c] = 0.9 if grid[r][c] == 1 else 0.0  # mur = blanc, chemin = noir

    if phase == "solve" and visited:
        for (r, c) in visited:
            if grid[r][c] == 0:
                z[r][c] = 0.35

    if solution:
        for (r, c) in solution:
            z[r][c] = 0.7

    if current:
        z[current[0]][current[1]] = 1.0

    colorscale = [
        [0.00, "#0f172a"],    # chemin non visité
        [0.35, "#1e3a5f"],    # visité BFS
        [0.70, "#06b6d4"],    # solution
        [0.90, "#334155"],    # mur
        [1.00, "#f59e0b"],    # position courante
    ]

    return go.Heatmap(
        z=z.tolist(), colorscale=colorscale,
        showscale=False, xgap=0, ygap=0,
        zmin=0, zmax=1,
    )

def make_animated_fig(grid, gen_steps, solve_steps, solution_path, h, w, max_gen_frames=60, max_solve_frames=120):
    # Sous-échantillonner les frames de génération pour ne pas en avoir trop
    step_gen  = max(1, len(gen_steps)  // max_gen_frames)
    step_sol  = max(1, len(solve_steps)// max_solve_frames)
    gen_sampled   = gen_steps[::step_gen]   + [gen_steps[-1]]
    solve_sampled = solve_steps[::step_sol] + [solve_steps[-1]]

    all_frames = []
    descriptions = []

    # Phase 1 : génération
    for i, g in enumerate(gen_sampled):
        all_frames.append(grid_to_heatmap(g, phase="gen"))
        descriptions.append(f"🏗️ Génération du labyrinthe… étape {i+1}/{len(gen_sampled)}")

    # Phase 2 : résolution BFS
    for i, s in enumerate(solve_sampled):
        all_frames.append(grid_to_heatmap(grid, visited=s["visited"],
                                           current=s["current"], phase="solve"))
        descriptions.append(f"🔍 BFS — exploration… {len(s['visited'])} cellules visitées")

    # Frame finale : solution
    all_frames.append(grid_to_heatmap(grid, solution=solution_path, phase="solve"))
    descriptions.append(f"✅ Chemin trouvé ! {len(solution_path)} étapes")

    n_frames = len(all_frames)

    fig = go.Figure(
        data=[all_frames[0]],
        layout=go.Layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, scaleanchor='y'),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, autorange='reversed'),
            margin=dict(l=10, r=10, t=55, b=80),
            height=500,
            annotations=[dict(x=0.5, y=1.08, xref='paper', yref='paper',
                              text=descriptions[0], showarrow=False,
                              font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')],
            updatemenus=[dict(
                type="buttons", showactive=False, y=-0.15, x=0.5, xanchor="center",
                buttons=[
                    dict(label="▶  Démarrer", method="animate",
                         args=[None, dict(frame=dict(duration=80, redraw=True),
                                         transition=dict(duration=30),
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
                currentvalue=dict(prefix="", font=dict(color="#94a3b8", family="Space Mono", size=10),
                                  visible=False),
                pad=dict(t=40, b=5), len=0.9, x=0.05,
                bgcolor="#111118", bordercolor="#1e1e2e", tickcolor="#334155",
                font=dict(color="#64748b", size=8),
                steps=[dict(method="animate",
                            args=[[f"lm{k}"], dict(mode="immediate", frame=dict(duration=80, redraw=True),
                                                   transition=dict(duration=30))],
                            label="") for k in range(n_frames)],
            )],
        ),
        frames=[
            go.Frame(
                name=f"lm{k}",
                data=[all_frames[k]],
                layout=go.Layout(annotations=[dict(
                    x=0.5, y=1.08, xref='paper', yref='paper',
                    text=descriptions[k], showarrow=False,
                    font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')])
            )
            for k in range(n_frames)
        ],
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);color:#fcd34d;">🌀 LABYRINTHE</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Génération & Résolution</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Deux algorithmes en un : <b>DFS</b> génère un labyrinthe parfait (sans boucle), puis <b>BFS</b> trouve le chemin le plus court de l\'entrée à la sortie.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    rows = st.slider("Lignes",   5, 25, 12)
    cols = st.slider("Colonnes", 5, 35, 18)
    seed = st.slider("Graine (forme du labyrinthe)", 0, 99, 7)

    grid, gen_steps, h, w = generate_maze(rows, cols, seed)
    solve_steps, solution_path = solve_maze_bfs(grid, h, w)

    st.markdown(f'<span class="complexity-badge">Génération : O(n×m)</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">Résolution BFS : O(n×m)</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">Chemin : {len(solution_path)} étapes</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🏗️ Génération : DFS")
    st.markdown("""
    <div class="info-box" style="border-left-color:#f59e0b; font-size:0.82rem;">
    Parcours en profondeur (DFS) qui abat les murs entre cellules non visitées. Produit un labyrinthe <b>parfait</b> : un unique chemin entre deux points.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🔍 Résolution : BFS")
    st.markdown("""
    <div class="info-box" style="border-left-color:#06b6d4; font-size:0.82rem;">
    Parcours en largeur garantissant le <b>chemin le plus court</b> entre l'entrée (haut-gauche) et la sortie (bas-droite).
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎨 Légende")
    st.markdown("⬛ **Noir** — Couloir non exploré")
    st.markdown("🔵 **Bleu foncé** — Cellules explorées par BFS")
    st.markdown("🔵 **Cyan** — Chemin optimal")
    st.markdown("🟡 **Jaune** — Position courante")
    st.markdown("⬜ **Gris** — Mur")

with col_viz:
    fig = make_animated_fig(grid, gen_steps, solve_steps, solution_path, h, w)
    st.plotly_chart(fig, width='stretch', key=f"lm_{rows}_{cols}_{seed}")
