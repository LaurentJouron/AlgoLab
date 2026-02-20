import streamlit as st
import plotly.graph_objects as go
import heapq, collections, math, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Graphes — AlgoLab", page_icon="🕸️", layout="wide")
inject_css()
sidebar_nav()

# ── Graphes prédéfinis ────────────────────────────────────────────────────────

GRAPHS = {
    "Réseau de villes": {
        "nodes": ["Paris","Lyon","Marseille","Bordeaux","Toulouse","Nantes","Lille","Strasbourg"],
        "edges": [
            ("Paris","Lyon",465), ("Paris","Bordeaux",579), ("Paris","Nantes",385),
            ("Paris","Lille",225), ("Paris","Strasbourg",490),
            ("Lyon","Marseille",315), ("Lyon","Toulouse",535), ("Lyon","Strasbourg",490),
            ("Bordeaux","Toulouse",245), ("Bordeaux","Nantes",345),
            ("Marseille","Toulouse",405), ("Toulouse","Nantes",580),
            ("Lille","Strasbourg",530),
        ]
    },
    "Graphe simple": {
        "nodes": ["A","B","C","D","E","F","G"],
        "edges": [
            ("A","B",4), ("A","C",2), ("B","C",5), ("B","D",10),
            ("C","E",3), ("D","F",11), ("E","D",4), ("E","F",8), ("E","G",6),
            ("F","G",2)
        ]
    }
}

def compute_layout(nodes):
    pos = {}
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / len(nodes)
        pos[node] = (math.cos(angle) * 2, math.sin(angle) * 2)
    return pos

# ── Algorithmes ───────────────────────────────────────────────────────────────

def dijkstra_steps(nodes, edges, start):
    graph = collections.defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w)); graph[v].append((u, w))
    dist = {n: float('inf') for n in nodes}
    dist[start] = 0
    prev = {n: None for n in nodes}
    pq, visited, steps = [(0, start)], set(), []
    while pq:
        d, u = heapq.heappop(pq)
        if u in visited: continue
        visited.add(u)
        steps.append({"visited": set(visited), "current": u, "dist": dict(dist), "prev": dict(prev),
                      "desc": f"Visite <b>{u}</b> (distance={d})"})
        for v, w in graph[u]:
            if v not in visited and dist[u]+w < dist[v]:
                dist[v] = dist[u]+w; prev[v] = u
                heapq.heappush(pq, (dist[v], v))
                steps.append({"visited": set(visited), "current": v, "dist": dict(dist), "prev": dict(prev),
                               "desc": f"Mise à jour : dist[<b>{v}</b>] = {dist[v]} (via {u})"})
    return steps, dist, prev

def bfs_steps(nodes, edges, start):
    graph = collections.defaultdict(list)
    for u, v, _ in edges:
        graph[u].append(v); graph[v].append(u)
    visited, queue, steps = set([start]), collections.deque([start]), []
    while queue:
        u = queue.popleft()
        steps.append({"visited": set(visited), "current": u,
                      "desc": f"Défilement : <b>{u}</b> | File : {list(queue) or ['vide']}"})
        for v in sorted(graph[u]):
            if v not in visited:
                visited.add(v); queue.append(v)
    return steps

def dfs_steps(nodes, edges, start):
    graph = collections.defaultdict(list)
    for u, v, _ in edges:
        graph[u].append(v); graph[v].append(u)
    visited, steps, order = set(), [], []
    def dfs(u):
        visited.add(u); order.append(u)
        steps.append({"visited": set(visited), "current": u,
                      "desc": f"Exploration récursive de <b>{u}</b> (ordre : {list(order)})"})
        for v in sorted(graph[u]):
            if v not in visited: dfs(v)
    dfs(start)
    return steps

def get_path_edges(prev, end):
    path_edges, node = set(), end
    while prev.get(node):
        path_edges.add((prev[node], node)); node = prev[node]
    return path_edges

# ── Construction figure animée ────────────────────────────────────────────────

def build_frame_traces(nodes, edges, pos, visited, current, path_edges, dist):
    traces = []
    for u, v, w in edges:
        x0, y0 = pos[u]; x1, y1 = pos[v]
        is_path = (u,v) in path_edges or (v,u) in path_edges
        traces.append(go.Scatter(
            x=[x0,x1,None], y=[y0,y1,None], mode='lines',
            line=dict(color="#06b6d4" if is_path else "#1e2e3e",
                      width=3 if is_path else 1),
            hoverinfo='none', showlegend=False))
        mx, my = (x0+x1)/2, (y0+y1)/2
        traces.append(go.Scatter(
            x=[mx], y=[my], mode='text', text=[str(w)],
            textfont=dict(size=9, color='#475569', family='Space Mono'),
            hoverinfo='none', showlegend=False))

    node_colors = ["#f59e0b" if n==current else "#10b981" if n in visited else "#334155" for n in nodes]
    node_sizes  = [30 if n==current else 24 if n in visited else 22 for n in nodes]
    traces.append(go.Scatter(
        x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes],
        mode='markers+text',
        marker=dict(size=node_sizes, color=node_colors, line=dict(color='#0a0a0f', width=2)),
        text=nodes,
        textposition='top center',
        textfont=dict(size=11, color='#e2e8f0', family='Space Mono'),
        hovertext=[f"{n}: {int(dist[n])} km" if dist and dist.get(n, float('inf')) != float('inf') else n for n in nodes],
        hoverinfo='text', showlegend=False))
    return traces

