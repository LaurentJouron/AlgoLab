import streamlit as st
import plotly.graph_objects as go
import sys, os, time, random

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Dashboard — Graphix", page_icon="📈", layout="wide"
)
inject_css()
sidebar_nav()

# ── Benchmarks ────────────────────────────────────────────────────────────────


def bench_sorts(n=500):
    import time

    arr = random.sample(range(1, 10000), n)

    def bubble(a):
        a = a.copy()
        for i in range(len(a)):
            for j in range(len(a) - i - 1):
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
        return a

    def merge(a):
        if len(a) <= 1:
            return a
        m = len(a) // 2
        return merge_combine(merge(a[:m]), merge(a[m:]))

    def merge_combine(l, r):
        res, i, j = [], 0, 0
        while i < len(l) and j < len(r):
            if l[i] <= r[j]:
                res.append(l[i])
                i += 1
            else:
                res.append(r[j])
                j += 1
        return res + l[i:] + r[j:]

    results = {}
    for name, fn in [
        ("Tri Bulles", bubble),
        ("Tri Fusion", merge),
        ("Tri Rapide", sorted),
    ]:
        t0 = time.perf_counter()
        fn(arr)
        results[name] = (time.perf_counter() - t0) * 1000
    return results


def bench_search(n=10000):
    arr = list(range(n))
    target = random.randint(0, n - 1)

    def linear(a, t):
        for x in a:
            if x == t:
                return True
        return False

    def binary(a, t):
        lo, hi = 0, len(a) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if a[mid] == t:
                return True
            elif a[mid] < t:
                lo = mid + 1
            else:
                hi = mid - 1
        return False

    results = {}
    for name, fn in [
        ("Recherche Linéaire", linear),
        ("Recherche Binaire", binary),
    ]:
        t0 = time.perf_counter()
        for _ in range(100):
            fn(arr, target)
        results[name] = (time.perf_counter() - t0) * 10  # ms for 1 call
    return results


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.3);color:#67e8f9;">📈 TABLEAU DE BORD</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-title">Dashboard & Performances</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-desc">Comparaison des performances réelles des algorithmes mesurées sur ta machine. Les temps sont en millisecondes, moyennés sur plusieurs exécutions.</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Stats globales ────────────────────────────────────────────────────────────
st.markdown("### 📊 Vue d'ensemble de Graphix")
c1, c2, c3, c4 = st.columns(4)
c1.markdown(
    '<div class="stat-box"><div class="stat-num">28</div><div class="stat-label">Pages</div></div>',
    unsafe_allow_html=True,
)
c2.markdown(
    '<div class="stat-box"><div class="stat-num">50+</div><div class="stat-label">Algorithmes</div></div>',
    unsafe_allow_html=True,
)
c3.markdown(
    '<div class="stat-box"><div class="stat-num">7</div><div class="stat-label">Paradigmes</div></div>',
    unsafe_allow_html=True,
)
c4.markdown(
    '<div class="stat-box"><div class="stat-num">∞</div><div class="stat-label">Curiosité</div></div>',
    unsafe_allow_html=True,
)

# Paradigmes
st.markdown("---")
st.markdown("### 🧩 Paradigmes couverts")
p1, p2, p3, p4, p5, p6, p7 = st.columns(7)
paradigms = [
    (
        "Tri & Recherche",
        "#7c3aed",
        [
            "Tri Bulles/Fusion/Rapide",
            "Heap Sort",
            "Counting Sort",
            "Radix Sort",
            "Recherche Binaire",
        ],
    ),
    (
        "Récursivité & DP",
        "#06b6d4",
        [
            "Tours de Hanoï",
            "N-Reines",
            "Sac à Dos 0/1",
            "Fibonacci",
            "Levenshtein",
        ],
    ),
    (
        "Graphes & Chemins",
        "#10b981",
        [
            "Dijkstra",
            "Dijkstra Carte",
            "BFS",
            "DFS",
            "A*",
            "Labyrinthe",
            "Kruskal",
            "Prim",
            "PageRank",
        ],
    ),
    (
        "Automates & Struct",
        "#f59e0b",
        [
            "Jeu de la Vie",
            "Arbres Binaires",
            "Arbre Rouge-Noir",
            "Pile & File",
            "Table de Hachage",
        ],
    ),
    ("Crypto & Compress", "#ef4444", ["Huffman", "Chiffrement César", "RSA"]),
    (
        "Probabilités",
        "#ec4899",
        ["Monte Carlo (π)", "Algorithme Génétique", "Flood Fill"],
    ),
    (
        "Mathématiques",
        "#84cc16",
        ["Mandelbrot", "Lissajous", "Spirographe", "Crible Ératosthène"],
    ),
]
for col, (name, color, algos) in zip([p1, p2, p3, p4, p5, p6, p7], paradigms):
    items = "".join(
        f'<div style="color:#94a3b8;font-size:0.72rem;margin:2px 0;">• {a}</div>'
        for a in algos
    )
    col.markdown(
        f"""
    <div style="background:#111118;border:1px solid {color}33;border-left:3px solid {color};
                border-radius:8px;padding:0.8rem;min-height:220px;">
        <div style="color:{color};font-weight:700;font-size:0.82rem;margin-bottom:8px;">{name}</div>
        {items}
    </div>""",
        unsafe_allow_html=True,
    )

