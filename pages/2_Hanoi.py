import streamlit as st
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Hanoï — Graphix", page_icon="🗼", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithme ────────────────────────────────────────────────────────────────

DISK_COLORS = [
    "#7c3aed",
    "#06b6d4",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#ec4899",
    "#8b5cf6",
    "#14b8a6",
]


def hanoi_moves(n):
    moves = []

    def solve(k, src, tgt, aux):
        if k == 0:
            return
        solve(k - 1, src, aux, tgt)
        moves.append((src, tgt, k))
        solve(k - 1, aux, tgt, src)

    solve(n, "A", "C", "B")
    return moves


def build_state(n_disks, moves_done):
    towers = {"A": list(range(n_disks, 0, -1)), "B": [], "C": []}
    for src, tgt, _ in moves_done:
        towers[tgt].append(towers[src].pop())
    return towers


def make_hanoi_frame_data(towers, n_disks, highlight=None):
    """Retourne shapes + annotations pour un état donné des tours."""
    shapes, annotations = [], []
    tower_x = {"A": 1, "B": 3, "C": 5}

    for t, cx in tower_x.items():
        # Pilier
        shapes.append(
            dict(
                type="rect",
                x0=cx - 0.08,
                x1=cx + 0.08,
                y0=0,
                y1=n_disks + 1.2,
                fillcolor="#334155",
                line=dict(color="#475569", width=1),
            )
        )
        # Base
        shapes.append(
            dict(
                type="rect",
                x0=cx - 1.5,
                x1=cx + 1.5,
                y0=-0.3,
                y1=0,
                fillcolor="#1e293b",
                line=dict(color="#334155", width=1),
            )
        )
        # Label tour
        annotations.append(
            dict(
                x=cx,
                y=-0.7,
                text=f"<b>{t}</b>",
                showarrow=False,
                font=dict(color="#e2e8f0", size=16, family="Space Mono"),
            )
        )
        # Disques
        for row, disk in enumerate(towers[t]):
            w = disk * 0.8 + 0.4
            color = DISK_COLORS[(disk - 1) % len(DISK_COLORS)]
            border = "#ffffff" if highlight == disk else color
            lw = 2 if highlight == disk else 0
            shapes.append(
                dict(
                    type="rect",
                    x0=cx - w / 2,
                    x1=cx + w / 2,
                    y0=row + 0.05,
                    y1=row + 0.85,
                    fillcolor=color,
                    line=dict(color=border, width=lw),
                )
            )
            annotations.append(
                dict(
                    x=cx,
                    y=row + 0.45,
                    text=str(disk),
                    showarrow=False,
                    font=dict(color="white", size=11, family="Space Mono"),
                )
            )

    return shapes, annotations


