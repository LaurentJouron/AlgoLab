import streamlit as st
import plotly.graph_objects as go
import math, heapq, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Kruskal / Prim — Graphix", page_icon="🌉", layout="wide")
inject_css()
sidebar_nav()

# ── Union-Find ────────────────────────────────────────────────────────────────
class UF:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return False
        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1
        return True

# ── Algorithmes ───────────────────────────────────────────────────────────────
def kruskal_steps(nodes, edges):
    sorted_edges = sorted(edges, key=lambda e: e[2])
    uf       = UF(len(nodes))
    node_idx = {n: i for i, n in enumerate(nodes)}
    mst, rejected, steps = [], [], []
    steps.append({"mst": [], "current": None, "rejected": [],
                  "desc": f"Arêtes triées par poids croissant — on teste dans l'ordre"})
    for u, v, w in sorted_edges:
        if uf.union(node_idx[u], node_idx[v]):
            mst.append((u, v, w))
            steps.append({"mst": list(mst), "current": (u,v,w), "rejected": list(rejected),
                          "desc": f"✅ <b>{u}–{v}</b> (poids {w}) ajoutée — pas de cycle"})
        else:
            rejected.append((u,v,w))
            steps.append({"mst": list(mst), "current": (u,v,w), "rejected": list(rejected),
                          "desc": f"❌ <b>{u}–{v}</b> (poids {w}) rejetée — créerait un cycle"})
    total = sum(e[2] for e in mst)
    steps.append({"mst": list(mst), "current": None, "rejected": list(rejected),
                  "desc": f"✅ Terminé — {len(mst)} arêtes, poids total = <b>{total}</b>"})
    return steps

def prim_steps(nodes, edges):
    graph = {n: [] for n in nodes}
    for u, v, w in edges:
        graph[u].append((v, w)); graph[v].append((u, w))
    start   = nodes[0]
    visited = {start}
    heap    = [(w, start, v) for v, w in graph[start]]
    heapq.heapify(heap)
    mst, rejected, steps = [], [], []
    steps.append({"mst": [], "current": None, "visited": {start}, "rejected": [],
                  "desc": f"Départ depuis <b>{start}</b> — on explore ses voisins"})
    while heap:
        w, u, v = heapq.heappop(heap)
        if v in visited:
            rejected.append((u, v, w))
            steps.append({"mst": list(mst), "current": (u,v,w), "visited": set(visited),
                          "rejected": list(rejected),
                          "desc": f"❌ <b>{u}–{v}</b> (poids {w}) ignorée — <b>{v}</b> déjà dans l'arbre"})
            continue
        visited.add(v)
        mst.append((u, v, w))
        steps.append({"mst": list(mst), "current": (u,v,w), "visited": set(visited),
                      "rejected": list(rejected),
                      "desc": f"✅ <b>{u}–{v}</b> (poids {w}) ajoutée — <b>{v}</b> rejoint l'arbre"})
        for neighbor, nw in graph[v]:
            if neighbor not in visited:
                heapq.heappush(heap, (nw, v, neighbor))
    total = sum(e[2] for e in mst)
    steps.append({"mst": list(mst), "current": None, "visited": set(visited),
                  "rejected": list(rejected),
                  "desc": f"✅ Terminé — poids total ACM = <b>{total}</b>"})
    return steps

# ── Graphes ───────────────────────────────────────────────────────────────────
GRAPHS = {
    "Réseau de villes": {
        "nodes": ["Paris","Lyon","Marseille","Bordeaux","Toulouse","Nantes"],
        "edges": [("Paris","Lyon",465),("Paris","Bordeaux",579),("Paris","Nantes",385),
                  ("Lyon","Marseille",315),("Lyon","Toulouse",535),
                  ("Bordeaux","Toulouse",245),("Bordeaux","Nantes",345),
                  ("Marseille","Toulouse",405),("Toulouse","Nantes",580),("Paris","Marseille",777)]
    },
    "Graphe simple A–F": {
        "nodes": ["A","B","C","D","E","F"],
        "edges": [("A","B",4),("A","C",2),("B","C",1),("B","D",5),
                  ("C","D",8),("C","E",10),("D","E",2),("D","F",6),("E","F",3)]
    },
}

