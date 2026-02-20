import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Sac à Dos — Graphix", page_icon="🎒", layout="wide"
)
inject_css()
sidebar_nav()

# ── Algorithme ────────────────────────────────────────────────────────────────


def knapsack_dp(weights, values, capacity):
    n = len(weights)
    dp = np.zeros((n + 1, capacity + 1), dtype=int)
    steps = []

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i - 1] <= w:
                take = values[i - 1] + dp[i - 1][w - weights[i - 1]]
                notake = dp[i - 1][w]
                dp[i][w] = take if take > notake else notake
                action = (
                    f"Objet {i} ({values[i-1]}€, {weights[i-1]}kg) → PRIS (gain {take} > {notake})"
                    if take > notake
                    else f"Objet {i} ({values[i-1]}€, {weights[i-1]}kg) → IGNORÉ ({notake} ≥ {take})"
                )
            else:
                dp[i][w] = dp[i - 1][w]
                action = f"Objet {i} trop lourd ({weights[i-1]}kg > {w}kg dispo) → IGNORÉ"
            steps.append((i, w, dp.copy(), action))

    chosen, ci, cw = [], n, capacity
    while ci > 0 and cw > 0:
        if dp[ci][cw] != dp[ci - 1][cw]:
            chosen.append(ci - 1)
            cw -= weights[ci - 1]
        ci -= 1

    return dp, steps, chosen


def hex_to_rgba(h, a):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


def make_items_bar(weights, values, n, chosen_indices, current_item):
    colors = [
        (
            "#10b981"
            if i in chosen_indices
            else "#f59e0b" if i == current_item else "#334155"
        )
        for i in range(n)
    ]
    return [
        go.Bar(
            name="Valeur (€)",
            x=[f"Obj {i+1}" for i in range(n)],
            y=values,
            marker_color=colors,
            text=[f"{v}€" for v in values],
            textposition="auto",
            textfont=dict(color="white", size=10),
        ),
        go.Bar(
            name="Poids (kg)",
            x=[f"Obj {i+1}" for i in range(n)],
            y=weights,
            marker_color=[hex_to_rgba(c, 0.5) for c in colors],
            text=[f"{w}kg" for w in weights],
            textposition="auto",
            textfont=dict(color="white", size=10),
        ),
    ]


def make_dp_heatmap(dp_partial, hi, hw):
    z = dp_partial.astype(float)
    rows, cols = z.shape
    # Masquer les cellules pas encore remplies
    for c in range(cols):
        if c > hw:
            z[hi][c] = float("nan")
    text = [[str(int(v)) if not np.isnan(v) else "" for v in row] for row in z]
    return go.Heatmap(
        z=z,
        text=text,
        texttemplate="%{text}",
        textfont=dict(size=10, color="white", family="Space Mono"),
        colorscale=[[0, "#111118"], [0.5, "#1e3a5f"], [1, "#06b6d4"]],
        showscale=False,
        xgap=2,
        ygap=2,
    )


