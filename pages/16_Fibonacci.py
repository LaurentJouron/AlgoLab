import streamlit as st
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Fibonacci — Graphix", page_icon="🌀", layout="wide"
)
inject_css()
sidebar_nav()

# ── Algorithmes ───────────────────────────────────────────────────────────────


def fib_recursive_trace(n):
    """Retourne liste de nœuds et arêtes de l'arbre d'appels."""
    nodes, edges, counter = [], [], [0]

    def rec(k, parent_id):
        my_id = counter[0]
        counter[0] += 1
        nodes.append({"id": my_id, "k": k, "base": k <= 1})
        if parent_id is not None:
            edges.append((parent_id, my_id))
        if k <= 1:
            return k
        l = rec(k - 1, my_id)
        r = rec(k - 2, my_id)
        return l + r

    result = rec(n, None)
    return result, nodes, edges


def fib_memo_steps(n):
    memo, steps = {}, []

    def fib(k, depth=0):
        if k in memo:
            steps.append(
                {
                    "k": k,
                    "depth": depth,
                    "hit": True,
                    "memo": dict(memo),
                    "desc": f"🟡 Cache hit : F({k}) = <b>{memo[k]}</b> — déjà calculé, on retourne directement",
                }
            )
            return memo[k]
        steps.append(
            {
                "k": k,
                "depth": depth,
                "hit": False,
                "memo": dict(memo),
                "desc": f"🔵 Calcul de F({k}) — pas encore en cache, on descend",
            }
        )
        memo[k] = (
            k if k <= 1 else fib(k - 1, depth + 1) + fib(k - 2, depth + 1)
        )
        steps.append(
            {
                "k": k,
                "depth": depth,
                "hit": False,
                "memo": dict(memo),
                "desc": f"💾 F({k}) = <b>{memo[k]}</b> mémoïsé — plus besoin de recalculer",
            }
        )
        return memo[k]

    result = fib(n)
    return result, steps


def fib_iterative_steps(n):
    steps = []
    if n == 0:
        return 0, [
            {
                "i": 0,
                "a": 0,
                "b": 1,
                "sequence": [0],
                "desc": "F(0) = 0 — cas de base",
            }
        ]
    a, b, sequence = 0, 1, [0, 1]
    steps.append(
        {
            "i": 1,
            "a": 0,
            "b": 1,
            "sequence": [0, 1],
            "desc": "Initialisation : a=F(0)=0, b=F(1)=1",
        }
    )
    for i in range(2, n + 1):
        a, b = b, a + b
        sequence.append(b)
        steps.append(
            {
                "i": i,
                "a": a,
                "b": b,
                "sequence": list(sequence),
                "desc": f"F({i}) = F({i-1}) + F({i-2}) = {a} + {sequence[-3]} = <b>{b}</b>",
            }
        )
    return b, steps


# ── Visualisations ────────────────────────────────────────────────────────────


def make_call_tree_fig(nodes, edges, highlight_base=True):
    """Arbre d'appels correct avec positions calculées par BFS."""
    if not nodes:
        return go.Figure()
    # Positions : BFS niveau par niveau
    from collections import defaultdict, deque

    children = defaultdict(list)
    for p, c in edges:
        children[p].append(c)
    level = {0: 0}
    q = deque([0])
    level_nodes = defaultdict(list)
    level_nodes[0].append(0)
    while q:
        cur = q.popleft()
        for ch in children[cur]:
            level[ch] = level[cur] + 1
            level_nodes[level[ch]].append(ch)
            q.append(ch)
    pos = {}
    for lv, nids in level_nodes.items():
        for idx, nid in enumerate(nids):
            pos[nid] = (idx - (len(nids) - 1) / 2, -lv * 1.6)

    traces = []
    for p, c in edges:
        if p in pos and c in pos:
            x0, y0 = pos[p]
            x1, y1 = pos[c]
            traces.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode="lines",
                    line=dict(color="#334155", width=1.2),
                    hoverinfo="none",
                    showlegend=False,
                )
            )
    nx = [pos[nd["id"]][0] for nd in nodes if nd["id"] in pos]
    ny = [pos[nd["id"]][1] for nd in nodes if nd["id"] in pos]
    nc = [
        "#f59e0b" if nd["base"] else "#7c3aed"
        for nd in nodes
        if nd["id"] in pos
    ]
    nt = [f"F({nd['k']})" for nd in nodes if nd["id"] in pos]
    ns = [22 if nd["base"] else 18 for nd in nodes if nd["id"] in pos]

    traces.append(
        go.Scatter(
            x=nx,
            y=ny,
            mode="markers+text",
            marker=dict(
                size=ns, color=nc, line=dict(color="#0a0a0f", width=1)
            ),
            text=nt,
            textposition="middle center",
            textfont=dict(size=8, color="white", family="Space Mono"),
            hoverinfo="none",
            showlegend=False,
        )
    )
    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        showlegend=False,
    )
    return fig


