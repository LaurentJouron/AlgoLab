import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Lissajous — Graphix", page_icon="🐢", layout="wide")
inject_css()
sidebar_nav()

PRESETS_LIS = {
    "Cercle":           (1, 1, 0.0),
    "Ellipse":          (1, 1, 0.5),
    "Figure 8":         (1, 2, 0.0),
    "Trèfle":           (2, 3, 0.0),
    "Papillon":         (3, 4, 0.5),
    "Spirographe":      (5, 6, 0.0),
    "Étoile":           (5, 4, 1.2),
    "Chaos doux":       (7, 6, 0.9),
}

PALETTES_LIS = {
    "Violet → Cyan":  ["#7c3aed","#06b6d4"],
    "Rouge → Jaune":  ["#ef4444","#f59e0b"],
    "Vert → Bleu":    ["#10b981","#3b82f6"],
    "Rose → Orange":  ["#ec4899","#f97316"],
    "Mono Violet":    ["#7c3aed","#7c3aed"],
}

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);color:#a78bfa;">🐢 LISSAJOUS</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Courbes de Lissajous & Spirographe</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">x(t) = A·sin(a·t + δ), &nbsp; y(t) = B·sin(b·t). &nbsp; Ces courbes paramétriques tracent des formes radicalement différentes selon le rapport a/b et le déphasage δ. Simples à définir, infiniment variées.</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📐 Lissajous", "⚙️ Spirographe (Épicycloïde)"])

