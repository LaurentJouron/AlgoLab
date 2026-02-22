import streamlit as st
import plotly.graph_objects as go
import math, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="PageRank — Graphix", page_icon="🌐", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithme ────────────────────────────────────────────────────────────────
def pagerank_steps(nodes, edges, damping=0.85, max_iter=30, tol=1e-6):
    n    = len(nodes)
    idx  = {node: i for i, node in enumerate(nodes)}
    out  = {node: [] for node in nodes}
    inc  = {node: [] for node in nodes}
    for src, dst in edges:
        out[src].append(dst)
        inc[dst].append(src)

    rank  = {node: 1/n for node in nodes}
    steps = [{"rank": dict(rank), "iteration": 0, "diff": None,
               "desc": f"Initialisation — chaque page reçoit 1/{n} = {1/n:.4f}"}]

    for it in range(1, max_iter+1):
        new_rank = {}
        for node in nodes:
            contrib = sum(rank[src] / len(out[src]) for src in inc[node] if out[src])
            new_rank[node] = (1 - damping) / n + damping * contrib
        diff = sum(abs(new_rank[nd] - rank[nd]) for nd in nodes)
        rank = new_rank
        converged = diff < tol
        steps.append({"rank": dict(rank), "iteration": it, "diff": diff,
                       "desc": f"Itération {it} — variation Δ={diff:.6f}" +
                               (" &nbsp;✅ <b>Convergé !</b>" if converged else "")})
        if converged:
            break
    return steps

# ── Graphes ───────────────────────────────────────────────────────────────────
GRAPHS = {
    "Web simplifié (6 pages)": {
        "nodes": ["A","B","C","D","E","F"],
        "edges": [("A","B"),("A","C"),("B","C"),("B","D"),
                  ("C","A"),("D","C"),("E","D"),("F","A"),("F","B")]
    },
    "Réseau d'influence": {
        "nodes": ["Hub","Alpha","Beta","Gamma","Delta"],
        "edges": [("Hub","Alpha"),("Hub","Beta"),("Hub","Gamma"),
                  ("Alpha","Hub"),("Beta","Hub"),("Gamma","Delta"),
                  ("Delta","Hub"),("Alpha","Beta")]
    },
    "Chaîne circulaire": {
        "nodes": ["P1","P2","P3","P4","P5"],
        "edges": [("P1","P2"),("P2","P3"),("P3","P4"),("P4","P5"),("P5","P1"),
                  ("P1","P3"),("P3","P5"),("P5","P2")]
    },
}

def compute_pos(nodes):
    pos = {}
    for i, n in enumerate(nodes):
        a = 2 * math.pi * i / len(nodes) - math.pi / 2
        pos[n] = (round(math.cos(a) * 2.5, 4), round(math.sin(a) * 2.5, 4))
    return pos

def make_graph_fig(nodes, edges, pos, rank):
    max_r = max(rank.values()) if rank else 1
    traces = []
    # Arêtes avec flèches via annotations
    for src, dst in edges:
        x0, y0 = pos[src]; x1, y1 = pos[dst]
        # Raccourcir légèrement vers le nœud destination
        dx, dy = x1-x0, y1-y0
        dist   = math.sqrt(dx*dx+dy*dy)
        if dist > 0:
            x1e = x1 - dx/dist * 0.28
            y1e = y1 - dy/dist * 0.28
        else:
            x1e, y1e = x1, y1
        traces.append(go.Scatter(
            x=[x0, x1e, None], y=[y0, y1e, None], mode='lines',
            line=dict(color='#334155', width=1.5),
            hoverinfo='none', showlegend=False))
        # Tête de flèche
        traces.append(go.Scatter(
            x=[x1e], y=[y1e], mode='markers',
            marker=dict(size=7, color='#475569', symbol='triangle-right',
                        angle=math.degrees(math.atan2(dy, dx))),
            hoverinfo='none', showlegend=False))

    # Nœuds — taille proportionnelle au rank
    for node in nodes:
        r    = rank.get(node, 1/len(nodes))
        size = int(20 + r / max_r * 32)
        top3 = sorted(rank.values(), reverse=True)[:3]
        color = "#f59e0b" if r == top3[0] else \
                "#10b981" if r in top3[1:] else "#1e3a5f"
        x, y = pos[node]
        traces.append(go.Scatter(
            x=[x], y=[y], mode='markers+text',
            marker=dict(size=size, color=color,
                        line=dict(color='#0a0a0f', width=2)),
            text=[node], textposition='middle center',
            textfont=dict(size=10, color='white', family='Space Mono'),
            name=f"{node}: {r:.3f}",
            hovertemplate=f"<b>{node}</b><br>PageRank: {r:.4f}<extra></extra>",
        ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-3.5,3.5]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-3.5,3.5]),
        showlegend=False, margin=dict(l=10,r=10,t=10,b=10), height=400,
    )
    return fig

