import streamlit as st
import plotly.graph_objects as go
import heapq, math, sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Dijkstra Carte — Graphix", page_icon="🗺️", layout="wide"
)
inject_css()
sidebar_nav()

# ── Données : villes françaises avec coordonnées réelles ──────────────────────
VILLES = {
    "Paris": (2.347, 48.859),
    "Lyon": (4.832, 45.748),
    "Marseille": (5.369, 43.297),
    "Bordeaux": (-0.579, 44.837),
    "Toulouse": (1.444, 43.605),
    "Nantes": (-1.554, 47.218),
    "Strasbourg": (7.745, 48.573),
    "Lille": (3.057, 50.630),
    "Rennes": (-1.678, 48.114),
    "Montpellier": (3.877, 43.610),
}

ROUTES = [
    ("Paris", "Lyon", 465),
    ("Paris", "Bordeaux", 579),
    ("Paris", "Nantes", 385),
    ("Paris", "Lille", 225),
    ("Paris", "Strasbourg", 490),
    ("Paris", "Rennes", 350),
    ("Lyon", "Marseille", 315),
    ("Lyon", "Toulouse", 535),
    ("Lyon", "Montpellier", 300),
    ("Lyon", "Strasbourg", 490),
    ("Marseille", "Montpellier", 160),
    ("Marseille", "Toulouse", 405),
    ("Bordeaux", "Toulouse", 245),
    ("Bordeaux", "Nantes", 345),
    ("Nantes", "Rennes", 110),
    ("Toulouse", "Montpellier", 245),
    ("Lille", "Strasbourg", 530),
]


def dijkstra_steps(start, end):
    graph = {v: [] for v in VILLES}
    for u, v, w in ROUTES:
        graph[u].append((v, w))
        graph[v].append((u, w))

    dist = {v: float("inf") for v in VILLES}
    prev = {v: None for v in VILLES}
    dist[start] = 0
    heap = [(0, start)]
    visited = set()
    steps = []

    steps.append(
        {
            "dist": dict(dist),
            "visited": set(),
            "current": None,
            "frontier": {start},
            "prev": dict(prev),
            "desc": f"Initialisation — distance de <b>{start}</b> = 0, toutes les autres = ∞",
        }
    )

    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        steps.append(
            {
                "dist": dict(dist),
                "visited": set(visited),
                "current": u,
                "frontier": set(n for n, _ in graph[u] if n not in visited),
                "prev": dict(prev),
                "desc": f"Visite <b>{u}</b> (distance = {d} km) — exploration des voisins",
            }
        )
        if u == end:
            break
        for v, w in graph[u]:
            if v not in visited and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))
                steps.append(
                    {
                        "dist": dict(dist),
                        "visited": set(visited),
                        "current": u,
                        "frontier": set(),
                        "prev": dict(prev),
                        "desc": f"Mise à jour : <b>{u}</b>→<b>{v}</b> = {dist[u]}+{w} = <b>{dist[v]} km</b>",
                    }
                )

    # Reconstruit le chemin
    path, cur = [], end
    while cur:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    steps.append(
        {
            "dist": dict(dist),
            "visited": set(visited),
            "current": end,
            "frontier": set(),
            "prev": dict(prev),
            "path": path,
            "desc": f"✅ Chemin optimal <b>{start} → {end}</b> = <b>{dist[end]} km</b>",
        }
    )
    return steps, dist[end], path


def reconstruct_path_from_prev(prev, end):
    """Reconstruit le chemin connu jusqu'ici depuis prev (partiel ou final)."""
    if not prev or prev.get(end) is None:
        return []
    path, cur = [], end
    visited_back = set()
    while cur and cur not in visited_back:
        visited_back.add(cur)
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path


