import streamlit as st
import plotly.graph_objects as go
import random, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Tri — AlgoLab", page_icon="📊", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithmes ───────────────────────────────────────────────────────────────

def bubble_sort_steps(arr):
    steps, descriptions = [], []
    a = arr.copy()
    n = len(a)
    for i in range(n):
        for j in range(0, n-i-1):
            steps.append((a.copy(), j, j+1, list(range(n-i, n))))
            descriptions.append(f"Comparaison : a[{j}]={a[j]} et a[{j+1}]={a[j+1]}")
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                steps.append((a.copy(), j, j+1, list(range(n-i, n))))
                descriptions.append(f"Échange : a[{j}] ↔ a[{j+1}] → {a[j+1]} avant {a[j]}")
    steps.append((a.copy(), -1, -1, list(range(n))))
    descriptions.append("✅ Tableau trié !")
    return steps, descriptions

def merge_sort_steps(arr):
    steps, descriptions = [], []
    a = arr.copy()
    def merge_sort(arr, left):
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        L = merge_sort(arr[:mid], left)
        R = merge_sort(arr[mid:], left + mid)
        merged = []
        i = j = 0
        while i < len(L) and j < len(R):
            steps.append((a.copy(), left+i, left+mid+j, []))
            descriptions.append(f"Fusion : comparaison L[{i}]={L[i]} vs R[{j}]={R[j]}")
            if L[i] <= R[j]:
                merged.append(L[i]); i += 1
            else:
                merged.append(R[j]); j += 1
        merged.extend(L[i:]); merged.extend(R[j:])
        for k, val in enumerate(merged):
            a[left+k] = val
        steps.append((a.copy(), -1, -1, list(range(left, left+len(merged)))))
        descriptions.append(f"Sous-tableau [{left}:{left+len(merged)}] fusionné")
        return merged
    merge_sort(a, 0)
    return steps, descriptions

def quick_sort_steps(arr):
    steps, descriptions = [], []
    a = arr.copy()
    def quick_sort(lo, hi):
        if lo >= hi: return
        pivot = a[hi]
        i = lo
        steps.append((a.copy(), hi, -1, []))
        descriptions.append(f"Pivot choisi : a[{hi}] = {pivot}")
        for j in range(lo, hi):
            steps.append((a.copy(), j, hi, []))
            descriptions.append(f"Comparaison : a[{j}]={a[j]} vs pivot={pivot}")
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                steps.append((a.copy(), i, j, []))
                descriptions.append(f"Échange : a[{i}]={a[i]} ↔ a[{j}]={a[j]}")
                i += 1
        a[i], a[hi] = a[hi], a[i]
        steps.append((a.copy(), i, hi, [i]))
        descriptions.append(f"Pivot {pivot} placé en position {i} ✓")
        quick_sort(lo, i-1)
        quick_sort(i+1, hi)
    quick_sort(0, len(a)-1)
    steps.append((a.copy(), -1, -1, list(range(len(a)))))
    descriptions.append("✅ Tableau trié !")
    return steps, descriptions

def get_colors(arr, idx1, idx2, sorted_indices, accent):
    colors = []
    for i in range(len(arr)):
        if i in sorted_indices: colors.append("#10b981")
        elif i == idx1:         colors.append("#f59e0b")
        elif i == idx2:         colors.append("#ef4444")
        else:                   colors.append(accent)
    return colors

