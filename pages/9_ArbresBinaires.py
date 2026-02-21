import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Arbres Binaires — Graphix", page_icon="🌳", layout="wide")
inject_css()
sidebar_nav()

# ── Structure ─────────────────────────────────────────────────────────────────

class Node:
    def __init__(self, val):
        self.val   = val
        self.left  = None
        self.right = None

class BST:
    def __init__(self):
        self.root  = None
        self.steps = []

    def insert(self, val):
        self.steps = []
        self.root  = self._insert(self.root, val)

    def _insert(self, node, val):
        if node is None:
            self.steps.append(("insert_done", val))
            return Node(val)
        self.steps.append(("compare", node.val, val))
        if val < node.val:
            self.steps.append(("go_left", node.val))
            node.left  = self._insert(node.left, val)
        elif val > node.val:
            self.steps.append(("go_right", node.val))
            node.right = self._insert(node.right, val)
        else:
            self.steps.append(("duplicate", val))
        return node

    def search(self, val):
        self.steps = []
        return self._search(self.root, val)

    def _search(self, node, val):
        if node is None:
            self.steps.append(("not_found", val))
            return False
        self.steps.append(("compare", node.val, val))
        if val == node.val:
            self.steps.append(("found", val))
            return True
        elif val < node.val:
            self.steps.append(("go_left", node.val))
            return self._search(node.left, val)
        else:
            self.steps.append(("go_right", node.val))
            return self._search(node.right, val)

    def delete(self, val):
        self.steps = []
        self.root  = self._delete(self.root, val)

    def _delete(self, node, val):
        if node is None:
            self.steps.append(("not_found", val))
            return None
        self.steps.append(("compare", node.val, val))
        if val < node.val:
            self.steps.append(("go_left", node.val))
            node.left  = self._delete(node.left, val)
        elif val > node.val:
            self.steps.append(("go_right", node.val))
            node.right = self._delete(node.right, val)
        else:
            self.steps.append(("delete", val))
            if node.left is None:  return node.right
            if node.right is None: return node.left
            # Successeur in-order
            succ = node.right
            while succ.left: succ = succ.left
            self.steps.append(("replace", val, succ.val))
            node.val   = succ.val
            node.right = self._delete(node.right, succ.val)
        return node

    def traversal(self, mode):
        self.steps = []
        order = []
        if mode == "In-order (trié)":
            self._inorder(self.root, order)
        elif mode == "Pré-order":
            self._preorder(self.root, order)
        else:
            self._postorder(self.root, order)
        return order

    def _inorder(self, node, out):
        if node:
            self._inorder(node.left, out)
            out.append(node.val)
            self.steps.append(("visit", node.val))
            self._inorder(node.right, out)

    def _preorder(self, node, out):
        if node:
            out.append(node.val)
            self.steps.append(("visit", node.val))
            self._preorder(node.left, out)
            self._preorder(node.right, out)

    def _postorder(self, node, out):
        if node:
            self._postorder(node.left, out)
            self._postorder(node.right, out)
            out.append(node.val)
            self.steps.append(("visit", node.val))

# ── Layout de l'arbre ─────────────────────────────────────────────────────────

def compute_positions(node, x=0, y=0, gap=1.5, positions=None):
    if positions is None: positions = {}
    if node is None: return positions
    positions[node.val] = (x, y)
    if node.left:
        compute_positions(node.left,  x - gap / (abs(y)+1), y - 1.2, gap * 0.75, positions)
    if node.right:
        compute_positions(node.right, x + gap / (abs(y)+1), y - 1.2, gap * 0.75, positions)
    return positions

def get_edges(node, edges=None):
    if edges is None: edges = []
    if node is None: return edges
    if node.left:
        edges.append((node.val, node.left.val))
        get_edges(node.left, edges)
    if node.right:
        edges.append((node.val, node.right.val))
        get_edges(node.right, edges)
    return edges

