import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Mandelbrot — Graphix", page_icon="🌀", layout="wide")
inject_css()
sidebar_nav()

# ── Calcul ─────────────────────────────────────────────────────────────────────
@st.cache_data
def compute_mandelbrot(xmin, xmax, ymin, ymax, width=400, height=350, max_iter=80):
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    C = x[np.newaxis, :] + 1j * y[:, np.newaxis]
    Z = np.zeros_like(C)
    M = np.zeros(C.shape, dtype=float)
    for i in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask] ** 2 + C[mask]
        M[mask] += 1
    return M

PRESETS = {
    "Vue globale":        (-2.5, 1.0, -1.25, 1.25),
    "Vallée du dragon":   (-0.75, -0.7, 0.1, 0.15),
    "Spirale dorée":      (-0.5, -0.4, 0.55, 0.65),
    "Mini Mandelbrot":    (-1.78, -1.72, -0.03, 0.03),
    "Tentacules":         (0.25, 0.35, 0.0, 0.1),
    "Bord infini":        (-0.22, -0.17, 1.03, 1.08),
}

COLORSCALES = {
    "Inferno":    "Inferno",
    "Viridis":    "Viridis",
    "Plasma":     "Plasma",
    "Twilight":   [[0,"#0a0a0f"],[0.25,"#7c3aed"],[0.5,"#06b6d4"],[0.75,"#10b981"],[1,"#f59e0b"]],
    "Rouge-Noir": [[0,"#0a0a0f"],[0.4,"#7f1d1d"],[0.7,"#dc2626"],[0.9,"#fca5a5"],[1,"#ffffff"]],
}

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);color:#a78bfa;">🌀 MANDELBROT</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Fractale de Mandelbrot</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Un nombre complexe c appartient à l\'ensemble de Mandelbrot si la suite z_{n+1} = z²_n + c ne diverge pas. La couleur d\'un pixel = le nombre d\'itérations avant divergence. Complexité infinie à chaque niveau de zoom.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### 🔭 Navigation")
    preset = st.selectbox("Zone prédéfinie", list(PRESETS.keys()))
    xmin0, xmax0, ymin0, ymax0 = PRESETS[preset]

    st.markdown("#### 🎨 Rendu")
    colorscale_name = st.selectbox("Palette de couleurs", list(COLORSCALES.keys()), index=3)
    max_iter = st.select_slider("Itérations max", options=[40, 60, 80, 120, 200], value=80)
    resolution = st.select_slider("Résolution", options=["Rapide (300px)", "Normale (450px)", "Haute (600px)"], value="Normale (450px)")
    width  = {"Rapide (300px)": 300, "Normale (450px)": 450, "Haute (600px)": 600}[resolution]
    height = int(width * 0.75)

    st.markdown("---")
    st.markdown("#### 🔍 Zoom manuel")
    xmin = st.number_input("x min", value=float(xmin0), format="%.6f", step=0.01)
    xmax = st.number_input("x max", value=float(xmax0), format="%.6f", step=0.01)
    ymin = st.number_input("y min", value=float(ymin0), format="%.6f", step=0.01)
    ymax = st.number_input("y max", value=float(ymax0), format="%.6f", step=0.01)

    st.markdown("---")
    st.markdown("""
    <div class="info-box" style="border-left-color:#7c3aed; font-size:0.82rem;">
    <b>Suite :</b> z₀ = 0, z_{n+1} = z²_n + c<br><br>
    Si |z_n| > 2 pour un certain n → <b>c diverge</b> (coloré)<br>
    Si |z_n| ≤ 2 après max_iter → <b>c ∈ Mandelbrot</b> (noir)<br><br>
    La bordure entre les deux est de complexité <b>fractale infinie</b>.
    </div>""", unsafe_allow_html=True)

with col_viz:
    with st.spinner("Calcul en cours…"):
        M = compute_mandelbrot(xmin, xmax, ymin, ymax, width, height, max_iter)

    fig = go.Figure(go.Heatmap(
        z=M,
        x=np.linspace(xmin, xmax, width),
        y=np.linspace(ymin, ymax, height),
        colorscale=COLORSCALES[colorscale_name],
        showscale=False,
        hovertemplate="Re=%{x:.4f}, Im=%{y:.4f}<br>Itérations=%{z}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#0a0a0f',
        xaxis=dict(showgrid=False, title="Re(c)", tickfont=dict(color='#475569', size=9)),
        yaxis=dict(showgrid=False, title="Im(c)", tickfont=dict(color='#475569', size=9),
                   scaleanchor='x'),
        margin=dict(l=50, r=10, t=10, b=50), height=500,
    )
    st.plotly_chart(fig, use_container_width=True, key=f"mandel_{preset}_{colorscale_name}_{max_iter}_{width}_{xmin:.4f}_{xmax:.4f}_{ymin:.4f}_{ymax:.4f}")

    # Info zone
    c_center = complex((xmin+xmax)/2, (ymin+ymax)/2)
    zoom_factor = round(3.5 / max(xmax - xmin, 1e-10), 1)
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Centre Re", f"{c_center.real:.5f}")
    col_b.metric("Centre Im", f"{c_center.imag:.5f}")
    col_c.metric("Zoom ×", f"{zoom_factor:,.0f}")

    st.markdown(f"""
    <div class="info-box" style="border-left-color:#7c3aed; font-size:0.82rem;">
    💡 <b>Astuce :</b> Modifie les valeurs x/y min/max pour zoomer sur une zone précise.
    Les zones les plus intéressantes se trouvent sur le <b>bord</b> de l'ensemble (entre le noir et les couleurs).
    Essaie les presets "Vallée du dragon" ou "Mini Mandelbrot" pour voir des copies miniatures de l'ensemble entier !
    </div>""", unsafe_allow_html=True)
