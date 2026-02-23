import streamlit as st
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Crible d'Ératosthène — Graphix", page_icon="🔢", layout="wide"
)
inject_css()
sidebar_nav()


# ── Algorithme ────────────────────────────────────────────────────────────────
def sieve_steps(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    steps = []
    steps.append(
        {
            "is_prime": list(is_prime),
            "current": None,
            "multiples": [],
            "desc": "Initialisation — tous les nombres supposés premiers sauf 0 et 1",
        }
    )
    p = 2
    while p * p <= n:
        if is_prime[p]:
            multiples = list(range(p * p, n + 1, p))
            for m in multiples:
                is_prime[m] = False
            steps.append(
                {
                    "is_prime": list(is_prime),
                    "current": p,
                    "multiples": multiples,
                    "desc": f"Élimination des multiples de <b>{p}</b> : {p}², {p}²+{p}, … ({len(multiples)} nombre(s) barrés)",
                }
            )
        p += 1
    primes = [i for i in range(2, n + 1) if is_prime[i]]
    steps.append(
        {
            "is_prime": list(is_prime),
            "current": None,
            "multiples": [],
            "desc": f"✅ Terminé — <b>{len(primes)}</b> nombres premiers jusqu'à {n}",
        }
    )
    return steps


def make_sieve_fig(step, n, cols=20):
    is_prime = step["is_prime"]
    current = step["current"]
    multiples = set(step["multiples"])
    rows = (n // cols) + 1

    colors, texts, hovers = [], [], []
    for i in range(1, rows * cols + 1):
        if i > n:
            colors.append("rgba(0,0,0,0)")
            texts.append("")
            hovers.append("")
            continue
        if i == current:
            c = "#f59e0b"
        elif i in multiples:
            c = "#ef4444"
        elif i <= 1:
            c = "#1e293b"
        elif is_prime[i]:
            c = "#10b981"
        else:
            c = "#1e293b"
        colors.append(c)
        texts.append(str(i))
        hovers.append(f"{'Premier' if is_prime[i] else 'Composé'} : {i}")

    x_pos = [(i % cols) for i in range(len(texts))]
    y_pos = [-(i // cols) for i in range(len(texts))]

    fig = go.Figure()
    # Cellules (carrés colorés)
    for i, (x, y, c, t, h) in enumerate(
        zip(x_pos, y_pos, colors, texts, hovers)
    ):
        if not t:
            continue
        fig.add_shape(
            type="rect",
            x0=x - 0.45,
            y0=y - 0.45,
            x1=x + 0.45,
            y1=y + 0.45,
            fillcolor=c,
            line=dict(color="#0a0a0f", width=0.5),
        )
    # Textes - couleurs calculées AVANT filtrage pour garder la correspondance d'indices
    text_colors_all = [
        "#0a0a0f" if c in ("#10b981", "#f59e0b", "#ef4444") else "#475569"
        for c in colors
    ]
    visible_mask = [t != "" for t in texts]
    fig.add_trace(
        go.Scatter(
            x=[x for x, v in zip(x_pos, visible_mask) if v],
            y=[y for y, v in zip(y_pos, visible_mask) if v],
            mode="text",
            text=[t for t, v in zip(texts, visible_mask) if v],
            textfont=dict(
                size=10,
                family="Space Mono",
                color=[c for c, v in zip(text_colors_all, visible_mask) if v],
            ),
            hovertext=[h for h, v in zip(hovers, visible_mask) if v],
            hovertemplate="%{hovertext}<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#0a0a0f",
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-0.6, cols - 0.4],
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-(rows - 0.4), 0.6],
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        height=max(300, rows * 32),
    )
    return fig


def make_prime_distribution(primes, n):
    """Graphique de distribution des premiers."""
    if not primes:
        return go.Figure()
    gaps = [primes[i + 1] - primes[i] for i in range(len(primes) - 1)]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=list(range(2, len(primes))),
            y=gaps,
            marker=dict(
                color="#7c3aed", line=dict(color="#0a0a0f", width=0.5)
            ),
            name="Écart entre premiers consécutifs",
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        font=dict(color="#e2e8f0", family="DM Sans"),
        xaxis=dict(
            showgrid=True, gridcolor="#1e1e2e", title="Rang du premier"
        ),
        yaxis=dict(showgrid=True, gridcolor="#1e1e2e", title="Écart"),
        margin=dict(l=40, r=10, t=10, b=40),
        height=180,
        showlegend=False,
    )
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;">🔢 CRIBLE D\'ÉRATOSTHÈNE</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-title">Crible d\'Ératosthène</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-desc">Algorithme inventé vers 240 av. J.-C. pour trouver tous les nombres premiers jusqu\'à N. On barre successivement les multiples de chaque premier : ce qui reste est premier. Complexité O(n log log n) — quasi-linéaire.</div>',
    unsafe_allow_html=True,
)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    n_max = st.select_slider(
        "Chercher les premiers jusqu'à",
        options=[50, 100, 200, 300, 500],
        value=100,
    )
    steps_er = sieve_steps(n_max)
    primes_final = [i for i, p in enumerate(steps_er[-1]["is_prime"]) if p]

    st.markdown(
        f'<span class="complexity-badge">O(n log log n)</span>',
        unsafe_allow_html=True,
    )
    st.metric("Nombres premiers trouvés", len(primes_final))
    st.metric("Étapes d'élimination", len(steps_er) - 2)
    st.markdown("---")
    st.markdown(
        """
    <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
    <b>Pourquoi commencer à p² ?</b><br>
    Les multiples de p inférieurs à p² ont déjà été éliminés lors des passes précédentes (2p, 3p… ont des facteurs plus petits).<br><br>
    <b>Pourquoi s'arrêter à √n ?</b><br>
    Tout nombre composé n a un facteur premier ≤ √n. Donc au-delà de √n, il ne reste que des premiers.
    </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("🟢 **Vert** = nombre premier")
    st.markdown("🟡 **Jaune** = premier courant")
    st.markdown("🔴 **Rouge** = multiples barrés")
    st.markdown("🔵 **Sombre** = composé (éliminé)")
    st.markdown("*Glisse le slider pour voir chaque élimination*")

with col_viz:
    si = st.slider("Étape", 0, len(steps_er) - 1, 0, key="er_step")
    s = steps_er[si]
    st.markdown(
        f'<div class="info-box" style="border-left-color:#10b981;">{s["desc"]}</div>',
        unsafe_allow_html=True,
    )

    cols_grid = 20 if n_max <= 200 else 25
    fig = make_sieve_fig(s, n_max, cols=cols_grid)
    st.plotly_chart(fig, use_container_width=True, key=f"er_{si}_{n_max}")

    # Premiers trouvés jusqu'à maintenant
    found = [i for i, p in enumerate(s["is_prime"]) if p and i >= 2]
    if found:
        st.markdown(
            f"**{len(found)} premiers trouvés :** {', '.join(map(str, found[:40]))}"
            + (" …" if len(found) > 40 else "")
        )

    # Distribution des écarts
    if len(found) > 5:
        st.markdown("##### 📊 Écarts entre nombres premiers consécutifs")
        st.plotly_chart(
            make_prime_distribution(found, n_max),
            use_container_width=True,
            key=f"er_dist_{si}_{n_max}",
        )
