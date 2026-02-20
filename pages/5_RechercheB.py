import streamlit as st
import plotly.graph_objects as go
import random, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Recherche Binaire — Graphix", page_icon="🔍", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithme ────────────────────────────────────────────────────────────────

def binary_search_steps(arr, target):
    steps = []
    lo, hi = 0, len(arr) - 1

    while lo <= hi:
        mid = (lo + hi) // 2
        steps.append({
            "arr": arr, "lo": lo, "hi": hi, "mid": mid,
            "target": target, "found": None,
            "desc": f"Milieu = index {mid} → valeur <b>{arr[mid]}</b> | Recherche de <b>{target}</b> dans [{lo} … {hi}]"
        })
        if arr[mid] == target:
            steps.append({
                "arr": arr, "lo": lo, "hi": hi, "mid": mid,
                "target": target, "found": mid,
                "desc": f"✅ Trouvé ! <b>{target}</b> est à l'index <b>{mid}</b>"
            })
            return steps
        elif arr[mid] < target:
            lo = mid + 1
            steps.append({
                "arr": arr, "lo": lo, "hi": hi, "mid": mid,
                "target": target, "found": None,
                "desc": f"{arr[mid]} &lt; {target} → on cherche à droite : [{lo} … {hi}]"
            })
        else:
            hi = mid - 1
            steps.append({
                "arr": arr, "lo": lo, "hi": hi, "mid": mid,
                "target": target, "found": None,
                "desc": f"{arr[mid]} &gt; {target} → on cherche à gauche : [{lo} … {hi}]"
            })

    steps.append({
        "arr": arr, "lo": lo, "hi": hi, "mid": -1,
        "target": target, "found": -1,
        "desc": f"❌ <b>{target}</b> n'existe pas dans le tableau"
    })
    return steps

def make_frame(s):
    arr    = s["arr"]
    lo, hi = s["lo"], s["hi"]
    mid    = s["mid"]
    found  = s["found"]
    n      = len(arr)

    colors = []
    for i in range(n):
        if found is not None and found >= 0 and i == found:
            colors.append("#10b981")
        elif i == mid and found is None:
            colors.append("#f59e0b")
        elif lo <= i <= hi:
            colors.append("#7c3aed")
        else:
            colors.append("#1e293b")

    border_colors = ["#ffffff" if i == mid else c for i, c in enumerate(colors)]

    return go.Bar(
        x=list(range(n)), y=arr,
        marker=dict(color=colors, line=dict(color=border_colors, width=[2 if i == mid else 0 for i in range(n)])),
        text=arr, textposition='outside',
        textfont=dict(color='#e2e8f0', size=10, family='Space Mono'),
    )

def make_animated_fig(steps, arr):
    ymax = max(arr) + 10

    fig = go.Figure(
        data=[make_frame(steps[0])],
        layout=go.Layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            font=dict(color='#e2e8f0', family='DM Sans'),
            xaxis=dict(showgrid=False, showticklabels=True, zeroline=False,
                       tickfont=dict(size=9, color='#64748b', family='Space Mono')),
            yaxis=dict(showgrid=True, gridcolor='#1e1e2e', zeroline=False, range=[0, ymax]),
            margin=dict(l=20, r=20, t=55, b=80),
            height=380, bargap=0.1,
            annotations=[dict(x=0.5, y=1.08, xref='paper', yref='paper',
                              text=steps[0]["desc"], showarrow=False,
                              font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')],
            updatemenus=[dict(
                type="buttons", showactive=False, y=-0.22, x=0.5, xanchor="center",
                buttons=[
                    dict(label="▶  Démarrer", method="animate",
                         args=[None, dict(frame=dict(duration=800, redraw=True),
                                         transition=dict(duration=200, easing="cubic-in-out"),
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
                font=dict(color="#64748b", size=9),
                steps=[dict(method="animate",
                            args=[[f"rb{k}"], dict(mode="immediate", frame=dict(duration=800, redraw=True),
                                                   transition=dict(duration=200))],
                            label=str(k)) for k in range(len(steps))],
            )],
        ),
        frames=[
            go.Frame(
                name=f"rb{k}",
                data=[make_frame(s)],
                layout=go.Layout(annotations=[dict(
                    x=0.5, y=1.08, xref='paper', yref='paper',
                    text=s["desc"], showarrow=False,
                    font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')])
            )
            for k, s in enumerate(steps)
        ],
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);color:#a78bfa;">🔍 RECHERCHE BINAIRE</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Recherche Binaire</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Trouver un élément dans un tableau trié en divisant l\'espace de recherche par deux à chaque étape. <b>Violet</b> = zone active, <b>jaune</b> = milieu testé, <b>vert</b> = trouvé, <b>sombre</b> = éliminé.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    n      = st.slider("Taille du tableau", 8, 30, 15)
    custom = st.checkbox("Choisir la valeur cible manuellement", value=False)

    if st.button("🎲 Générer nouveau tableau", width='stretch'):
        st.session_state.rb_arr = sorted(random.sample(range(1, 200), n))

    if "rb_arr" not in st.session_state or len(st.session_state.rb_arr) != n:
        st.session_state.rb_arr = sorted(random.sample(range(1, 200), n))

    arr = st.session_state.rb_arr

    if custom:
        target = st.number_input("Valeur à chercher", min_value=1, max_value=200, value=arr[n//2])
    else:
        target_idx = st.slider("Index de la valeur cible", 0, n-1, n//3)
        target = arr[target_idx]
        st.markdown(f'<div class="info-box" style="border-left-color:#7c3aed;">Valeur cible : <b style="color:#a78bfa;">{target}</b> (index {target_idx})</div>', unsafe_allow_html=True)

    steps = binary_search_steps(arr, target)
    st.markdown(f'<span class="complexity-badge">O(log n) — {len(steps)} étapes</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">n = {n} → log₂(n) ≈ {n.bit_length()-1}</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🧠 Principe")
    st.markdown("""
    <div class="info-box" style="border-left-color:#7c3aed; font-size:0.82rem;">
    1. Calculer le milieu <b>mid = (lo + hi) / 2</b><br>
    2. Si <b>arr[mid] == cible</b> → trouvé ✅<br>
    3. Si <b>arr[mid] &lt; cible</b> → chercher à droite<br>
    4. Si <b>arr[mid] &gt; cible</b> → chercher à gauche<br>
    5. Répéter jusqu'à trouver ou épuiser
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎨 Légende")
    st.markdown("🟣 **Violet** — Zone de recherche active")
    st.markdown("🟡 **Jaune** — Élément du milieu testé")
    st.markdown("🟢 **Vert** — Élément trouvé")
    st.markdown("⬛ **Sombre** — Zone éliminée")

with col_viz:
    fig = make_animated_fig(steps, arr)
    st.plotly_chart(fig, width='stretch', key=f"rb_{arr}_{target}")