# ── Benchmark Tri ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### ⏱️ Comparateur de performances")

b1, b2 = st.columns(2)

with b1:
    st.markdown("#### 📊 Algorithmes de Tri")
    n_sort = st.slider("Taille du tableau", 100, 2000, 500, key="bench_n")
    if st.button(
        "🚀 Lancer le benchmark Tri", width="stretch", type="primary"
    ):
        with st.spinner("Mesure en cours…"):
            results = bench_sorts(n_sort)
        st.session_state.sort_bench = results

    if "sort_bench" in st.session_state:
        r = st.session_state.sort_bench
        names = list(r.keys())
        values = list(r.values())
        colors = ["#ef4444", "#06b6d4", "#10b981"]
        fig = go.Figure(
            go.Bar(
                x=names,
                y=values,
                marker_color=colors,
                text=[f"{v:.3f} ms" for v in values],
                textposition="outside",
                textfont=dict(color="#e2e8f0", size=11, family="Space Mono"),
            )
        )
        fig.update_layout(
            paper_bgcolor="#0a0a0f",
            plot_bgcolor="#111118",
            font=dict(color="#e2e8f0", family="DM Sans"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#1e1e2e", title="ms"),
            margin=dict(l=20, r=20, t=20, b=20),
            height=260,
        )
        st.plotly_chart(fig, width="stretch", key="bench_sort")
        fastest = min(r, key=r.get)
        slowest = max(r, key=r.get)
        ratio = r[slowest] / r[fastest]
        st.markdown(
            f'<div class="info-box" style="border-left-color:#10b981;">🏆 <b>{fastest}</b> est {ratio:.0f}× plus rapide que <b>{slowest}</b> sur {n_sort} éléments</div>',
            unsafe_allow_html=True,
        )

with b2:
    st.markdown("#### 🔍 Recherche Linéaire vs Binaire")
    n_search = st.slider(
        "Taille du tableau trié", 1000, 50000, 10000, step=1000, key="bench_ns"
    )
    if st.button(
        "🚀 Lancer le benchmark Recherche", width="stretch", type="primary"
    ):
        with st.spinner("Mesure en cours…"):
            results_s = bench_search(n_search)
        st.session_state.search_bench = results_s

    if "search_bench" in st.session_state:
        r = st.session_state.search_bench
        names = list(r.keys())
        values = list(r.values())
        colors = ["#ef4444", "#10b981"]
        fig2 = go.Figure(
            go.Bar(
                x=names,
                y=values,
                marker_color=colors,
                text=[f"{v:.4f} ms" for v in values],
                textposition="outside",
                textfont=dict(color="#e2e8f0", size=11, family="Space Mono"),
            )
        )
        fig2.update_layout(
            paper_bgcolor="#0a0a0f",
            plot_bgcolor="#111118",
            font=dict(color="#e2e8f0", family="DM Sans"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#1e1e2e", title="ms"),
            margin=dict(l=20, r=20, t=20, b=20),
            height=260,
        )
        st.plotly_chart(fig2, width="stretch", key="bench_search")
        if values[0] > 0:
            ratio = values[0] / values[1]
            st.markdown(
                f'<div class="info-box" style="border-left-color:#06b6d4;">🏆 La recherche binaire est <b>{ratio:.0f}×</b> plus rapide sur {n_search:,} éléments</div>',
                unsafe_allow_html=True,
            )

# ── Complexités ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📐 Complexités — vue comparative")
import numpy as np

n_vals = np.array(range(1, 101))
fig3 = go.Figure()
curves = [
    ("O(1)", np.ones_like(n_vals), "#64748b"),
    ("O(log n)", np.log2(n_vals), "#10b981"),
    ("O(n)", n_vals.astype(float), "#06b6d4"),
    ("O(n log n)", n_vals * np.log2(n_vals), "#f59e0b"),
    ("O(n²)", n_vals.astype(float) ** 2 / 10, "#ef4444"),
]
for name, y, color in curves:
    fig3.add_trace(
        go.Scatter(
            x=n_vals,
            y=y,
            name=name,
            mode="lines",
            line=dict(color=color, width=2),
        )
    )
fig3.update_layout(
    paper_bgcolor="#0a0a0f",
    plot_bgcolor="#111118",
    font=dict(color="#e2e8f0", family="DM Sans"),
    xaxis=dict(title="n (taille entrée)", showgrid=True, gridcolor="#1e1e2e"),
    yaxis=dict(
        title="Opérations (relatif)",
        showgrid=True,
        gridcolor="#1e1e2e",
        range=[0, 200],
    ),
    legend=dict(bgcolor="#111118", bordercolor="#1e1e2e"),
    margin=dict(l=40, r=20, t=20, b=40),
    height=320,
)
st.plotly_chart(fig3, width="stretch", key="complexity_chart")