def make_animated_fig(steps, descs, accent):
    arr0, i1, i2, si = steps[0]
    n    = len(arr0)
    ymax = max(max(s[0]) for s in steps) + 8

    def frame_bar(arr, i1, i2, si):
        return go.Bar(
            x=list(range(n)), y=arr,
            marker_color=get_colors(arr, i1, i2, si, accent),
            marker_line_width=0,
            text=arr, textposition='outside',
            textfont=dict(color='#e2e8f0', size=10, family='Space Mono'),
        )

    fig = go.Figure(
        data=[frame_bar(arr0, i1, i2, si)],
        layout=go.Layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            font=dict(color='#e2e8f0', family='DM Sans'),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor='#1e1e2e', zeroline=False, range=[0, ymax]),
            margin=dict(l=20, r=20, t=50, b=70),
            height=380, bargap=0.15,
            annotations=[dict(
                x=0.5, y=1.06, xref='paper', yref='paper',
                text=descs[0], showarrow=False,
                font=dict(color='#94a3b8', size=12, family='DM Sans'),
                align='center',
            )],
            updatemenus=[dict(
                type="buttons", showactive=False,
                y=-0.18, x=0.5, xanchor="center",
                buttons=[
                    dict(label="▶  Démarrer", method="animate",
                         args=[None, dict(frame=dict(duration=220, redraw=True),
                                         transition=dict(duration=100, easing="cubic-in-out"),
                                         fromcurrent=True, mode="immediate")]),
                    dict(label="⏸  Pause", method="animate",
                         args=[[None], dict(frame=dict(duration=0, redraw=False),
                                            mode="immediate",
                                            transition=dict(duration=0))]),
                ],
                font=dict(color="#e2e8f0", family="Space Mono", size=12),
                bgcolor="#1e1e2e", bordercolor="#334155",
            )],
            sliders=[dict(
                active=0,
                currentvalue=dict(prefix="Étape : ",
                                  font=dict(color="#94a3b8", family="Space Mono", size=11),
                                  visible=True, xanchor="center"),
                pad=dict(t=45, b=5), len=0.9, x=0.05,
                bgcolor="#111118", bordercolor="#1e1e2e", tickcolor="#334155",
                font=dict(color="#64748b", size=9),
                steps=[dict(method="animate",
                            args=[[f"f{k}"], dict(mode="immediate",
                                                  frame=dict(duration=220, redraw=True),
                                                  transition=dict(duration=100))],
                            label=str(k)) for k in range(len(steps))],
            )],
        ),
        frames=[
            go.Frame(
                name=f"f{k}",
                data=[frame_bar(arr, i1, i2, si)],
                layout=go.Layout(annotations=[dict(
                    x=0.5, y=1.06, xref='paper', yref='paper',
                    text=descs[k], showarrow=False,
                    font=dict(color='#94a3b8', size=12, family='DM Sans'),
                    align='center',
                )])
            )
            for k, (arr, i1, i2, si) in enumerate(steps)
        ],
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);color:#a78bfa;">📊 ALGORITHMES DE TRI</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Tri & Comparaisons</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Observez chaque étape de 3 algorithmes de tri. Utilisez le bouton <b>▶ Démarrer</b> ou le slider pour naviguer. Les barres jaunes = comparaison, rouge = pivot, vert = trié.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    algo  = st.selectbox("Algorithme", ["Tri à Bulles", "Tri Fusion", "Tri Rapide"])
    n     = st.slider("Taille du tableau", 5, 20, 10)

    if st.button("🎲 Générer nouveau tableau", width='stretch'):
        st.session_state.tri_arr = random.sample(range(1, 100), n)

    if "tri_arr" not in st.session_state:
        st.session_state.tri_arr = random.sample(range(1, 100), n)

    arr    = st.session_state.tri_arr
    accent = {"Tri à Bulles": "#7c3aed", "Tri Fusion": "#06b6d4", "Tri Rapide": "#f59e0b"}[algo]

    if algo == "Tri à Bulles":
        steps, descs = bubble_sort_steps(arr)
        complexity   = "O(n²) comparaisons"
    elif algo == "Tri Fusion":
        steps, descs = merge_sort_steps(arr)
        complexity   = "O(n log n) — Stable"
    else:
        steps, descs = quick_sort_steps(arr)
        complexity   = "O(n log n) moyen"

    st.markdown(f'<span class="complexity-badge">{complexity}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{len(steps)} étapes</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎨 Légende")
    st.markdown("🟡 Élément comparé")
    st.markdown("🔴 Second élément / Pivot")
    st.markdown("🟢 Trié et en place")

with col_viz:
    fig = make_animated_fig(steps, descs, accent)
    st.plotly_chart(fig, width='stretch', key=f"tri_{algo}_{len(arr)}")