# ── Lissajous ─────────────────────────────────────────────────────────────────
with tab1:
    col_ctrl, col_viz = st.columns([1, 3])
    with col_ctrl:
        st.markdown("#### ⚙️ Paramètres")
        preset_l = st.selectbox("Preset", list(PRESETS_LIS.keys()), index=2, key="lis_preset")
        pa, pb, pd = PRESETS_LIS[preset_l]
        a   = st.slider("Fréquence a (x)", 1, 12, int(pa), key="lis_a")
        b   = st.slider("Fréquence b (y)", 1, 12, int(pb), key="lis_b")
        delta = st.slider("Déphasage δ (rad)", 0.0, 2*np.pi, float(pd), step=0.05, key="lis_delta",
                          format="%.2f")
        n_pts = st.select_slider("Points", options=[500,1000,2000,5000], value=2000, key="lis_pts")
        pal_l = st.selectbox("Couleur", list(PALETTES_LIS.keys()), key="lis_pal")
        show_anim = st.checkbox("Mode animation (tracer progressivement)", value=False, key="lis_anim")

        t_max = 2 * np.pi * np.lcm(a, b) if np.lcm(a, b) <= 60 else 4 * np.pi
        t = np.linspace(0, t_max, n_pts)
        x = np.sin(a * t + delta)
        y = np.sin(b * t)

        st.markdown("---")
        st.markdown(f"""
        <div class="info-box" style="border-left-color:#7c3aed; font-size:0.82rem;">
        <b>x(t)</b> = sin({a}·t + {delta:.2f})<br>
        <b>y(t)</b> = sin({b}·t)<br><br>
        Rapport a/b = <b>{a}/{b}</b><br>
        La courbe se ferme quand a/b est rationnel.<br><br>
        PGCD({a},{b}) = <b>{np.gcd(a,b)}</b> &nbsp;→&nbsp; <b>{a//np.gcd(a,b)}/{b//np.gcd(a,b)}</b> irréductible
        </div>""", unsafe_allow_html=True)

    with col_viz:
        c1, c2 = PALETTES_LIS[pal_l]
        colors = [f"rgba({int(c1[1:3],16)},{int(c1[3:5],16)},{int(c1[5:7],16)},{0.4+0.6*i/n_pts})"
                  for i in range(n_pts)]

        if show_anim:
            n_show = st.slider("Progression", 10, n_pts, n_pts//2, key="lis_prog")
            x_show, y_show = x[:n_show], y[:n_show]
        else:
            x_show, y_show = x, y

        # Dégradé via segments colorés par position
        fig = go.Figure()
        step_seg = max(1, len(x_show) // 200)
        for i in range(0, len(x_show)-step_seg, step_seg):
            t_ratio = i / len(x_show)
            r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
            r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
            r = int(r1*(1-t_ratio)+r2*t_ratio)
            g_c = int(g1*(1-t_ratio)+g2*t_ratio)
            b_c = int(b1*(1-t_ratio)+b2*t_ratio)
            seg_color = f"#{r:02x}{g_c:02x}{b_c:02x}"
            fig.add_trace(go.Scatter(
                x=x_show[i:i+step_seg+1], y=y_show[i:i+step_seg+1],
                mode='lines', line=dict(color=seg_color, width=1.5),
                showlegend=False, hoverinfo='none',
            ))
        # Point courant
        if show_anim:
            fig.add_trace(go.Scatter(x=[x_show[-1]], y=[y_show[-1]], mode='markers',
                                     marker=dict(size=10, color='#f59e0b',
                                                 line=dict(color='#0a0a0f', width=1.5)),
                                     showlegend=False))
        fig.update_layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            xaxis=dict(showgrid=True, gridcolor='#1e1e2e', zeroline=False,
                       range=[-1.15,1.15], showticklabels=False),
            yaxis=dict(showgrid=True, gridcolor='#1e1e2e', zeroline=False,
                       range=[-1.15,1.15], showticklabels=False, scaleanchor='x'),
            margin=dict(l=10, r=10, t=10, b=10), height=480,
        )
        st.plotly_chart(fig, use_container_width=True,
                        key=f"lis_{a}_{b}_{delta:.2f}_{n_pts}_{pal_l}")

        st.markdown(f"""
        <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:8px;">
        {"".join(f'<div style="background:#111118;border:1px solid #1e1e2e;border-top:3px solid {c1 if i%2==0 else c2};border-radius:6px;padding:6px 12px;font-family:Space Mono,monospace;font-size:0.72rem;color:#94a3b8;">{lbl}</div>'
        for i,(lbl) in enumerate([f"a={a}", f"b={b}", f"δ={delta:.2f}", f"{n_pts} pts", f"t∈[0,{t_max:.1f}]"]))}
        </div>""", unsafe_allow_html=True)

# ── Épicycloïde (spirographe) ──────────────────────────────────────────────────
with tab2:
    col_ctrl2, col_viz2 = st.columns([1, 3])
    with col_ctrl2:
        st.markdown("#### ⚙️ Paramètres")
        R_val  = st.slider("Rayon grand cercle (R)", 3, 10, 5, key="epi_R")
        r_val  = st.slider("Rayon petit cercle (r)", 1, R_val, 2, key="epi_r")
        d_val  = st.slider("Distance au crayon (d)", 1, r_val+2, r_val, key="epi_d")
        pal_e  = st.selectbox("Couleur", list(PALETTES_LIS.keys()), index=1, key="epi_pal")
        n_epi  = st.select_slider("Points", options=[1000,3000,6000], value=3000, key="epi_pts")

        lcm_rR = int(R_val * r_val / np.gcd(R_val, r_val))
        t_e = np.linspace(0, 2 * np.pi * lcm_rR / r_val, n_epi)
        x_e = (R_val - r_val) * np.cos(t_e) + d_val * np.cos((R_val - r_val) / r_val * t_e)
        y_e = (R_val - r_val) * np.sin(t_e) - d_val * np.sin((R_val - r_val) / r_val * t_e)

        st.markdown("---")
        st.markdown(f"""
        <div class="info-box" style="border-left-color:#f59e0b; font-size:0.82rem;">
        Un petit cercle (r={r_val}) roule à l'intérieur d'un grand cercle (R={R_val}).<br>
        Un crayon à distance d={d_val} du centre du petit cercle trace la courbe.<br><br>
        <b>Pétales :</b> {R_val // np.gcd(R_val, r_val)}<br>
        <b>Cycles pour fermer :</b> {lcm_rR // r_val}
        </div>""", unsafe_allow_html=True)

    with col_viz2:
        c1e, c2e = PALETTES_LIS[pal_e]
        fig2 = go.Figure()
        step_e = max(1, len(x_e) // 200)
        for i in range(0, len(x_e)-step_e, step_e):
            t_ratio = i / len(x_e)
            r1,g1,b1 = int(c1e[1:3],16),int(c1e[3:5],16),int(c1e[5:7],16)
            r2,g2,b2 = int(c2e[1:3],16),int(c2e[3:5],16),int(c2e[5:7],16)
            rc = int(r1*(1-t_ratio)+r2*t_ratio)
            gc2 = int(g1*(1-t_ratio)+g2*t_ratio)
            bc2 = int(b1*(1-t_ratio)+b2*t_ratio)
            fig2.add_trace(go.Scatter(
                x=x_e[i:i+step_e+1], y=y_e[i:i+step_e+1],
                mode='lines', line=dict(color=f"#{rc:02x}{gc2:02x}{bc2:02x}", width=1.5),
                showlegend=False, hoverinfo='none',
            ))
        fig2.update_layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor='x'),
            margin=dict(l=10, r=10, t=10, b=10), height=480,
        )
        st.plotly_chart(fig2, use_container_width=True,
                        key=f"epi_{R_val}_{r_val}_{d_val}_{pal_e}")
