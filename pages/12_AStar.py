import streamlit as st
import plotly.graph_objects as go
import heapq, math, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="A* — Graphix", page_icon="⭐", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithme A* sur grille ──────────────────────────────────────────────────

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])  # Manhattan

def astar_steps(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    open_set   = [(0, start)]
    came_from  = {}
    g_score    = {start: 0}
    f_score    = {start: heuristic(start, end)}
    open_nodes = {start}
    closed     = set()
    steps      = []

    while open_set:
        _, current = heapq.heappop(open_set)
        if current not in open_nodes:
            continue
        open_nodes.discard(current)

        if current == end:
            # Reconstituer le chemin
            path = []
            node = end
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()
            steps.append({"current": current, "open": set(open_nodes), "closed": set(closed),
                          "path": path, "g": dict(g_score), "f": dict(f_score),
                          "desc": f"✅ Chemin trouvé ! {len(path)} étapes, coût = {g_score[end]}"})
            return steps, path

        closed.add(current)
        steps.append({"current": current, "open": set(open_nodes), "closed": set(closed),
                      "path": [], "g": dict(g_score), "f": dict(f_score),
                      "desc": f"Explore <b>({current[0]},{current[1]})</b> | g={g_score[current]} | h={heuristic(current,end)} | f={f_score.get(current,'?')}"})

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = current[0]+dr, current[1]+dc
            neighbor = (nr, nc)
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and neighbor not in closed:
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor]   = tentative_g
                    f_score[neighbor]   = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_nodes.add(neighbor)
                    steps.append({"current": neighbor, "open": set(open_nodes), "closed": set(closed),
                                  "path": [], "g": dict(g_score), "f": dict(f_score),
                                  "desc": f"Mise à jour <b>({nr},{nc})</b> | g={tentative_g} | h={heuristic(neighbor,end)} | f={f_score[neighbor]}"})

    steps.append({"current": None, "open": set(), "closed": set(closed),
                  "path": [], "g": dict(g_score), "f": dict(f_score),
                  "desc": "❌ Aucun chemin trouvé"})
    return steps, []

