import streamlit as st
import plotly.graph_objects as go
from collections import deque
import random, sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Flood Fill — Graphix", page_icon="🌊", layout="wide"
)
inject_css()
sidebar_nav()

# ── Algorithme ────────────────────────────────────────────────────────────────
PALETTE = {
    "Blanc": (255, 255, 255),
    "Rouge": (220, 50, 50),
    "Bleu": (50, 130, 220),
    "Vert": (50, 180, 80),
    "Jaune": (240, 200, 0),
    "Orange": (230, 120, 20),
    "Violet": (140, 60, 200),
    "Cyan": (20, 190, 210),
}


def rgb_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def make_grid(n, seed=42):
    rng = random.Random(seed)
    colors = list(PALETTE.keys())
    return [[rng.choice(colors[:4]) for _ in range(n)] for _ in range(n)]


def flood_fill_steps(grid, sx, sy, new_color):
    n = len(grid)
    g = [row[:] for row in grid]
    old_c = g[sx][sy]
    if old_c == new_color:
        return [
            {
                "grid": g,
                "frontier": set(),
                "filled": set(),
                "desc": "La couleur cible est identique — rien à faire",
            }
        ]

    steps = []
    frontier = deque([(sx, sy)])
    visited = set()
    filled = set()

    steps.append(
        {
            "grid": [r[:] for r in g],
            "frontier": {(sx, sy)},
            "filled": set(),
            "desc": f"Départ en ({sx},{sy}) — couleur source : <b>{old_c}</b>, cible : <b>{new_color}</b>",
        }
    )

    while frontier:
        batch_front = set()
        next_frontier = deque()
        # Traiter toute la frontière courante en une étape visuelle
        for _ in range(min(len(frontier), 8)):
            if not frontier:
                break
            x, y = frontier.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            g[x][y] = new_color
            filled.add((x, y))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < n
                    and 0 <= ny < n
                    and g[nx][ny] == old_c
                    and (nx, ny) not in visited
                ):
                    next_frontier.append((nx, ny))
                    batch_front.add((nx, ny))
            frontier.extendleft(list(next_frontier)[::-1])
            next_frontier = deque()

        steps.append(
            {
                "grid": [r[:] for r in g],
                "frontier": set(batch_front),
                "filled": set(filled),
                "desc": f"Propagation — {len(filled)} cellule(s) remplies",
            }
        )

    steps.append(
        {
            "grid": [r[:] for r in g],
            "frontier": set(),
            "filled": set(filled),
            "desc": f"✅ Remplissage terminé — <b>{len(filled)}</b> cellule(s) modifiées",
        }
    )
    return steps


def count_islands_steps(grid):
    n = len(grid)
    g = [row[:] for row in grid]
    visited = [[False] * n for _ in range(n)]
    island_id = [[0] * n for _ in range(n)]
    steps, count = [], 0
    steps.append(
        {
            "visited": [r[:] for r in visited],
            "island_id": [r[:] for r in island_id],
            "count": 0,
            "desc": "Comptage des îles — chaque couleur distincte = une île",
        }
    )
    for i in range(n):
        for j in range(n):
            if not visited[i][j]:
                count += 1
                q = deque([(i, j)])
                c = g[i][j]
                while q:
                    x, y = q.popleft()
                    if visited[x][y]:
                        continue
                    visited[x][y] = True
                    island_id[x][y] = count
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < n
                            and 0 <= ny < n
                            and not visited[nx][ny]
                            and g[nx][ny] == c
                        ):
                            q.append((nx, ny))
                steps.append(
                    {
                        "visited": [r[:] for r in visited],
                        "island_id": [r[:] for r in island_id],
                        "count": count,
                        "desc": f"Île n°{count} découverte en ({i},{j}) — couleur <b>{c}</b>",
                    }
                )
    steps.append(
        {
            "visited": [r[:] for r in visited],
            "island_id": [r[:] for r in island_id],
            "count": count,
            "desc": f"✅ <b>{count}</b> île(s) distincte(s) trouvées",
        }
    )
    return steps


# ── Visualisation ─────────────────────────────────────────────────────────────
ISLAND_COLORS = [
    "#ef4444",
    "#f59e0b",
    "#10b981",
    "#06b6d4",
    "#7c3aed",
    "#ec4899",
    "#84cc16",
    "#f97316",
    "#14b8a6",
    "#8b5cf6",
]