def make_map_fig(step, start, end):
    fig = go.Figure()

    # Chemin connu à cette étape (depuis prev courant)
    path_nodes = step.get("path") or reconstruct_path_from_prev(
        step.get("prev", {}), end
    )
    path_edges = set()
    for i in range(len(path_nodes) - 1):
        path_edges.add((path_nodes[i], path_nodes[i + 1]))
        path_edges.add((path_nodes[i + 1], path_nodes[i]))

    # Routes de fond
    for u, v, w in ROUTES:
        x0, y0 = VILLES[u]
        x1, y1 = VILLES[v]
        on_path = (u, v) in path_edges
        color = "#10b981" if on_path else "#1e3a5f"
        width = 4 if on_path else 1.5
        fig.add_trace(
            go.Scattergeo(
                lon=[x0, x1, None],
                lat=[y0, y1, None],
                mode="lines",
                line=dict(color=color, width=width),
                hoverinfo="none",
                showlegend=False,
            )
        )
        # Label distance au milieu
        if not on_path:
            fig.add_trace(
                go.Scattergeo(
                    lon=[(x0 + x1) / 2],
                    lat=[(y0 + y1) / 2],
                    mode="text",
                    text=[str(w)],
                    textfont=dict(
                        size=9, color="#475569", family="Space Mono"
                    ),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

    # Nœuds
    for ville, (lon, lat) in VILLES.items():
        dist_val = step["dist"].get(ville, float("inf"))
        dist_str = f"{dist_val} km" if dist_val != float("inf") else "∞"

        if path_nodes and ville in path_nodes:
            color, size = "#10b981", 20
        elif ville == step.get("current"):
            color, size = "#f59e0b", 22
        elif ville in step.get("visited", set()):
            color, size = "#7c3aed", 16
        elif ville in step.get("frontier", set()):
            color, size = "#06b6d4", 15
        elif ville == start:
            color, size = "#10b981", 18
        elif ville == end:
            color, size = "#ef4444", 18
        else:
            color, size = "#1e3a5f", 13

        fig.add_trace(
            go.Scattergeo(
                lon=[lon],
                lat=[lat],
                mode="markers+text",
                marker=dict(
                    size=size,
                    color=color,
                    line=dict(color="#0a0a0f", width=1.5),
                ),
                text=[f" {ville}\n {dist_str}"],
                textposition="top right",
                textfont=dict(size=9, color="#e2e8f0", family="Space Mono"),
                name=ville,
                hovertemplate=f"<b>{ville}</b><br>Distance : {dist_str}<extra></extra>",
            )
        )

    fig.update_geos(
        projection_type="mercator",
        lonaxis=dict(range=[-5, 10]),
        lataxis=dict(range=[42, 52]),
        showland=True,
        landcolor="#111118",
        showcoastlines=True,
        coastlinecolor="#334155",
        showcountries=True,
        countrycolor="#334155",
        showframe=False,
        bgcolor="#0a0a0f",
        showrivers=False,
        showlakes=False,
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        height=520,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;">🗺️ DIJKSTRA CARTE</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-title">Dijkstra sur carte réelle</div>',
    unsafe_allow_html=True,
)
st.markdown(
    "<div class=\"page-desc\">L'algorithme de Dijkstra appliqué au réseau routier français. Chaque ville visitée est colorée, les distances sont mises à jour en temps réel. Le chemin optimal final s'affiche en vert sur la carte.</div>",
    unsafe_allow_html=True,
)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    villes_list = list(VILLES.keys())
    start = st.selectbox("Ville de départ", villes_list, index=0)
    end = st.selectbox("Ville d'arrivée", villes_list, index=2)

    if start == end:
        st.warning("Choisir deux villes différentes")
        st.stop()

    steps, dist_finale, path = dijkstra_steps(start, end)
    st.markdown(
        f'<span class="complexity-badge">O((V+E) log V) · {len(steps)} étapes</span>',
        unsafe_allow_html=True,
    )
    st.metric("Distance optimale", f"{dist_finale} km")
    st.markdown(
        f'<div class="info-box" style="border-left-color:#10b981;font-size:0.85rem;">Chemin : <b>{" → ".join(path)}</b></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        """
    <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
    <b>Algorithme :</b><br>
    1. Distance départ = 0, reste = ∞<br>
    2. Extraire le nœud non-visité le plus proche<br>
    3. Mettre à jour ses voisins si on trouve mieux<br>
    4. Répéter jusqu'à l'arrivée<br><br>
    Garantit le chemin le plus court dans un graphe à poids positifs.
    </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("🟢 **Vert** — Chemin optimal / départ")
    st.markdown("🟡 **Jaune** — Ville en cours de visite")
    st.markdown("🟣 **Violet** — Ville visitée")
    st.markdown("🔵 **Cyan** — Voisins à explorer")
    st.markdown("🔴 **Rouge** — Destination")
    st.markdown("*Glisse le slider pour avancer*")

with col_viz:
    step_idx = st.slider("Étape", 0, len(steps) - 1, 0, key="dijk_step")
    s = steps[step_idx]
    st.markdown(
        f'<div class="info-box" style="border-left-color:#10b981;">{s["desc"]}</div>',
        unsafe_allow_html=True,
    )
    fig = make_map_fig(s, start, end)
    st.plotly_chart(
        fig, use_container_width=True, key=f"dijk_{step_idx}_{start}_{end}"
    )

    # Table des distances
    st.markdown("##### 📊 Distances connues à cette étape")
    dist_cols = st.columns(5)
    for i, (ville, d) in enumerate(
        sorted(s["dist"].items(), key=lambda x: x[1])
    ):
        d_str = f"{d} km" if d != float("inf") else "∞"
        color = "#10b981" if d != float("inf") else "#475569"
        dist_cols[i % 5].markdown(
            f"""
        <div style="text-align:center;background:#111118;border:1px solid #1e1e2e;
                    border-radius:6px;padding:5px;margin-bottom:4px;
                    font-family:'Space Mono',monospace;font-size:0.72rem;">
            <div style="color:#94a3b8;">{ville}</div>
            <div style="color:{color};font-weight:700;">{d_str}</div>
        </div>""",
            unsafe_allow_html=True,
        )