def compute_pos(nodes):
    pos = {}
    for i, n in enumerate(nodes):
        a = 2 * math.pi * i / len(nodes) - math.pi / 2
        pos[n] = (round(math.cos(a) * 2.2, 4), round(math.sin(a) * 2.2, 4))
    return pos

def make_graph_fig(nodes, edges, pos, mst_set, current, rejected_set, visited=None):
    traces = []
    for u, v, w in edges:
        k1, k2 = (u,v,w), (v,u,w)
        is_mst     = k1 in mst_set or k2 in mst_set
        is_current = current and (current[:2] in [(u,v),(v,u)])
        is_rejected= k1 in rejected_set or k2 in rejected_set
        color = "#10b981" if is_mst else "#f59e0b" if is_current else "#ef4444" if is_rejected else "#253545"
        width = 3.5 if (is_mst or is_current) else 1
        x0, y0 = pos[u]; x1, y1 = pos[v]
        traces.append(go.Scatter(x=[x0,x1,None], y=[y0,y1,None], mode='lines',
                                 line=dict(color=color, width=width),
                                 hoverinfo='none', showlegend=False))
        # Label poids
        traces.append(go.Scatter(x=[(x0+x1)/2], y=[(y0+y1)/2], mode='text',
                                 text=[str(w)],
                                 textfont=dict(size=10, color='#94a3b8', family='Space Mono'),
                                 hoverinfo='none', showlegend=False))
    # Nœuds
    nc = ["#10b981" if (visited and n in visited) else "#1e3a5f" for n in nodes]
    traces.append(go.Scatter(
        x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes],
        mode='markers+text',
        marker=dict(size=32, color=nc, line=dict(color='#0a0a0f', width=2)),
        text=nodes, textposition='middle center',
        textfont=dict(size=11, color='white', family='Space Mono'),
        hoverinfo='none', showlegend=False))
    return traces