def make_grid_fig(
    grid, frontier=None, filled=None, island_id=None, n_islands=0, title=""
):
    n = len(grid)
    frontier = frontier or set()
    filled = filled or set()
    z, text, hover = [], [], []

    for i in range(n):
        zrow, trow, hrow = [], [], []
        for j in range(n):
            cell_color = PALETTE[grid[i][j]]
            zrow.append(
                cell_color[0] * 0.299
                + cell_color[1] * 0.587
                + cell_color[2] * 0.114
            )
            trow.append("")
            if (i, j) in frontier:
                hrow.append(f"Frontière ({i},{j})")
            else:
                hrow.append(f"({i},{j}): {grid[i][j]}")
        z.append(zrow)
        text.append(trow)
        hover.append(hrow)

    fig = go.Figure()
    # Trace fantôme pour ancrer les axes (sans shapes, Plotly ne dimensionne pas)
    fig.add_trace(
        go.Scatter(
            x=[-0.5, n - 0.5],
            y=[-0.5, n - 0.5],
            mode="markers",
            marker=dict(size=0.1, opacity=0),
            hoverinfo="none",
            showlegend=False,
        )
    )
    for i in range(n):
        for j in range(n):
            r, g, b = PALETTE[grid[i][j]]
            if island_id and island_id[i][j] > 0:
                fill = ISLAND_COLORS[
                    (island_id[i][j] - 1) % len(ISLAND_COLORS)
                ]
            else:
                fill = rgb_hex(r, g, b)

            border_color = (
                "#f59e0b"
                if (i, j) in frontier
                else "#10b981" if (i, j) in filled else "#0a0a0f"
            )
            border_w = 3 if (i, j) in frontier or (i, j) in filled else 0.5

            fig.add_shape(
                type="rect",
                x0=j - 0.5,
                y0=n - i - 1.5,
                x1=j + 0.5,
                y1=n - i - 0.5,
                fillcolor=fill,
                line=dict(color=border_color, width=border_w),
            )

    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#0a0a0f",
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-0.5, n - 0.5],
            constrain="domain",
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-0.5, n - 0.5],
            scaleanchor="x",
        ),
        margin=dict(l=10, r=10, t=30 if title else 10, b=10),
        height=420,
        title=(
            dict(text=title, font=dict(color="#94a3b8", size=12), x=0.5)
            if title
            else None
        ),
    )
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.3);color:#67e8f9;">🌊 FLOOD FILL</span>',
    unsafe_allow_html=True,
)
st.markdown('<div class="page-title">Flood Fill</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-desc">L\'algorithme derrière l\'outil "seau" de Paint. Un BFS se propage depuis la cellule cliquée vers toutes les cellules adjacentes de même couleur. Application classique : compter les régions connexes (îles).</div>',
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["🪣  Remplissage (Paint)", "🏝️  Compter les îles"])

# ── Tab 1 : Flood Fill classique ──────────────────────────────────────────────
with tab1:
    col_ctrl, col_viz = st.columns([1, 3])
    with col_ctrl:
        st.markdown("#### ⚙️ Paramètres")
        n_ff = st.slider("Taille de la grille", 6, 16, 10, key="ff_n")
        seed_ff = st.slider("Graine", 0, 99, 7, key="ff_seed")
        sx = st.slider("Ligne de départ", 0, n_ff - 1, n_ff // 2, key="ff_sx")
        sy = st.slider(
            "Colonne de départ", 0, n_ff - 1, n_ff // 2, key="ff_sy"
        )
        new_c = st.selectbox(
            "Nouvelle couleur", list(PALETTE.keys()), index=5, key="ff_color"
        )

        grid_ff = make_grid(n_ff, seed_ff)
        steps_ff = flood_fill_steps(grid_ff, sx, sy, new_c)

        old_c = grid_ff[sx][sy]
        st.markdown(
            f'<span class="complexity-badge">O(n×m) — BFS</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{len(steps_ff)} étapes</span>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            f"""
        <div class="info-box" style="border-left-color:#06b6d4; font-size:0.82rem;">
        <b>Cellule sélectionnée :</b> ({sx},{sy})<br>
        <b>Couleur source :</b> {old_c}<br>
        <b>Nouvelle couleur :</b> {new_c}<br><br>
        <b>Algorithme (BFS) :</b><br>
        1. Ajouter la cellule de départ à la file<br>
        2. Dépiler une cellule, la recolorer<br>
        3. Ajouter ses voisins de même couleur<br>
        4. Répéter jusqu'à la file vide
        </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("🟡 **Jaune** = frontière active")
        st.markdown("🟢 **Vert** = cellules remplies")
        st.markdown("*Glisse le slider pour voir la propagation*")

    with col_viz:
        si = st.slider("Étape", 0, len(steps_ff) - 1, 0, key="ff_step")
        s = steps_ff[si]
        st.markdown(
            f'<div class="info-box" style="border-left-color:#06b6d4;">{s["desc"]}</div>',
            unsafe_allow_html=True,
        )
        fig = make_grid_fig(s["grid"], s["frontier"], s["filled"])
        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"ff_{si}_{seed_ff}_{sx}_{sy}_{new_c}",
        )

# ── Tab 2 : Compter les îles ──────────────────────────────────────────────────
with tab2:
    col_ctrl2, col_viz2 = st.columns([1, 3])
    with col_ctrl2:
        st.markdown("#### ⚙️ Paramètres")
        n_il = st.slider("Taille de la grille", 5, 12, 8, key="il_n")
        seed_il = st.slider("Graine", 0, 99, 22, key="il_seed")

        grid_il = make_grid(n_il, seed_il)
        steps_il = count_islands_steps(grid_il)

        st.markdown(
            f'<span class="complexity-badge">O(n×m) — DFS/BFS</span>',
            unsafe_allow_html=True,
        )
        st.metric("Îles trouvées", steps_il[-1]["count"])
        st.markdown("---")
        st.markdown(
            """
        <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
        <b>Problème classique d'entretien :</b><br><br>
        Compter les régions connexes dans une grille.<br>
        Chaque groupe de cellules adjacentes de même couleur = une île.<br><br>
        <b>Algorithme :</b><br>
        Pour chaque cellule non-visitée, lancer un DFS/BFS pour marquer toute sa région.
        Chaque nouveau départ = une nouvelle île.
        </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("🎨 **Chaque couleur** = une île distincte")
        st.markdown("*Avance étape par étape pour voir la découverte*")

    with col_viz2:
        si2 = st.slider("Étape", 0, len(steps_il) - 1, 0, key="il_step")
        s2 = steps_il[si2]
        st.markdown(
            f'<div class="info-box" style="border-left-color:#10b981;">{s2["desc"]}</div>',
            unsafe_allow_html=True,
        )
        st.metric("Îles découvertes", s2["count"])
        fig2 = make_grid_fig(
            grid_il,
            island_id=s2["island_id"],
            n_islands=s2["count"],
            title="Îles colorées par région",
        )
        st.plotly_chart(
            fig2, use_container_width=True, key=f"il_{si2}_{seed_il}"
        )