def make_rank_bar(rank, it):
    sorted_nodes = sorted(rank.keys(), key=lambda nd: -rank[nd])
    vals   = [rank[n] for n in sorted_nodes]
    colors = ["#f59e0b" if i==0 else "#10b981" if i==1 else
              "#7c3aed" if i==2 else "#1e3a5f"
              for i in range(len(sorted_nodes))]
    fig = go.Figure(go.Bar(
        x=sorted_nodes, y=vals,
        marker=dict(color=colors, line=dict(color='#0a0a0f', width=1)),
        text=[f"{v:.4f}" for v in vals], textposition='outside',
        textfont=dict(size=10, color='#e2e8f0', family='Space Mono'),
    ))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
        font=dict(color='#e2e8f0', family='DM Sans'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#1e1e2e', title="Score"),
        margin=dict(l=30,r=10,t=30,b=20), height=260, showlegend=False,
        title=dict(text=f"Scores — itération {it}",
                   font=dict(color='#94a3b8',size=12), x=0.5)
    )
    return fig

def make_convergence_fig(steps):
    diffs = [(s["iteration"], s["diff"]) for s in steps[1:] if s["diff"] is not None]
    if not diffs: return None
    xi, yi = zip(*diffs)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(xi), y=list(yi), mode='lines+markers',
                             line=dict(color='#06b6d4', width=2),
                             marker=dict(size=5, color='#06b6d4'), showlegend=False))
    fig.add_hline(y=1e-6, line=dict(color='#10b981', width=1.5, dash='dash'),
                  annotation_text="Seuil convergence (1e-6)",
                  annotation_font=dict(color='#10b981', size=10))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
        font=dict(color='#e2e8f0', family='DM Sans'),
        xaxis=dict(showgrid=True, gridcolor='#1e1e2e', title="Itération", dtick=1),
        yaxis=dict(showgrid=True, gridcolor='#1e1e2e', title="Variation Δ", type='log'),
        margin=dict(l=50,r=10,t=10,b=40), height=210, showlegend=False,
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.3);color:#67e8f9;">🌐 PAGERANK</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">PageRank</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">L\'algorithme original de Google (1998). Les pages se transmettent leur importance via les liens : une page très liée reçoit un score élevé. Le score converge en quelques itérations. La <b>taille des nœuds</b> est proportionnelle au PageRank.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    graph_name = st.selectbox("Graphe", list(GRAPHS.keys()))
    damping    = st.slider("Facteur d'amortissement (d)", 0.5, 0.99, 0.85, step=0.01,
                           help="d=0.85 : 85% de chances de suivre un lien, 15% de sauter aléatoirement")

    g      = GRAPHS[graph_name]
    nodes  = g["nodes"]; edges = g["edges"]
    pos    = compute_pos(nodes)
    steps  = pagerank_steps(nodes, edges, damping=damping)
    n_iter = len(steps) - 1

    st.markdown(f'<span class="complexity-badge">O(k·(V+E)) · {n_iter} itérations</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🏆 Top 3 final")
    final_rank = steps[-1]["rank"]
    top3 = sorted(final_rank.items(), key=lambda x: -x[1])[:3]
    for med, (node, score) in zip(["🥇","🥈","🥉"], top3):
        st.markdown(f'<div class="info-box" style="border-left-color:#f59e0b;padding:0.4rem 0.8rem;margin-bottom:4px;">{med} <b>{node}</b> — {score:.4f}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🧠 Formule")
    st.markdown(f"""
    <div class="info-box" style="border-left-color:#06b6d4; font-size:0.82rem;">
    PR(A) = <b>(1-d)/N</b> + <b>d</b> × Σ PR(i)/L(i)<br><br>
    • <b>d</b> = {damping} (amortissement)<br>
    • <b>N</b> = {len(nodes)} pages<br>
    • <b>L(i)</b> = nb de liens sortants de i<br><br>
    <b>Intuition :</b> un surfeur suit un lien avec probabilité d, ou saute vers une page aléatoire avec 1-d.<br><br>
    Le PageRank = probabilité d'être sur cette page à l'infini.
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("🟡 **Jaune** = page #1")
    st.markdown("🟢 **Vert** = pages #2 et #3")
    st.markdown("🔵 **Bleu** = autres pages")
    st.markdown("📐 **Taille** ∝ PageRank")
    st.markdown("*Glisse le slider pour voir les itérations*")

with col_viz:
    step_idx = st.slider("Itération", 0, len(steps)-1, 0, key="pr_step")
    s = steps[step_idx]
    st.markdown(f'<div class="info-box" style="border-left-color:#06b6d4;">{s["desc"]}</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown("##### 🌐 Graphe (taille ∝ PageRank)")
        st.plotly_chart(make_graph_fig(nodes, edges, pos, s["rank"]),
                        use_container_width=True, key=f"pr_graph_{step_idx}_{graph_name}")
    with col_b:
        st.markdown("##### 📊 Scores triés")
        st.plotly_chart(make_rank_bar(s["rank"], s["iteration"]),
                        use_container_width=True, key=f"pr_bar_{step_idx}_{graph_name}")

    conv_fig = make_convergence_fig(steps)
    if conv_fig and step_idx > 1:
        st.markdown("##### 📉 Convergence (axe Y logarithmique)")
        st.plotly_chart(conv_fig, use_container_width=True, key=f"pr_conv_{step_idx}_{graph_name}")