def make_animated_fig(n_disks, all_moves):
    total = len(all_moves)

    def step_desc(k):
        if k == 0:
            return f"État initial : {n_disks} disques sur la tour A"
        elif k == total:
            return "✅ Terminé ! Tous les disques sont sur la tour C."
        else:
            src, tgt, disk = all_moves[k - 1]
            return f"Mouvement {k}/{total} — Disque <b>{disk}</b> : Tour {src} → Tour {tgt}"

    # Pré-calcul de tous les états
    all_states = []
    for k in range(total + 1):
        towers = build_state(n_disks, all_moves[:k])
        highlight = all_moves[k - 1][2] if k > 0 else None
        shapes, annots = make_hanoi_frame_data(towers, n_disks, highlight)
        all_states.append((shapes, annots, step_desc(k)))

    base_layout = dict(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        xaxis=dict(
            range=[0, 6.5],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=dict(
            range=[-1.2, n_disks + 1.8],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        margin=dict(l=10, r=10, t=55, b=70),
        height=420,
    )

    sh0, an0, desc0 = all_states[0]
    fig = go.Figure(
        # Trace fantôme invisible — les disques sont dans les shapes/annotations
        data=[
            go.Scatter(x=[None], y=[None], mode="markers", showlegend=False)
        ],
        layout=go.Layout(
            **base_layout,
            shapes=sh0,
            annotations=an0
            + [
                dict(
                    x=0.5,
                    y=1.08,
                    xref="paper",
                    yref="paper",
                    text=desc0,
                    showarrow=False,
                    font=dict(color="#94a3b8", size=12, family="DM Sans"),
                    align="center",
                )
            ],
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    y=-0.18,
                    x=0.5,
                    xanchor="center",
                    buttons=[
                        dict(
                            label="▶  Démarrer",
                            method="animate",
                            args=[
                                None,
                                dict(
                                    frame=dict(duration=500, redraw=True),
                                    transition=dict(
                                        duration=150, easing="cubic-in-out"
                                    ),
                                    fromcurrent=True,
                                    mode="immediate",
                                ),
                            ],
                        ),
                        dict(
                            label="⏸  Pause",
                            method="animate",
                            args=[
                                [None],
                                dict(
                                    frame=dict(duration=0, redraw=False),
                                    mode="immediate",
                                    transition=dict(duration=0),
                                ),
                            ],
                        ),
                    ],
                    font=dict(color="#e2e8f0", family="Space Mono", size=12),
                    bgcolor="#1e1e2e",
                    bordercolor="#334155",
                )
            ],
            sliders=[
                dict(
                    active=0,
                    currentvalue=dict(
                        prefix="Mouvement : ",
                        font=dict(
                            color="#94a3b8", family="Space Mono", size=11
                        ),
                        visible=True,
                        xanchor="center",
                    ),
                    pad=dict(t=45, b=5),
                    len=0.9,
                    x=0.05,
                    bgcolor="#111118",
                    bordercolor="#1e1e2e",
                    tickcolor="#334155",
                    font=dict(color="#64748b", size=9),
                    steps=[
                        dict(
                            method="animate",
                            args=[
                                [f"h{k}"],
                                dict(
                                    mode="immediate",
                                    frame=dict(duration=500, redraw=True),
                                    transition=dict(duration=150),
                                ),
                            ],
                            label=str(k),
                        )
                        for k in range(total + 1)
                    ],
                )
            ],
        ),
        frames=[
            go.Frame(
                name=f"h{k}",
                data=[
                    go.Scatter(
                        x=[None], y=[None], mode="markers", showlegend=False
                    )
                ],
                layout=go.Layout(
                    shapes=sh,
                    annotations=an
                    + [
                        dict(
                            x=0.5,
                            y=1.08,
                            xref="paper",
                            yref="paper",
                            text=desc,
                            showarrow=False,
                            font=dict(
                                color="#94a3b8", size=12, family="DM Sans"
                            ),
                            align="center",
                        )
                    ],
                ),
            )
            for k, (sh, an, desc) in enumerate(all_states)
        ],
    )
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.3);color:#67e8f9;">🗼 TOURS DE HANOÏ</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-title">Tours de Hanoï</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="page-desc">Déplacer n disques de la tour A à la tour C, sans jamais poser un grand disque sur un petit. Utilisez <b>▶ Démarrer</b> ou le slider pour naviguer pas à pas.</div>',
    unsafe_allow_html=True,
)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    n_disks = st.slider("Nombre de disques", 2, 7, 3)

    total_moves = 2**n_disks - 1
    st.markdown(
        f'<span class="complexity-badge">Total : {total_moves} mouvements</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">O(2ⁿ) · n={n_disks}</span>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### 🧠 Principe récursif")
    st.markdown(
        """
    <div class="info-box" style="border-left-color:#06b6d4; font-size:0.82rem;">
    <b>hanoi(n, A→C via B) :</b><br>
    1. hanoi(n-1, A→B via C)<br>
    2. Déplacer disque n : A→C<br>
    3. hanoi(n-1, B→C via A)
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### 🎨 Disques")
    for i in range(1, n_disks + 1):
        c = DISK_COLORS[(i - 1) % len(DISK_COLORS)]
        st.markdown(
            f'<span style="color:{c};font-family:Space Mono,monospace;font-size:0.85rem;">● Disque {i}</span>',
            unsafe_allow_html=True,
        )

with col_viz:
    all_moves = hanoi_moves(n_disks)
    fig = make_animated_fig(n_disks, all_moves)
    st.plotly_chart(fig, width="stretch", key=f"hanoi_{n_disks}")