def make_animated_fig(nodes, edges, pos, steps, prefix):
    def frame_data(s):
        return make_graph_fig(nodes, edges, pos,
                              set(tuple(e) for e in s["mst"]),
                              s["current"],
                              set(tuple(e) for e in s["rejected"]),
                              s.get("visited"))
    s0 = steps[0]
    fig = go.Figure(
        data=frame_data(s0),
        layout=go.Layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-3,3]),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-3,3]),
            margin=dict(l=20, r=20, t=60, b=90), height=460,
            annotations=[dict(x=0.5, y=1.08, xref='paper', yref='paper', text=s0["desc"],
                              showarrow=False, font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')],
            updatemenus=[dict(type="buttons", showactive=False, y=-0.20, x=0.5, xanchor="center",
                buttons=[
                    dict(label="▶  Démarrer", method="animate",
                         args=[None, dict(frame=dict(duration=900, redraw=True),
                                         transition=dict(duration=250, easing="cubic-in-out"),
                                         fromcurrent=True, mode="immediate")]),
                    dict(label="⏸  Pause", method="animate",
                         args=[[None], dict(frame=dict(duration=0, redraw=False),
                                            mode="immediate", transition=dict(duration=0))]),
                ],
                font=dict(color="#e2e8f0", family="Space Mono", size=12),
                bgcolor="#1e1e2e", bordercolor="#334155")],
            sliders=[dict(active=0,
                currentvalue=dict(prefix="Étape : ", font=dict(color="#94a3b8", family="Space Mono", size=11),
                                  visible=True, xanchor="center"),
                pad=dict(t=50, b=5), len=0.9, x=0.05,
                bgcolor="#111118", bordercolor="#1e1e2e", tickcolor="#334155",
                font=dict(color="#64748b", size=9),
                steps=[dict(method="animate",
                            args=[[f"{prefix}{k}"], dict(mode="immediate",
                                   frame=dict(duration=900, redraw=True),
                                   transition=dict(duration=250))],
                            label=str(k)) for k in range(len(steps))])],
        ),
        frames=[go.Frame(name=f"{prefix}{k}", data=frame_data(s),
                         layout=go.Layout(annotations=[dict(x=0.5, y=1.08, xref='paper', yref='paper',
                                                            text=s["desc"], showarrow=False,
                                                            font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')]))
                for k, s in enumerate(steps)],
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;">🌉 ARBRE COUVRANT MINIMAL</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Kruskal & Prim</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Trouver l\'arbre qui connecte tous les nœuds au coût total minimal — l\'<b>Arbre Couvrant Minimal (ACM)</b>. Deux stratégies : Kruskal ajoute les arêtes les moins chères sans créer de cycle, Prim étend un arbre nœud par nœud.</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔗  Kruskal — Arêtes globales", "🌱  Prim — Croissance locale"])

# ── Kruskal ───────────────────────────────────────────────────────────────────
with tab1:
    col_ctrl, col_viz = st.columns([1, 3])
    with col_ctrl:
        st.markdown("#### ⚙️ Paramètres")
        graph_k = st.selectbox("Graphe", list(GRAPHS.keys()), key="g_kruskal")
        gk = GRAPHS[graph_k]
        nodes_k, edges_k = gk["nodes"], gk["edges"]
        steps_k = kruskal_steps(nodes_k, edges_k)
        total_k = steps_k[-1]["mst"]
        total_k = sum(e[2] for e in total_k)
        st.markdown(f'<span class="complexity-badge">O(E log E) · {len(steps_k)-2} arêtes testées</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">Poids ACM : {total_k}</span>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""
        <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
        <b>Idée :</b> trier toutes les arêtes, prendre les moins chères<br><br>
        1. Trier les arêtes par poids croissant<br>
        2. Pour chaque arête, vérifier via <b>Union-Find</b> si elle crée un cycle<br>
        3. Si non → l'ajouter à l'ACM<br>
        4. S'arrêter quand on a <b>V−1</b> arêtes<br><br>
        <b>Union-Find</b> : structure qui détecte en O(α) si deux nœuds sont déjà connectés.
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("🟢 **Vert** — Dans l'ACM")
        st.markdown("🟡 **Jaune** — Arête testée")
        st.markdown("🔴 **Rouge** — Rejetée (cycle)")
        st.markdown("*Appuie sur **▶ Démarrer** ou glisse le slider*")
    with col_viz:
        pos_k = compute_pos(nodes_k)
        fig_k = make_animated_fig(nodes_k, edges_k, pos_k, steps_k, "kr")
        st.plotly_chart(fig_k, use_container_width=True, key=f"kruskal_{graph_k}")

# ── Prim ─────────────────────────────────────────────────────────────────────
with tab2:
    col_ctrl2, col_viz2 = st.columns([1, 3])
    with col_ctrl2:
        st.markdown("#### ⚙️ Paramètres")
        graph_p = st.selectbox("Graphe", list(GRAPHS.keys()), key="g_prim")
        gp = GRAPHS[graph_p]
        nodes_p, edges_p = gp["nodes"], gp["edges"]
        steps_p = prim_steps(nodes_p, edges_p)
        total_p = sum(e[2] for e in steps_p[-1]["mst"])
        st.markdown(f'<span class="complexity-badge">O(E log V) · {len(steps_p)-2} étapes</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">Poids ACM : {total_p}</span>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""
        <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
        <b>Idée :</b> faire grandir un arbre depuis un nœud de départ<br><br>
        1. Démarrer depuis le premier nœud<br>
        2. Mettre tous ses voisins dans un <b>min-heap</b><br>
        3. Extraire le voisin le moins cher non encore visité<br>
        4. L'ajouter à l'arbre, ajouter ses voisins au heap<br>
        5. Répéter jusqu'à couvrir tous les nœuds<br><br>
        Kruskal et Prim donnent <b>toujours le même ACM</b> (ou un ACM de même poids).
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("🟢 **Vert** — Dans l'ACM / visité")
        st.markdown("🟡 **Jaune** — Arête testée")
        st.markdown("🔴 **Rouge** — Ignorée (déjà visité)")
        st.markdown("*Appuie sur **▶ Démarrer** ou glisse le slider*")
    with col_viz2:
        pos_p = compute_pos(nodes_p)
        fig_p = make_animated_fig(nodes_p, edges_p, pos_p, steps_p, "pr")
        st.plotly_chart(fig_p, use_container_width=True, key=f"prim_{graph_p}")
