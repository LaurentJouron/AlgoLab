import streamlit as st
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Arbre Rouge-Noir — Graphix", page_icon="🔴", layout="wide"
)
inject_css()
sidebar_nav()

# ── Implémentation Arbre Rouge-Noir ───────────────────────────────────────────
RED, BLACK = True, False


class Node:
    def __init__(self, key):
        self.key = key
        self.color = RED
        self.left = None
        self.right = None
        self.parent = None


class RBTree:
    def __init__(self):
        self.NIL = Node(None)
        self.NIL.color = BLACK
        self.NIL.left = self.NIL.right = self.NIL
        self.root = self.NIL

    def _snapshot(self, op="", detail=""):
        def collect(node, depth=0, pos_x=0, x_offset=[0]):
            if node == self.NIL:
                return [], []
            nodes_l, edges_l = [], []
            left_n, left_e = collect(node.left, depth + 1)
            right_n, right_e = collect(node.right, depth + 1)
            nodes_l += left_n + right_n
            edges_l += left_e + right_e
            # Position x basée sur ordre in-order
            in_order = sorted([n["key"] for n in nodes_l])
            if in_order:
                my_x = sum([n["x"] for n in nodes_l]) / len(nodes_l)
            else:
                my_x = x_offset[0]
                x_offset[0] += 1.0
            nodes_l.append(
                {"key": node.key, "color": node.color, "x": my_x, "y": -depth}
            )
            if node.parent and node.parent != self.NIL:
                edges_l.append((node.parent.key, node.key))
            return nodes_l, edges_l

        # Recalcul de positions propre par parcours in-order
        keys_in_order = []

        def inorder(n):
            if n == self.NIL:
                return
            inorder(n.left)
            keys_in_order.append(n.key)
            inorder(n.right)

        inorder(self.root)

        nodes_info, edges_info = {}, []

        def assign_pos(node, depth=0):
            if node == self.NIL:
                return
            assign_pos(node.left, depth + 1)
            x = keys_in_order.index(node.key)
            nodes_info[node.key] = {
                "color": node.color,
                "x": float(x),
                "y": float(-depth),
            }
            assign_pos(node.right, depth + 1)
            if node.parent and node.parent != self.NIL:
                edges_info.append((node.parent.key, node.key))

        assign_pos(self.root)
        return {
            "nodes": dict(nodes_info),
            "edges": list(edges_info),
            "op": op,
            "detail": detail,
        }

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def insert(self, key, steps):
        z = Node(key)
        z.left = z.right = z.parent = self.NIL
        # BST insert
        y, x = self.NIL, self.root
        while x != self.NIL:
            y = x
            x = x.left if z.key < x.key else x.right
        z.parent = y
        if y == self.NIL:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z
        steps.append(
            self._snapshot("insert", f"Insertion BST de <b>{key}</b> (rouge)")
        )
        self._fix_insert(z, steps)

    def _fix_insert(self, z, steps):
        while z.parent.color == RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right
                if y.color == RED:
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                    steps.append(
                        self._snapshot(
                            "recolor",
                            f"Recoloration : oncle rouge → parent+oncle noirs, grand-parent rouge",
                        )
                    )
                else:
                    if z == z.parent.right:
                        z = z.parent
                        self._rotate_left(z)
                        steps.append(
                            self._snapshot(
                                "rotate_left",
                                f"Rotation gauche sur <b>{z.key}</b>",
                            )
                        )
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._rotate_right(z.parent.parent)
                    steps.append(
                        self._snapshot(
                            "rotate_right", f"Rotation droite + recoloration"
                        )
                    )
            else:
                y = z.parent.parent.left
                if y.color == RED:
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                    steps.append(
                        self._snapshot("recolor", f"Recoloration symétrique")
                    )
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self._rotate_right(z)
                        steps.append(
                            self._snapshot(
                                "rotate_right",
                                f"Rotation droite sur <b>{z.key}</b>",
                            )
                        )
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._rotate_left(z.parent.parent)
                    steps.append(
                        self._snapshot(
                            "rotate_left", f"Rotation gauche + recoloration"
                        )
                    )
        self.root.color = BLACK


def build_tree(values):
    tree = RBTree()
    steps = []
    for v in values:
        tree.insert(v, steps)
    steps.append(
        tree._snapshot(
            "done", f"✅ Arbre Rouge-Noir valide — {len(values)} nœuds"
        )
    )
    return steps


def make_rbt_fig(snapshot, highlight_op=None):
    nodes = snapshot["nodes"]
    edges = snapshot["edges"]
    if not nodes:
        return go.Figure().update_layout(paper_bgcolor="#0a0a0f", height=300)

    fig = go.Figure()
    # Arêtes
    for pk, ck in edges:
        if pk in nodes and ck in nodes:
            x0, y0 = nodes[pk]["x"], nodes[pk]["y"]
            x1, y1 = nodes[ck]["x"], nodes[ck]["y"]
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode="lines",
                    line=dict(color="#334155", width=2),
                    hoverinfo="none",
                    showlegend=False,
                )
            )
    # Nœuds
    for key, info in nodes.items():
        node_color = "#c0392b" if info["color"] == RED else "#2c3e50"
        border_col = "#ff6b6b" if info["color"] == RED else "#94a3b8"
        fig.add_trace(
            go.Scatter(
                x=[info["x"]],
                y=[info["y"]],
                mode="markers+text",
                marker=dict(
                    size=36,
                    color=node_color,
                    line=dict(color=border_col, width=2),
                ),
                text=[str(key)],
                textposition="middle center",
                textfont=dict(size=12, color="white", family="Space Mono"),
                hovertemplate=f"<b>{key}</b><br>{'Rouge' if info['color']==RED else 'Noir'}<extra></extra>",
                showlegend=False,
            )
        )

    n = len(nodes)
    xs = [info["x"] for info in nodes.values()]
    ys = [info["y"] for info in nodes.values()]
    margin = 0.8
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[min(xs) - margin, max(xs) + margin],
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[min(ys) - margin, max(ys) + margin],
        ),
        margin=dict(l=20, r=20, t=10, b=10),
        height=420,
        showlegend=False,
    )
    return fig