def make_grid_frame(grid, step, start, end):
    rows, cols = len(grid), len(grid[0])
    z = [[0.0]*cols for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                z[r][c] = 1.0           # mur
            elif (r,c) in step["closed"]:
                z[r][c] = 0.35          # fermé
            elif (r,c) in step["open"]:
                z[r][c] = 0.55          # ouvert
            else:
                z[r][c] = 0.0           # non visité

    for (r,c) in step["path"]:
        z[r][c] = 0.8                   # chemin final

    if step["current"]:
        r,c = step["current"]
        z[r][c] = 0.95                  # nœud actif

    # Départ et arrivée
    z[start[0]][start[1]] = 0.72
    z[end[0]][end[1]]     = 0.72

    colorscale = [
        [0.00, "#0f172a"],   # non visité
        [0.35, "#1e3a5f"],   # fermé (exploré)
        [0.55, "#7c3aed"],   # ouvert (à explorer)
        [0.72, "#10b981"],   # départ/arrivée/chemin
        [0.80, "#06b6d4"],   # chemin final
        [0.95, "#f59e0b"],   # nœud actif
        [1.00, "#334155"],   # mur
    ]

    return go.Heatmap(z=z, colorscale=colorscale, showscale=False,
                      xgap=1, ygap=1, zmin=0, zmax=1)

def make_animated_fig(grid, steps, start, end):
    s0 = steps[0]
    fig = go.Figure(
        data=[make_grid_frame(grid, s0, start, end)],
        layout=go.Layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, autorange='reversed'),
            margin=dict(l=10, r=10, t=55, b=80), height=460,
            annotations=[dict(x=0.5, y=1.08, xref='paper', yref='paper',
                              text=s0["desc"], showarrow=False,
                              font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')],
            updatemenus=[dict(
                type="buttons", showactive=False, y=-0.16, x=0.5, xanchor="center",
                buttons=[
                    dict(label="▶  Démarrer", method="animate",
                         args=[None, dict(frame=dict(duration=120, redraw=True),
                                         transition=dict(duration=40),
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
                currentvalue=dict(prefix="Étape : ", font=dict(color="#94a3b8", family="Space Mono", size=11),
                                  visible=True, xanchor="center"),
                pad=dict(t=45, b=5), len=0.9, x=0.05,
                bgcolor="#111118", bordercolor="#1e1e2e", tickcolor="#334155",
                font=dict(color="#64748b", size=8),
                steps=[dict(method="animate",
                            args=[[f"as{k}"], dict(mode="immediate", frame=dict(duration=120, redraw=True),
                                                   transition=dict(duration=40))],
                            label=str(k)) for k in range(len(steps))],
            )],
        ),
        frames=[
            go.Frame(name=f"as{k}", data=[make_grid_frame(grid, s, start, end)],
                     layout=go.Layout(annotations=[dict(x=0.5, y=1.08, xref='paper', yref='paper',
                                                        text=s["desc"], showarrow=False,
                                                        font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')]))
            for k, s in enumerate(steps)
        ],
    )
    return fig

# ── Grilles prédéfinies ───────────────────────────────────────────────────────

def make_random_grid(rows, cols, wall_pct, seed):
    import random
    rng = random.Random(seed)
    grid = [[1 if rng.random() < wall_pct else 0 for _ in range(cols)] for _ in range(rows)]
    grid[0][0] = 0; grid[rows-1][cols-1] = 0
    return grid

PRESET_GRIDS = {
    "Labyrinthe simple": [
        [0,0,0,1,0,0,0,0,0,0],
        [1,1,0,1,0,1,1,1,1,0],
        [0,0,0,0,0,0,0,1,0,0],
        [0,1,1,1,1,1,0,1,0,1],
        [0,0,0,0,0,1,0,0,0,0],
        [1,1,1,1,0,1,1,1,1,0],
        [0,0,0,1,0,0,0,0,1,0],
        [0,1,0,1,1,1,1,0,1,0],
        [0,1,0,0,0,0,0,0,1,0],
        [0,0,0,1,1,1,1,1,1,0],
    ],
    "Couloir étroit": [
        [0,0,0,0,0,0,0,0,0,0],
        [1,1,1,1,1,1,1,1,1,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,1],
        [0,0,0,0,0,0,0,0,0,0],
        [1,1,1,1,1,1,1,1,1,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,1,1,1,1,1,1,1,1,1],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
    ],
}

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);color:#fcd34d;">⭐ ALGORITHME A*</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">A* — Chemin Optimal</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">A* combine le coût réel (g) et une heuristique (h) pour trouver le chemin le plus court plus efficacement que Dijkstra. <b>Violet</b> = ouvert, <b>bleu foncé</b> = exploré, <b>cyan</b> = chemin final.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    grid_choice = st.selectbox("Grille", list(PRESET_GRIDS.keys()) + ["Aléatoire"])

    if grid_choice == "Aléatoire":
        rows     = st.slider("Lignes",   8, 20, 12)
        cols_n   = st.slider("Colonnes", 8, 20, 12)
        wall_pct = st.slider("Densité de murs", 0.1, 0.5, 0.28)
        seed     = st.slider("Graine", 0, 99, 42)
        grid     = make_random_grid(rows, cols_n, wall_pct, seed)
    else:
        grid = PRESET_GRIDS[grid_choice]

    rows, cols_n = len(grid), len(grid[0])
    start = (0, 0)
    end   = (rows-1, cols_n-1)

    steps, path = astar_steps(grid, start, end)

    st.markdown(f'<span class="complexity-badge">O((V+E) log V) avec heuristique</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{len(steps)} étapes explorées</span>', unsafe_allow_html=True)
    if path:
        st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">Chemin : {len(path)} cases</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🧠 Formule A*")
    st.markdown("""
    <div class="info-box" style="border-left-color:#f59e0b; font-size:0.82rem;">
    <b>f(n) = g(n) + h(n)</b><br><br>
    • <b>g(n)</b> : coût réel depuis le départ<br>
    • <b>h(n)</b> : heuristique (distance Manhattan)<br>
    • Explore toujours le nœud avec le plus petit <b>f</b><br>
    • Garantit le chemin optimal si h est admissible
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎨 Légende")
    st.markdown("🟡 **Jaune** — Nœud actif")
    st.markdown("🟣 **Violet** — Open set (à explorer)")
    st.markdown("🔵 **Bleu foncé** — Closed set (exploré)")
    st.markdown("🟢 **Vert** — Départ / Arrivée")
    st.markdown("🔵 **Cyan** — Chemin optimal")
    st.markdown("⬜ **Gris** — Mur")

with col_viz:
    fig = make_animated_fig(grid, steps, start, end)
    st.plotly_chart(fig, width='stretch', key=f"as_{grid_choice}_{len(steps)}")
