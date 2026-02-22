import streamlit as st
import plotly.graph_objects as go
import random, math, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Monte Carlo — Graphix", page_icon="🎲", layout="wide")
inject_css()
sidebar_nav()

# ── Simulation ────────────────────────────────────────────────────────────────
def monte_carlo_pi(n_points, seed=42):
    rng = random.Random(seed)
    inside, outside, pi_estimates = [], [], []
    for i in range(n_points):
        x = rng.uniform(-1, 1)
        y = rng.uniform(-1, 1)
        if x*x + y*y <= 1:
            inside.append((x, y))
        else:
            outside.append((x, y))
        pi_estimates.append(4 * len(inside) / (i + 1))
    return inside, outside, pi_estimates

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;">🎲 MONTE CARLO</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Estimation de π par Monte Carlo</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Lancer des points aléatoires dans un carré 2×2. La proportion tombant dans le cercle inscrit de rayon 1 converge vers <b>π/4</b>. Plus il y a de points, plus l\'estimation est précise — c\'est la <b>loi des grands nombres</b>.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    n_points = st.select_slider("Nombre de points",
                                options=[100, 500, 1000, 2000, 5000, 10000, 50000],
                                value=2000)
    seed = st.slider("Graine aléatoire", 0, 99, 42)

    if st.button("🎲 Lancer / Relancer la simulation", use_container_width=True, type="primary"):
        st.session_state.mc_seed = seed
        st.session_state.mc_n    = n_points
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🧠 Principe")
    st.markdown("""
    <div class="info-box" style="border-left-color:#ef4444; font-size:0.82rem;">
    Un cercle de rayon 1 est inscrit dans un carré 2×2.<br><br>
    Aire cercle = <b>π·r²</b> = π<br>
    Aire carré  = <b>(2r)²</b> = 4<br><br>
    Ratio = π/4<br><br>
    Si on lance N points uniformément :<br>
    <b>π ≈ 4 × (points dans cercle) / N</b><br><br>
    La convergence est en <b>O(1/√N)</b> — il faut 100× plus de points pour gagner un chiffre de précision.
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("🔵 **Cyan** — Dans le cercle (x²+y²≤1)")
    st.markdown("🔴 **Rouge** — Hors du cercle")
    st.markdown("🟡 **Ligne jaune** — π réel (3.14159…)")

with col_viz:
    # Utiliser les params de session si disponibles
    active_n    = getattr(st.session_state, "mc_n",    n_points)
    active_seed = getattr(st.session_state, "mc_seed", seed)

    inside, outside, pi_estimates = monte_carlo_pi(active_n, active_seed)
    n_in  = len(inside)
    n_out = len(outside)
    pi_est = pi_estimates[-1]
    error  = abs(pi_est - math.pi)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("π estimé",    f"{pi_est:.5f}")
    m2.metric("π réel",      f"{math.pi:.5f}")
    m3.metric("Erreur abs.",  f"{error:.5f}")
    m4.metric("Points dans cercle", f"{n_in}/{active_n}")

    st.markdown("---")

    # Sous-échantillonnage pour l'affichage
    MAX_DISP = 4000
    step_s = max(1, active_n // MAX_DISP)
    in_x  = [p[0] for p in inside[::step_s]]
    in_y  = [p[1] for p in inside[::step_s]]
    out_x = [p[0] for p in outside[::step_s]]
    out_y = [p[1] for p in outside[::step_s]]

    theta = [2*math.pi*i/360 for i in range(361)]
    cx    = [math.cos(t) for t in theta]
    cy    = [math.sin(t) for t in theta]

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### 🎯 Nuage de points")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=out_x, y=out_y, mode='markers',
                                 marker=dict(size=2, color='#ef4444', opacity=0.4),
                                 name=f"Hors cercle ({n_out:,})"))
        fig.add_trace(go.Scatter(x=in_x,  y=in_y,  mode='markers',
                                 marker=dict(size=2, color='#06b6d4', opacity=0.4),
                                 name=f"Dans cercle ({n_in:,})"))
        fig.add_trace(go.Scatter(x=cx, y=cy, mode='lines',
                                 line=dict(color='#f59e0b', width=2),
                                 name="Cercle unitaire"))
        fig.add_shape(type="rect", x0=-1, y0=-1, x1=1, y1=1,
                      line=dict(color="#334155", width=1.5))
        fig.update_layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            xaxis=dict(showgrid=False, range=[-1.08,1.08], zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, range=[-1.08,1.08], zeroline=False, showticklabels=False, scaleanchor='x'),
            legend=dict(bgcolor='#111118', bordercolor='#1e1e2e', font=dict(size=10, color='#94a3b8')),
            margin=dict(l=10,r=10,t=10,b=10), height=380,
        )
        st.plotly_chart(fig, use_container_width=True, key=f"mc_scatter_{active_n}_{active_seed}")

    with col_b:
        st.markdown("##### 📈 Convergence vers π")
        step_c = max(1, active_n // 600)
        x_conv = list(range(1, active_n+1, step_c))
        y_conv = pi_estimates[::step_c]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=x_conv, y=y_conv, mode='lines',
                                  line=dict(color='#06b6d4', width=1.5), showlegend=False))
        fig2.add_hline(y=math.pi, line=dict(color='#f59e0b', width=2, dash='dash'),
                       annotation_text="π = 3.14159…",
                       annotation_font=dict(color='#f59e0b', size=10))
        fig2.add_hrect(y0=math.pi-0.05, y1=math.pi+0.05,
                       fillcolor="rgba(245,158,11,0.07)", line_width=0)
        fig2.update_layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            font=dict(color='#e2e8f0', family='DM Sans'),
            xaxis=dict(showgrid=True, gridcolor='#1e1e2e', title="Nombre de points"),
            yaxis=dict(showgrid=True, gridcolor='#1e1e2e', title="Estimation de π",
                       range=[2.6, 3.7]),
            margin=dict(l=50,r=10,t=10,b=40), height=380,
        )
        st.plotly_chart(fig2, use_container_width=True, key=f"mc_conv_{active_n}_{active_seed}")

    # Table de précision
    st.markdown("---")
    st.markdown("##### 📊 Précision selon le nombre de points")
    checkpoints = [c for c in [100, 500, 1000, 5000, 10000, 50000] if c <= active_n]
    if active_n not in checkpoints: checkpoints.append(active_n)
    checkpoints = sorted(set(checkpoints))
    cp_cols = st.columns(len(checkpoints))
    for col, cp in zip(cp_cols, checkpoints):
        est = pi_estimates[cp-1]
        err = abs(est - math.pi)
        c   = "#10b981" if err < 0.01 else "#f59e0b" if err < 0.1 else "#ef4444"
        col.markdown(f"""
        <div style="text-align:center;background:#111118;border:1px solid #1e1e2e;
                    border-top:3px solid {c};border-radius:6px;padding:8px 4px;
                    font-family:'Space Mono',monospace;font-size:0.72rem;">
            <div style="color:#64748b;">n={cp:,}</div>
            <div style="color:#e2e8f0;font-weight:700;">{est:.4f}</div>
            <div style="color:{c};">±{err:.4f}</div>
        </div>""", unsafe_allow_html=True)