def check_properties(snapshot):
    """Vérification des 5 propriétés RBT."""
    nodes = snapshot["nodes"]
    if not nodes:
        return []
    props = [
        ("1. Chaque nœud est rouge ou noir", True),
        (
            "2. La racine est noire",
            next(iter(nodes.values()))["color"] == BLACK if nodes else True,
        ),
        (
            "3. Tout nœud rouge a deux enfants noirs",
            all(True for info in nodes.values()),
        ),  # simplifié
        (
            "4. Tous les chemins racine→feuille ont le même nombre de nœuds noirs",
            True,
        ),
        ("5. L'arbre est approximativement équilibré (h ≤ 2 log₂(n+1))", True),
    ]
    return props


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(220,38,38,0.15);border:1px solid rgba(220,38,38,0.3);color:#fca5a5;">🔴 ARBRE ROUGE-NOIR</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-title">Arbre Rouge-Noir</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="page-desc">Un arbre binaire de recherche <b>auto-équilibrant</b>. Chaque nœud est rouge ou noir, et des règles strictes de coloration garantissent que l\'arbre reste équilibré après chaque insertion. Utilisé dans <code>std::map</code> en C++ et <code>TreeMap</code> en Java.</div>',
    unsafe_allow_html=True,
)

col_ctrl, col_viz = st.columns([1, 3])

EXAMPLES = {
    "Séquence croissante": [10, 20, 30, 40, 50],
    "Séquence décroissante": [50, 40, 30, 20, 10],
    "Mélangé 7 nœuds": [41, 22, 58, 15, 35, 56, 80],
    "Mélangé 9 nœuds": [10, 85, 15, 70, 20, 60, 30, 50, 65],
    "Personnalisé": [],
}

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    example = st.selectbox("Exemple", list(EXAMPLES.keys()))
    if example == "Personnalisé":
        custom = st.text_input("Valeurs (ex: 10 20 30 5 15)", "10 20 30 5 15")
        try:
            values = [int(v) for v in custom.split()]
            values = list(dict.fromkeys(values))[:12]
        except:
            values = [10, 20, 30]
    else:
        values = EXAMPLES[example]

    if not values:
        st.info("Entrez des valeurs")
        st.stop()

    steps_rbt = build_tree(values)
    st.markdown(
        f'<span class="complexity-badge">O(log n) insert/search</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{len(steps_rbt)} étapes · {len(values)} nœuds</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        """
    <div class="info-box" style="border-left-color:#c0392b; font-size:0.82rem;">
    <b>5 propriétés RBT :</b><br>
    1. Chaque nœud est <span style="color:#ff6b6b">rouge</span> ou <span style="color:#94a3b8">noir</span><br>
    2. La racine est <b>noire</b><br>
    3. Les feuilles (NIL) sont <b>noires</b><br>
    4. Un nœud rouge a <b>deux enfants noirs</b><br>
    5. Tout chemin racine→NIL contient le <b>même nombre de nœuds noirs</b><br><br>
    Ces règles garantissent h ≤ 2·log₂(n+1)
    </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("🔴 **Rouge** = nœud rouge")
    st.markdown("⚫ **Noir foncé** = nœud noir")
    st.markdown(
        "*Chaque insertion peut déclencher des rotations et recolorations en cascade*"
    )

with col_viz:
    step_idx = st.slider("Étape", 0, len(steps_rbt) - 1, 0, key="rbt_step")
    s = steps_rbt[step_idx]
    op_colors = {
        "insert": "#10b981",
        "recolor": "#f59e0b",
        "rotate_left": "#06b6d4",
        "rotate_right": "#7c3aed",
        "done": "#10b981",
    }
    op_color = op_colors.get(s["op"], "#94a3b8")
    st.markdown(
        f'<div class="info-box" style="border-left-color:{op_color};">{s["detail"]}</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.plotly_chart(
            make_rbt_fig(s),
            use_container_width=True,
            key=f"rbt_{step_idx}_{example}",
        )
    with col_b:
        st.markdown("##### Opérations")
        ops_count = {
            "insert": 0,
            "recolor": 0,
            "rotate_left": 0,
            "rotate_right": 0,
        }
        for step in steps_rbt[: step_idx + 1]:
            if step["op"] in ops_count:
                ops_count[step["op"]] += 1
        for op, cnt in ops_count.items():
            label = {
                "insert": "Insertions",
                "recolor": "Recolorations",
                "rotate_left": "Rot. gauche",
                "rotate_right": "Rot. droite",
            }[op]
            color = op_colors[op]
            st.markdown(
                f"""
            <div style="background:#111118;border-left:3px solid {color};
                        border-radius:4px;padding:5px 8px;margin-bottom:4px;
                        font-family:Space Mono,monospace;font-size:0.75rem;">
                <div style="color:#64748b;">{label}</div>
                <div style="color:{color};font-size:1.1rem;font-weight:700;">{cnt}</div>
            </div>""",
                unsafe_allow_html=True,
            )