def make_memo_chart(memo, current_k):
    if not memo:
        return go.Figure().update_layout(paper_bgcolor="#0a0a0f", height=200)
    keys = sorted(memo.keys())
    colors = ["#f59e0b" if k == current_k else "#7c3aed" for k in keys]
    values = [memo[k] for k in keys]
    fig = go.Figure(
        go.Bar(
            x=[f"F({k})" for k in keys],
            y=values,
            marker=dict(color=colors, line=dict(color="#0a0a0f", width=1)),
            text=values,
            textposition="outside",
            textfont=dict(size=10, color="#e2e8f0", family="Space Mono"),
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        font=dict(color="#e2e8f0", family="DM Sans"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e1e2e", title="Valeur"),
        margin=dict(l=30, r=10, t=10, b=30),
        height=240,
        showlegend=False,
    )
    return fig


def make_iter_chart(sequence, current_i):
    colors = [
        (
            "#f59e0b"
            if i == current_i
            else "#06b6d4" if i == current_i - 1 else "#7c3aed"
        )
        for i in range(len(sequence))
    ]
    fig = go.Figure(
        go.Bar(
            x=[f"F({i})" for i in range(len(sequence))],
            y=sequence,
            marker=dict(color=colors, line=dict(color="#0a0a0f", width=1)),
            text=sequence,
            textposition="outside",
            textfont=dict(size=10, color="#e2e8f0", family="Space Mono"),
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        font=dict(color="#e2e8f0", family="DM Sans"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e1e2e", title="Valeur"),
        margin=dict(l=30, r=10, t=10, b=30),
        height=260,
        showlegend=False,
    )
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.3);color:#67e8f9;">🌀 FIBONACCI</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-title">Suite de Fibonacci</div>', unsafe_allow_html=True
)
st.markdown(
    "<div class=\"page-desc\">Trois façons de calculer F(n). La comparaison est frappante : le récursif refait les mêmes calculs des milliers de fois, la mémoïsation les évite avec un cache, et l'itératif n'utilise que deux variables.</div>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(
    [
        "🌳  Récursif — O(2ⁿ)",
        "💾  Mémoïsation — O(n)",
        "➡️  Itératif — O(n) / O(1)",
    ]
)

# ── Tab 1 : Récursif ──────────────────────────────────────────────────────────
with tab1:
    col_ctrl, col_viz = st.columns([1, 3])
    with col_ctrl:
        st.markdown("#### ⚙️ Paramètres")
        n_rec = st.slider("Calculer F(n)", 1, 10, 5, key="fib_rec_n")
        result_rec, nodes_rec, edges_rec = fib_recursive_trace(n_rec)
        n_calls = len(nodes_rec)
        n_base = sum(1 for nd in nodes_rec if nd["base"])
        st.metric(f"F({n_rec})", result_rec)
        st.markdown(
            f'<span class="complexity-badge">O(2ⁿ) — {n_calls} appels</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{n_base} appels de base (F(0) ou F(1))</span>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            f"""
        <div class="info-box" style="border-left-color:#ef4444; font-size:0.82rem;">
        <b>Problème :</b> F(k) est recalculé à chaque branche.<br><br>
        Pour F(5), F(3) est calculé <b>2 fois</b>,
        F(2) est calculé <b>3 fois</b>, F(1) <b>5 fois</b>.<br><br>
        Pour F(10) → {n_calls} appels.<br>
        Pour F(40) → ~2 milliards d'appels !<br><br>
        L'arbre s'<b>exponentielle</b> rapidement.
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("🟣 **Violet** = appel récursif")
        st.markdown("🟡 **Jaune** = cas de base F(0) ou F(1)")
    with col_viz:
        st.markdown(f"##### 🌳 Arbre des appels récursifs pour F({n_rec})")
        st.markdown(
            f"*{n_calls} appels au total — chaque nœud violet appelle deux sous-arbres*"
        )
        fig_tree = make_call_tree_fig(nodes_rec, edges_rec)
        st.plotly_chart(
            fig_tree, use_container_width=True, key=f"fib_tree_{n_rec}"
        )
        st.markdown(
            f"""
        <div class="info-box" style="border-left-color:#ef4444;">
        F({n_rec}) = <b>{result_rec}</b> — calculé en <b>{n_calls}</b> appels.
        Le même sous-problème est résolu plusieurs fois en descendant dans chaque branche.
        </div>""",
            unsafe_allow_html=True,
        )

# ── Tab 2 : Mémoïsation ───────────────────────────────────────────────────────
with tab2:
    col_ctrl2, col_viz2 = st.columns([1, 3])
    with col_ctrl2:
        st.markdown("#### ⚙️ Paramètres")
        n_memo = st.slider("Calculer F(n)", 1, 25, 8, key="fib_memo_n")
        result_memo, memo_steps = fib_memo_steps(n_memo)
        hits = sum(1 for s in memo_steps if s.get("hit"))
        st.metric(f"F({n_memo})", result_memo)
        st.markdown(
            f'<span class="complexity-badge">O(n) — {len(memo_steps)} étapes</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{hits} cache hits évités</span>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            """
        <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
        <b>Solution :</b> mémoriser chaque résultat dans un dictionnaire.<br><br>
        Avant de calculer F(k), on vérifie si on l'a déjà.<br>
        Si oui → retour immédiat.<br>
        Si non → calcul puis stockage.<br><br>
        Chaque valeur est calculée <b>exactement une fois</b>.
        Complexité : <b>O(n)</b> au lieu de O(2ⁿ).
        </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("🔵 **Violet** = nouveau calcul")
        st.markdown("🟡 **Jaune** = valeur en cours")
        st.markdown("💾 Cache = dictionnaire mémo")
    with col_viz2:
        step_m = st.slider(
            "Étape", 0, len(memo_steps) - 1, 0, key="fib_memo_step"
        )
        s = memo_steps[step_m]
        st.markdown(
            f'<div class="info-box" style="border-left-color:#10b981;">{s["desc"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("##### 💾 État du cache à cette étape")
        st.plotly_chart(
            make_memo_chart(s["memo"], s["k"]),
            use_container_width=True,
            key=f"fib_memo_{step_m}",
        )
        if s["memo"]:
            st.markdown(
                f"*{len(s['memo'])} valeur(s) en cache sur {n_memo+1} nécessaires*"
            )

# ── Tab 3 : Itératif ──────────────────────────────────────────────────────────
with tab3:
    col_ctrl3, col_viz3 = st.columns([1, 3])
    with col_ctrl3:
        st.markdown("#### ⚙️ Paramètres")
        n_iter = st.slider("Calculer F(n)", 1, 30, 10, key="fib_iter_n")
        result_iter, iter_steps = fib_iterative_steps(n_iter)
        st.metric(f"F({n_iter})", result_iter)
        st.markdown(
            f'<span class="complexity-badge">O(n) temps · O(1) espace</span>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            """
        <div class="info-box" style="border-left-color:#06b6d4; font-size:0.82rem;">
        <b>Optimal :</b> on ne garde que <b>deux variables</b>.<br><br>
        a, b = 0, 1<br>
        À chaque étape : a, b = b, a+b<br><br>
        Aucun tableau, aucun cache.<br>
        Espace constant : <b>O(1)</b>.<br><br>
        C'est la version à préférer en pratique.
        </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("🟡 **Jaune** = valeur calculée")
        st.markdown("🔵 **Cyan** = valeur précédente (a)")
        st.markdown("🟣 **Violet** = valeurs antérieures")
    with col_viz3:
        step_i = st.slider(
            "Étape", 0, len(iter_steps) - 1, 0, key="fib_iter_step"
        )
        s = iter_steps[step_i]
        st.markdown(
            f'<div class="info-box" style="border-left-color:#06b6d4;">{s["desc"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("##### 📊 Séquence construite")
        st.plotly_chart(
            make_iter_chart(s["sequence"], s["i"]),
            use_container_width=True,
            key=f"fib_iter_{step_i}",
        )
        # Tableau comparatif
        st.markdown("---")
        st.markdown("##### ⚖️ Comparaison des 3 approches")
        for m, tc, sc, col in [
            ("Récursif", "O(2ⁿ)", "O(n) pile", "#ef4444"),
            ("Mémoïsation", "O(n)", "O(n) cache", "#f59e0b"),
            ("Itératif", "O(n)", "O(1)", "#10b981"),
        ]:
            st.markdown(
                f"""
            <div style="display:flex;gap:1rem;align-items:center;background:#111118;
                        border-left:3px solid {col};border-radius:6px;
                        padding:0.5rem 0.8rem;margin-bottom:6px;font-family:'Space Mono',monospace;font-size:0.8rem;">
                <div style="color:{col};font-weight:700;min-width:110px;">{m}</div>
                <div style="color:#94a3b8;">Temps : <b style="color:#e2e8f0;">{tc}</b></div>
                <div style="color:#94a3b8;">Espace : <b style="color:#e2e8f0;">{sc}</b></div>
            </div>""",
                unsafe_allow_html=True,
            )
