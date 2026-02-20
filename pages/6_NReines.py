import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="N-Reines — Graphix", page_icon="♛", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithme backtracking ───────────────────────────────────────────────────

def n_queens_steps(n, max_steps=800):
    steps = []
    board = [-1] * n  # board[col] = row de la reine

    def is_safe(col, row):
        for c in range(col):
            r = board[c]
            if r == row or abs(r - row) == abs(c - col):
                return False
        return True

    def solve(col):
        if len(steps) >= max_steps:
            return False
        if col == n:
            steps.append({
                "board": board.copy(), "col": -1, "action": "solved",
                "desc": f"✅ Solution trouvée ! {n} reines placées sans conflit."
            })
            return True
        for row in range(n):
            if is_safe(col, row):
                board[col] = row
                steps.append({
                    "board": board.copy(), "col": col, "action": "place",
                    "desc": f"Reine placée colonne {col+1}, ligne {row+1} — test en cours…"
                })
                if solve(col + 1):
                    return True
                board[col] = -1
                steps.append({
                    "board": board.copy(), "col": col, "action": "backtrack",
                    "desc": f"↩ Backtrack colonne {col+1} — aucune position valide, on recule"
                })
        return False

    solve(0)
    return steps

def make_board_frame(board, n, col_active, action):
    # Construire la grille comme heatmap
    z    = [[0]*n for _ in range(n)]
    text = [["" ]*n for _ in range(n)]

    # Damier
    for r in range(n):
        for c in range(n):
            z[r][c] = 0.3 if (r+c) % 2 == 0 else 0.15

    # Reines placées
    for c in range(n):
        if board[c] != -1:
            r = board[c]
            if action == "solved":
                z[r][c] = 1.0
                text[r][c] = "♛"
            elif c == col_active and action == "backtrack":
                z[r][c] = 0.6
                text[r][c] = "✗"
            elif c == col_active:
                z[r][c] = 0.85
                text[r][c] = "♛"
            else:
                z[r][c] = 0.75
                text[r][c] = "♛"

    # Conflits visualisés (lignes/diagonales de la reine active)
    if col_active >= 0 and col_active < n and board[col_active] != -1 and action != "backtrack":
        row_active = board[col_active]
        for c in range(n):
            if c != col_active:
                # Même ligne
                if z[row_active][c] < 0.5:
                    z[row_active][c] = max(z[row_active][c], 0.45)
                # Diagonales
                dr = abs(c - col_active)
                for r in [row_active + dr, row_active - dr]:
                    if 0 <= r < n and z[r][c] < 0.5:
                        z[r][c] = max(z[r][c], 0.45)

    colorscale = [
        [0.00, "#0f172a"],
        [0.15, "#1e293b"],
        [0.30, "#1e293b"],
        [0.45, "#4c1d95"],
        [0.60, "#ef4444"],
        [0.75, "#7c3aed"],
        [0.85, "#f59e0b"],
        [1.00, "#10b981"],
    ]

    return [go.Heatmap(
        z=z, text=text, texttemplate="%{text}",
        textfont=dict(size=max(10, 28-n*2), color='white', family='Arial'),
        colorscale=colorscale,
        showscale=False, xgap=2, ygap=2,
        zmin=0, zmax=1,
    )]

def make_animated_fig(steps, n):
    s0     = steps[0]
    data0  = make_board_frame(s0["board"], n, s0["col"], s0["action"])

    fig = go.Figure(
        data=data0,
        layout=go.Layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            font=dict(color='#e2e8f0', family='DM Sans'),
            xaxis=dict(showgrid=False, showticklabels=True, zeroline=False,
                       tickvals=list(range(n)), ticktext=[f"Col {i+1}" for i in range(n)],
                       tickfont=dict(size=9, color='#64748b', family='Space Mono')),
            yaxis=dict(showgrid=False, showticklabels=True, zeroline=False, autorange='reversed',
                       tickvals=list(range(n)), ticktext=[f"Lig {i+1}" for i in range(n)],
                       tickfont=dict(size=9, color='#64748b', family='Space Mono')),
            margin=dict(l=60, r=20, t=60, b=80),
            height=460,
            annotations=[dict(x=0.5, y=1.09, xref='paper', yref='paper',
                              text=s0["desc"], showarrow=False,
                              font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')],
            updatemenus=[dict(
                type="buttons", showactive=False, y=-0.2, x=0.5, xanchor="center",
                buttons=[
                    dict(label="▶  Démarrer", method="animate",
                         args=[None, dict(frame=dict(duration=300, redraw=True),
                                         transition=dict(duration=100, easing="cubic-in-out"),
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
                            args=[[f"nq{k}"], dict(mode="immediate", frame=dict(duration=300, redraw=True),
                                                   transition=dict(duration=100))],
                            label=str(k)) for k in range(len(steps))],
            )],
        ),
        frames=[
            go.Frame(
                name=f"nq{k}",
                data=make_board_frame(s["board"], n, s["col"], s["action"]),
                layout=go.Layout(annotations=[dict(
                    x=0.5, y=1.09, xref='paper', yref='paper',
                    text=s["desc"], showarrow=False,
                    font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')])
            )
            for k, s in enumerate(steps)
        ],
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;">♛ N-REINES</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">N-Reines</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Placer N reines sur un échiquier N×N sans qu\'elles se menacent mutuellement. Le backtracking explore chaque possibilité et recule dès qu\'un conflit est détecté.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    n = st.slider("Taille de l'échiquier (N)", 4, 10, 6)

    steps = n_queens_steps(n)
    n_backtracks = sum(1 for s in steps if s["action"] == "backtrack")
    solved       = any(s["action"] == "solved" for s in steps)

    st.markdown(f'<span class="complexity-badge">O(N!) dans le pire cas</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{len(steps)} étapes · {n_backtracks} backtracks</span>', unsafe_allow_html=True)

    if solved:
        st.success(f"✅ Solution trouvée en {len(steps)} étapes")
    else:
        st.warning("⚠️ Limite d'étapes atteinte — augmente N pour voir plus")

    st.markdown("---")
    st.markdown("#### 🧠 Principe du backtracking")
    st.markdown("""
    <div class="info-box" style="border-left-color:#ef4444; font-size:0.82rem;">
    1. Placer une reine dans la colonne courante<br>
    2. Vérifier qu'elle ne menace aucune reine existante<br>
    3. Si OK → passer à la colonne suivante<br>
    4. Si impossible → <b>backtrack</b> ↩ (retirer et essayer la ligne suivante)<br>
    5. Recommencer jusqu'à placer toutes les reines
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎨 Légende")
    st.markdown("♛ **Jaune** — Reine en cours de test")
    st.markdown("♛ **Violet** — Reine validée")
    st.markdown("♛ **Vert** — Solution finale")
    st.markdown("✗ **Rouge** — Backtrack")
    st.markdown("🟣 **Violet clair** — Cases sous menace")

with col_viz:
    fig = make_animated_fig(steps, n)
    st.plotly_chart(fig, width='stretch', key=f"nq_{n}")