def make_animated_fig(weights, values, names, capacity, steps, chosen):
    n = len(weights)
    n_steps = len(steps)

    # ── Figure principale : deux sous-graphiques (items + DP table) ───────────
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.35, 0.65],
        subplot_titles=[
            "Objets — Valeur & Poids",
            "Table de programmation dynamique",
        ],
        vertical_spacing=0.12,
    )

    # Frame initiale
    si0, sw0, dp0, act0 = steps[0]
    for tr in make_items_bar(weights, values, n, [], si0 - 1):
        fig.add_trace(tr, row=1, col=1)
    fig.add_trace(
        make_dp_heatmap(dp0[: si0 + 1, : capacity + 1], si0, sw0), row=2, col=1
    )

    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        font=dict(color="#e2e8f0", family="DM Sans"),
        barmode="group",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e1e2e"),
        xaxis2=dict(title="Capacité →", showgrid=False, tickfont=dict(size=9)),
        yaxis2=dict(title="Objets ↓", showgrid=False, tickfont=dict(size=9)),
        legend=dict(bgcolor="#111118", bordercolor="#1e1e2e", x=1.01),
        margin=dict(l=40, r=120, t=80, b=80),
        height=580,
        annotations=[
            dict(
                text="Objets — Valeur & Poids",
                x=0.5,
                y=1.04,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(color="#94a3b8", size=12),
            ),
            dict(
                text="Table de programmation dynamique",
                x=0.5,
                y=0.6,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(color="#94a3b8", size=12),
            ),
            dict(
                text=act0,
                x=0.5,
                y=1.09,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(color="#fcd34d", size=11, family="DM Sans"),
                align="center",
            ),
        ],
        # Cellule active (shape)
        shapes=[
            dict(
                type="rect",
                x0=sw0 - 0.5,
                x1=sw0 + 0.5,
                y0=si0 - 0.5,
                y1=si0 + 0.5,
                line=dict(color="#f59e0b", width=3),
                fillcolor="rgba(245,158,11,0.15)",
                xref="x2",
                yref="y2",
            )
        ],
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                y=-0.12,
                x=0.5,
                xanchor="center",
                buttons=[
                    dict(
                        label="▶  Démarrer",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=80, redraw=True),
                                transition=dict(duration=40, easing="linear"),
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
                    prefix="Cellule : ",
                    font=dict(color="#94a3b8", family="Space Mono", size=11),
                    visible=True,
                    xanchor="center",
                ),
                pad=dict(t=45, b=5),
                len=0.9,
                x=0.05,
                bgcolor="#111118",
                bordercolor="#1e1e2e",
                tickcolor="#334155",
                font=dict(color="#64748b", size=8),
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [f"k{k}"],
                            dict(
                                mode="immediate",
                                frame=dict(duration=80, redraw=True),
                                transition=dict(duration=40),
                            ),
                        ],
                        label=str(k),
                    )
                    for k in range(n_steps)
                ],
            )
        ],
    )

    # Frames
    frames = []
    for k, (si, sw, dp_s, action) in enumerate(steps):
        done_chosen = chosen if k == n_steps - 1 else []
        bar_traces = make_items_bar(weights, values, n, done_chosen, si - 1)
        dp_trace = make_dp_heatmap(dp_s[: si + 1, : capacity + 1], si, sw)
        frames.append(
            go.Frame(
                name=f"k{k}",
                data=bar_traces + [dp_trace],
                traces=[0, 1, 2],
                layout=go.Layout(
                    annotations=[
                        dict(
                            text="Objets — Valeur & Poids",
                            x=0.5,
                            y=1.04,
                            xref="paper",
                            yref="paper",
                            showarrow=False,
                            font=dict(color="#94a3b8", size=12),
                        ),
                        dict(
                            text="Table de programmation dynamique",
                            x=0.5,
                            y=0.6,
                            xref="paper",
                            yref="paper",
                            showarrow=False,
                            font=dict(color="#94a3b8", size=12),
                        ),
                        dict(
                            text=action,
                            x=0.5,
                            y=1.09,
                            xref="paper",
                            yref="paper",
                            showarrow=False,
                            font=dict(
                                color="#fcd34d", size=11, family="DM Sans"
                            ),
                            align="center",
                        ),
                    ],
                    shapes=[
                        dict(
                            type="rect",
                            x0=sw - 0.5,
                            x1=sw + 0.5,
                            y0=si - 0.5,
                            y1=si + 0.5,
                            line=dict(color="#f59e0b", width=3),
                            fillcolor="rgba(245,158,11,0.15)",
                            xref="x2",
                            yref="y2",
                        )
                    ],
                ),
            )
        )
    fig.frames = frames
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);color:#fcd34d;">🎒 SAC À DOS</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-title">Sac à Dos 0/1</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="page-desc">Programmation dynamique : la cellule jaune montre la décision en cours. Utilisez <b>▶ Démarrer</b> ou le slider pour avancer.</div>',
    unsafe_allow_html=True,
)

DEFAULT_ITEMS = [
    {"nom": "Ordinateur", "poids": 3, "valeur": 4},
    {"nom": "Téléphone", "poids": 1, "valeur": 3},
    {"nom": "Tablette", "poids": 2, "valeur": 3},
    {"nom": "Appareil photo", "poids": 4, "valeur": 5},
    {"nom": "Montre", "poids": 1, "valeur": 2},
]

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    capacity = st.slider("Capacité du sac (kg)", 3, 15, 6)
    n_items = st.slider("Nombre d'objets", 3, 8, 5)

    st.markdown("---")
    st.markdown("#### 📦 Objets")
    items_data = []
    for i in range(n_items):
        d = (
            DEFAULT_ITEMS[i]
            if i < len(DEFAULT_ITEMS)
            else {"nom": f"Objet {i+1}", "poids": i + 1, "valeur": i + 2}
        )
        with st.expander(f"Objet {i+1} — {d['nom']}"):
            p = st.number_input(
                "Poids (kg)",
                min_value=1,
                max_value=capacity,
                value=min(d["poids"], capacity),
                key=f"p{i}",
            )
            v = st.number_input(
                "Valeur (€)",
                min_value=1,
                max_value=20,
                value=d["valeur"],
                key=f"v{i}",
            )
            items_data.append((p, v, d["nom"]))

    weights = [x[0] for x in items_data]
    values = [x[1] for x in items_data]
    names = [x[2] for x in items_data]

    dp_final, steps, chosen = knapsack_dp(weights, values, capacity)
    total_value = sum(values[i] for i in chosen)
    total_weight = sum(weights[i] for i in chosen)

    st.markdown("---")
    st.metric("💰 Valeur optimale", f"{total_value} €")
    st.metric("⚖️ Poids utilisé", f"{total_weight} / {capacity} kg")
    st.metric("📦 Objets sélectionnés", f"{len(chosen)} / {n_items}")

with col_viz:
    fig = make_animated_fig(weights, values, names, capacity, steps, chosen)
    st.plotly_chart(
        fig, width="stretch", key=f"ks_{n_items}_{capacity}_{weights}"
    )

    if chosen:
        st.markdown("---")
        st.markdown("**✅ Objets dans la solution optimale :**")
        cs = st.columns(len(chosen))
        for idx, c in enumerate(chosen):
            cs[idx].markdown(
                f"""
            <div style="background:#111118;border:1px solid #10b981;border-radius:8px;
                        padding:0.6rem;text-align:center;font-size:0.8rem;">
                <div style="color:#10b981;font-size:1.3rem;">✓</div>
                <b>{names[c]}</b><br>
                <span style="color:#64748b;">{values[c]}€ · {weights[c]}kg</span>
            </div>
            """,
                unsafe_allow_html=True,
            )