def make_tree_fig(bst, highlight=None, visited=None, found=None):
    if bst.root is None:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor='#0a0a0f', plot_bgcolor='#111118', height=380,
                          annotations=[dict(x=0.5, y=0.5, xref='paper', yref='paper',
                                           text="Arbre vide — insère des valeurs",
                                           font=dict(color='#64748b', size=14, family='Space Mono'),
                                           showarrow=False)])
        return fig

    pos   = compute_positions(bst.root)
    edges = get_edges(bst.root)
    if visited is None: visited = set()

    traces = []
    for u, v in edges:
        x0, y0 = pos[u]; x1, y1 = pos[v]
        traces.append(go.Scatter(x=[x0,x1,None], y=[y0,y1,None], mode='lines',
                                 line=dict(color='#334155', width=2),
                                 hoverinfo='none', showlegend=False))

    node_vals   = list(pos.keys())
    node_x      = [pos[v][0] for v in node_vals]
    node_y      = [pos[v][1] for v in node_vals]
    node_colors = []
    node_sizes  = []
    for v in node_vals:
        if found is not None and v == found:
            node_colors.append("#10b981"); node_sizes.append(32)
        elif highlight is not None and v == highlight:
            node_colors.append("#f59e0b"); node_sizes.append(32)
        elif v in visited:
            node_colors.append("#7c3aed"); node_sizes.append(26)
        else:
            node_colors.append("#1e3a5f"); node_sizes.append(26)

    traces.append(go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        marker=dict(size=node_sizes, color=node_colors, line=dict(color='#0a0a0f', width=2)),
        text=[str(v) for v in node_vals],
        textfont=dict(size=11, color='white', family='Space Mono'),
        textposition='middle center',
        hoverinfo='text', hovertext=[str(v) for v in node_vals],
        showlegend=False
    ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        margin=dict(l=20, r=20, t=20, b=20),
        height=380,
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;">🌳 ARBRES BINAIRES</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Arbre Binaire de Recherche</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Insertion, suppression et recherche dans un ABR. Chaque opération est tracée nœud par nœud. Jaune = nœud en cours, violet = visité, vert = trouvé.</div>', unsafe_allow_html=True)

if "bst" not in st.session_state:
    st.session_state.bst = BST()
    for v in [50, 30, 70, 20, 40, 60, 80]:
        st.session_state.bst.insert(v)
    st.session_state.bst.steps = []

bst = st.session_state.bst

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Opérations")
    op  = st.selectbox("Opération", ["Insérer", "Rechercher", "Supprimer", "Parcours"])
    val = None

    if op in ["Insérer", "Rechercher", "Supprimer"]:
        val = st.number_input("Valeur", min_value=1, max_value=999, value=45)

    if op == "Parcours":
        mode = st.selectbox("Mode", ["In-order (trié)", "Pré-order", "Post-order"])

    if st.button("▶ Exécuter", width='stretch', type="primary"):
        if op == "Insérer":
            bst.insert(val)
            st.session_state.op_desc  = f"Insertion de {val}"
            st.session_state.op_steps = bst.steps.copy()
        elif op == "Rechercher":
            bst.search(val)
            st.session_state.op_desc  = f"Recherche de {val}"
            st.session_state.op_steps = bst.steps.copy()
        elif op == "Supprimer":
            bst.delete(val)
            st.session_state.op_desc  = f"Suppression de {val}"
            st.session_state.op_steps = bst.steps.copy()
        elif op == "Parcours":
            order = bst.traversal(mode)
            st.session_state.op_desc  = f"Parcours {mode} → {order}"
            st.session_state.op_steps = bst.steps.copy()

    if st.button("↺ Réinitialiser l'arbre", width='stretch'):
        st.session_state.bst = BST()
        for v in [50, 30, 70, 20, 40, 60, 80]:
            st.session_state.bst.insert(v)
        st.session_state.bst.steps = []
        st.session_state.pop("op_steps", None)
        st.session_state.pop("op_desc", None)
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🧠 Propriétés ABR")
    st.markdown("""
    <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
    Pour chaque nœud <b>n</b> :<br>
    • Tous les nœuds gauches &lt; n<br>
    • Tous les nœuds droits &gt; n<br>
    • Recherche/Insertion : <b>O(log n)</b> en moy.<br>
    • Pire cas (dégénéré) : <b>O(n)</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎨 Légende")
    st.markdown("🟡 **Jaune** — Nœud en cours")
    st.markdown("🟣 **Violet** — Nœud visité")
    st.markdown("🟢 **Vert** — Trouvé / Inséré")

with col_viz:
    if "op_steps" in st.session_state and st.session_state.op_steps:
        steps    = st.session_state.op_steps
        visited  = set()
        highlight, found = None, None

        # Rejoue les steps pour construire les frames
        frames_state = []
        v2 = set()
        hl, fd = None, None
        for s in steps:
            if s[0] == "compare":
                hl = s[1]
                frames_state.append((set(v2), hl, fd, f"Comparaison : nœud <b>{s[1]}</b> vs valeur <b>{s[2]}</b>"))
            elif s[0] in ("go_left","go_right"):
                v2.add(s[1])
                frames_state.append((set(v2), None, fd, f"→ {'Gauche' if s[0]=='go_left' else 'Droite'} depuis <b>{s[1]}</b>"))
            elif s[0] == "found":
                fd = s[1]
                frames_state.append((set(v2), None, fd, f"✅ Valeur <b>{s[1]}</b> trouvée !"))
            elif s[0] == "not_found":
                frames_state.append((set(v2), None, None, f"❌ Valeur <b>{s[1]}</b> introuvable"))
            elif s[0] == "insert_done":
                fd = s[1]
                frames_state.append((set(v2), None, fd, f"✅ <b>{s[1]}</b> inséré dans l'arbre"))
            elif s[0] == "delete":
                frames_state.append((set(v2), s[1], None, f"🗑️ Suppression du nœud <b>{s[1]}</b>"))
            elif s[0] == "replace":
                frames_state.append((set(v2), s[2], None, f"Remplacement par le successeur <b>{s[2]}</b>"))
            elif s[0] == "visit":
                v2.add(s[1])
                frames_state.append((set(v2), s[1], None, f"Visite : <b>{s[1]}</b> | Ordre : {sorted(v2)}"))
            elif s[0] == "duplicate":
                frames_state.append((set(v2), s[1], None, f"⚠️ <b>{s[1]}</b> déjà présent, ignoré"))

        if frames_state:
            # Build animated fig
            def frame_traces(vs, hl, fd):
                pos   = compute_positions(bst.root)
                edges = get_edges(bst.root)
                tr    = []
                for u, v in edges:
                    x0,y0=pos[u]; x1,y1=pos[v]
                    tr.append(go.Scatter(x=[x0,x1,None],y=[y0,y1,None],mode='lines',
                                        line=dict(color='#334155',width=2),hoverinfo='none',showlegend=False))
                nv = list(pos.keys())
                nc = ["#10b981" if fd==v else "#f59e0b" if hl==v else "#7c3aed" if v in vs else "#1e3a5f" for v in nv]
                ns = [32 if v in (hl,fd) else 26 for v in nv]
                tr.append(go.Scatter(
                    x=[pos[v][0] for v in nv], y=[pos[v][1] for v in nv],
                    mode='markers+text',
                    marker=dict(size=ns,color=nc,line=dict(color='#0a0a0f',width=2)),
                    text=[str(v) for v in nv],
                    textfont=dict(size=11,color='white',family='Space Mono'),
                    textposition='middle center', hoverinfo='text', showlegend=False))
                return tr

            vs0, hl0, fd0, desc0 = frames_state[0]
            fig = go.Figure(
                data=frame_traces(vs0, hl0, fd0),
                layout=go.Layout(
                    paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
                    xaxis=dict(showgrid=False,showticklabels=False,zeroline=False),
                    yaxis=dict(showgrid=False,showticklabels=False,zeroline=False),
                    margin=dict(l=20,r=20,t=55,b=80), height=420,
                    annotations=[dict(x=0.5,y=1.09,xref='paper',yref='paper',
                                      text=desc0,showarrow=False,
                                      font=dict(color='#94a3b8',size=12,family='DM Sans'),align='center')],
                    updatemenus=[dict(
                        type="buttons",showactive=False,y=-0.18,x=0.5,xanchor="center",
                        buttons=[
                            dict(label="▶  Démarrer",method="animate",
                                 args=[None,dict(frame=dict(duration=700,redraw=True),
                                                 transition=dict(duration=200,easing="cubic-in-out"),
                                                 fromcurrent=True,mode="immediate")]),
                            dict(label="⏸  Pause",method="animate",
                                 args=[[None],dict(frame=dict(duration=0,redraw=False),
                                                   mode="immediate",transition=dict(duration=0))]),
                        ],
                        font=dict(color="#e2e8f0",family="Space Mono",size=12),
                        bgcolor="#1e1e2e",bordercolor="#334155",
                    )],
                    sliders=[dict(
                        active=0,
                        currentvalue=dict(prefix="Étape : ",font=dict(color="#94a3b8",family="Space Mono",size=11),
                                          visible=True,xanchor="center"),
                        pad=dict(t=45,b=5),len=0.9,x=0.05,
                        bgcolor="#111118",bordercolor="#1e1e2e",tickcolor="#334155",
                        font=dict(color="#64748b",size=9),
                        steps=[dict(method="animate",
                                    args=[[f"ab{k}"],dict(mode="immediate",frame=dict(duration=700,redraw=True),
                                                          transition=dict(duration=200))],
                                    label=str(k)) for k in range(len(frames_state))],
                    )],
                ),
                frames=[
                    go.Frame(name=f"ab{k}",
                             data=frame_traces(vs,hl,fd),
                             layout=go.Layout(annotations=[dict(x=0.5,y=1.09,xref='paper',yref='paper',
                                                                text=desc,showarrow=False,
                                                                font=dict(color='#94a3b8',size=12,family='DM Sans'),align='center')]))
                    for k,(vs,hl,fd,desc) in enumerate(frames_state)
                ],
            )
            st.plotly_chart(fig, width='stretch', key=f"ab_{id(frames_state)}")

        if "op_desc" in st.session_state:
            st.markdown(f'<div class="info-box" style="border-left-color:#10b981;">{st.session_state.op_desc}</div>', unsafe_allow_html=True)
    else:
        st.plotly_chart(make_tree_fig(bst), width='stretch', key="ab_init")
        st.markdown('<div class="info-box" style="border-left-color:#10b981;">Arbre initialisé avec [50, 30, 70, 20, 40, 60, 80]. Choisis une opération et clique <b>▶ Exécuter</b>.</div>', unsafe_allow_html=True)