def make_animated_fig(nodes, edges, pos, steps, algo, end_node, dist_final, prev_final):
    n_steps = len(steps)

    def get_path(k):
        if algo == "Dijkstra" and k == n_steps-1 and end_node:
            return get_path_edges(steps[k]["prev"], end_node)
        return set()

    s0 = steps[0]
    traces0 = build_frame_traces(nodes, edges, pos,
                                 s0["visited"], s0["current"], get_path(0),
                                 s0.get("dist"))

    fig = go.Figure(
        data=traces0,
        layout=go.Layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            margin=dict(l=20, r=20, t=55, b=75),
            height=460,
            annotations=[dict(
                x=0.5, y=1.07, xref='paper', yref='paper',
                text=s0["desc"], showarrow=False,
                font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')],
            updatemenus=[dict(
                type="buttons", showactive=False,
                y=-0.16, x=0.5, xanchor="center",
                buttons=[
                    dict(label="▶  Démarrer", method="animate",
                         args=[None, dict(frame=dict(duration=600, redraw=True),
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
                currentvalue=dict(prefix="Étape : ",
                                  font=dict(color="#94a3b8", family="Space Mono", size=11),
                                  visible=True, xanchor="center"),
                pad=dict(t=45, b=5), len=0.9, x=0.05,
                bgcolor="#111118", bordercolor="#1e1e2e", tickcolor="#334155",
                font=dict(color="#64748b", size=9),
                steps=[dict(method="animate",
                            args=[[f"g{k}"], dict(mode="immediate",
                                                  frame=dict(duration=600, redraw=True),
                                                  transition=dict(duration=200))],
                            label=str(k)) for k in range(n_steps)],
            )],
        ),
        frames=[
            go.Frame(
                name=f"g{k}",
                data=build_frame_traces(nodes, edges, pos,
                                        s["visited"], s["current"], get_path(k),
                                        s.get("dist")),
                layout=go.Layout(annotations=[dict(
                    x=0.5, y=1.07, xref='paper', yref='paper',
                    text=s["desc"], showarrow=False,
                    font=dict(color='#94a3b8', size=12, family='DM Sans'), align='center')])
            )
            for k, s in enumerate(steps)
        ],
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;">🕸️ ALGORITHMES DE GRAPHES</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Graphes & Parcours</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Visualisez Dijkstra, BFS et DFS. Utilisez <b>▶ Démarrer</b> ou le slider pour avancer. Nœuds verts = visités, jaune = en cours, bleu = chemin optimal.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    graph_name = st.selectbox("Graphe",       list(GRAPHS.keys()))
    algo       = st.selectbox("Algorithme",   ["Dijkstra", "BFS", "DFS"])
    g          = GRAPHS[graph_name]
    start_node = st.selectbox("Nœud de départ", g["nodes"])

    complexity_map = {"Dijkstra":"O((V+E) log V)", "BFS":"O(V+E)", "DFS":"O(V+E)"}
    st.markdown(f'<span class="complexity-badge">{complexity_map[algo]}</span>', unsafe_allow_html=True)
    st.markdown("---")

    end_node = None
    if algo == "Dijkstra":
        end_node = st.selectbox("Nœud d'arrivée", [n for n in g["nodes"] if n != start_node])

    desc_map = {
        "Dijkstra": "<b>Dijkstra :</b> Explore toujours le nœud le plus proche non encore visité. Garantit le chemin le plus court sur un graphe à poids positifs.",
        "BFS":      "<b>BFS :</b> Parcours niveau par niveau via une file (FIFO). Garantit le chemin le plus court en nombre d'arêtes.",
        "DFS":      "<b>DFS :</b> Explore aussi loin que possible avant de revenir en arrière. Utilise une pile ou la récursion.",
    }
    st.markdown(f'<div class="info-box" style="border-left-color:#10b981;font-size:0.82rem;">{desc_map[algo]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎨 Légende")
    st.markdown("🟡 Nœud en cours d'exploration")
    st.markdown("🟢 Nœud visité / finalisé")
    st.markdown("🔵 Chemin optimal (Dijkstra)")

# Calcul des étapes
pos = compute_layout(g["nodes"])
dist_final, prev_final = None, None
if algo == "Dijkstra":
    steps, dist_final, prev_final = dijkstra_steps(g["nodes"], g["edges"], start_node)
elif algo == "BFS":
    steps = bfs_steps(g["nodes"], g["edges"], start_node)
else:
    steps = dfs_steps(g["nodes"], g["edges"], start_node)

with col_viz:
    fig = make_animated_fig(g["nodes"], g["edges"], pos, steps, algo, end_node, dist_final, prev_final)
    st.plotly_chart(fig, width='stretch', key=f"gr_{graph_name}_{algo}_{start_node}")

    # Table distances Dijkstra
    if algo == "Dijkstra" and dist_final:
        st.markdown("---")
        st.markdown(f"#### 📊 Distances depuis **{start_node}**")
        cols = st.columns(len(g["nodes"]))
        for i, node in enumerate(g["nodes"]):
            d     = dist_final.get(node, float('inf'))
            label = f"{int(d)} km" if d != float('inf') else "∞"
            color = "#f59e0b" if node==start_node else ("#10b981" if d!=float('inf') else "#ef4444")
            cols[i].markdown(f"""
            <div style="background:#111118;border:1px solid #1e1e2e;border-radius:8px;
                        padding:0.6rem;text-align:center;font-family:'Space Mono',monospace;">
                <div style="color:{color};font-weight:700;font-size:1rem;">{node}</div>
                <div style="font-size:0.8rem;color:#94a3b8;">{label}</div>
            </div>""", unsafe_allow_html=True)
