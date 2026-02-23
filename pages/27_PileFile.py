import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Pile & File — Graphix", page_icon="📚", layout="wide")
inject_css()
sidebar_nav()

# ── Helpers ───────────────────────────────────────────────────────────────────
def make_stack_fig(stack, highlight=None, label="Pile (LIFO)"):
    fig = go.Figure()
    max_size = 10
    h = 0.7  # hauteur d'un bloc

    # Zone de fond (vide)
    for i in range(max_size):
        fig.add_shape(type="rect", x0=0.1, y0=i*h, x1=0.9, y1=(i+1)*h-0.05,
                      fillcolor="#0f172a", line=dict(color="#1e2e3e", width=1))

    # Blocs remplis
    for i, val in enumerate(stack):
        is_top = (i == len(stack)-1)
        is_hl  = (highlight == "top" and is_top) or \
                 (highlight == "push" and is_top) or \
                 (highlight == "pop"  and is_top)
        color  = "#f59e0b" if highlight == "push" and is_top else \
                 "#ef4444" if highlight == "pop"  and is_top else \
                 "#7c3aed"
        fig.add_shape(type="rect", x0=0.1, y0=i*h, x1=0.9, y1=(i+1)*h-0.05,
                      fillcolor=color, line=dict(color="#0a0a0f", width=1.5))
        fig.add_annotation(x=0.5, y=i*h + h/2 - 0.02, text=str(val), showarrow=False,
                           font=dict(size=14, color="white", family="Space Mono"), align="center")
        if is_top:
            fig.add_annotation(x=1.05, y=i*h + h/2, text="← TOP", showarrow=False,
                               font=dict(size=10, color="#f59e0b", family="Space Mono"))

    # Flèche bas (LIFO)
    fig.add_annotation(x=0.5, y=max_size*h+0.2, text="⬇ PUSH / POP ⬆",
                       showarrow=False, font=dict(size=10, color="#475569", family="Space Mono"))
    fig.add_annotation(x=0.5, y=-0.3, text="BOTTOM", showarrow=False,
                       font=dict(size=9, color="#334155", family="Space Mono"))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#0a0a0f',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-0.1,1.3]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-0.6, max_size*h+0.6]),
        margin=dict(l=10, r=10, t=30, b=10), height=420,
        title=dict(text=label, font=dict(color="#94a3b8", size=12), x=0.5),
    )
    return fig

def make_queue_fig(queue, highlight=None):
    fig = go.Figure()
    max_size = 8
    w = 1.0  # largeur d'un bloc

    # Emplacements vides
    for i in range(max_size):
        fig.add_shape(type="rect", x0=i*w+0.05, y0=0.1, x1=(i+1)*w-0.05, y1=0.9,
                      fillcolor="#0f172a", line=dict(color="#1e2e3e", width=1))

    # Éléments
    for i, val in enumerate(queue):
        is_front = (i == 0)
        is_rear  = (i == len(queue)-1)
        color    = "#ef4444" if (highlight == "dequeue" and is_front) else \
                   "#10b981" if (highlight == "enqueue" and is_rear)  else \
                   "#06b6d4"
        fig.add_shape(type="rect", x0=i*w+0.05, y0=0.1, x1=(i+1)*w-0.05, y1=0.9,
                      fillcolor=color, line=dict(color="#0a0a0f", width=1.5))
        fig.add_annotation(x=i*w+w/2, y=0.5, text=str(val), showarrow=False,
                           font=dict(size=14, color="white", family="Space Mono"))
        if is_front:
            fig.add_annotation(x=i*w+w/2, y=1.1, text="FRONT\n(Dequeue ←)", showarrow=False,
                               font=dict(size=9, color="#ef4444", family="Space Mono"))
        if is_rear:
            fig.add_annotation(x=i*w+w/2, y=-0.2, text="(Enqueue →)\nREAR", showarrow=False,
                               font=dict(size=9, color="#10b981", family="Space Mono"))

    # Flèches
    fig.add_annotation(x=-0.4, y=0.5, text="⬅ OUT", showarrow=False,
                       font=dict(size=10, color="#ef4444", family="Space Mono"))
    fig.add_annotation(x=max_size*w+0.2, y=0.5, text="IN ➡", showarrow=False,
                       font=dict(size=10, color="#10b981", family="Space Mono"))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#0a0a0f',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, max_size*w+1]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-0.6, 1.6]),
        margin=dict(l=10, r=10, t=30, b=10), height=200,
        title=dict(text="File (FIFO) — Premier entré, premier sorti",
                   font=dict(color="#94a3b8", size=12), x=0.5),
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.3);color:#67e8f9;">📚 PILE & FILE</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Pile & File</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Deux structures fondamentales. La <b>Pile (Stack)</b> fonctionne en LIFO — le dernier entré est le premier sorti (comme une pile d\'assiettes). La <b>File (Queue)</b> fonctionne en FIFO — le premier entré est le premier sorti (comme une file d\'attente).</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📚 Pile (Stack)", "🚶 File (Queue)", "💡 Applications"])

# ── Pile ──────────────────────────────────────────────────────────────────────
with tab1:
    col_ctrl, col_viz = st.columns([1, 3])
    with col_ctrl:
        st.markdown("#### ⚙️ Opérations")
        if "stack" not in st.session_state:
            st.session_state.stack = [3, 7, 1]
            st.session_state.stack_log = ["Pile initialisée : [3, 7, 1]"]
            st.session_state.stack_hl = None

        val_push = st.number_input("Valeur à empiler", min_value=0, max_value=99, value=42, key="s_val")
        c1, c2 = st.columns(2)
        if c1.button("⬆ PUSH", use_container_width=True, type="primary"):
            if len(st.session_state.stack) < 10:
                st.session_state.stack.append(val_push)
                st.session_state.stack_log.append(f"PUSH {val_push} → sommet")
                st.session_state.stack_hl = "push"
            else:
                st.session_state.stack_log.append("Stack overflow ! (max 10)")
        if c2.button("⬇ POP", use_container_width=True):
            if st.session_state.stack:
                popped = st.session_state.stack.pop()
                st.session_state.stack_log.append(f"POP → {popped} retiré du sommet")
                st.session_state.stack_hl = "pop"
            else:
                st.session_state.stack_log.append("Stack underflow ! (pile vide)")
        if st.button("👁 PEEK (voir le sommet)", use_container_width=True):
            if st.session_state.stack:
                top = st.session_state.stack[-1]
                st.session_state.stack_log.append(f"PEEK → sommet = {top}")
                st.session_state.stack_hl = "top"
        if st.button("🗑 Réinitialiser", use_container_width=True):
            st.session_state.stack = []
            st.session_state.stack_log = ["Pile vidée"]
            st.session_state.stack_hl = None

        st.markdown("---")
        st.markdown(f'<span class="complexity-badge">PUSH/POP/PEEK : O(1)</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">Taille : {len(st.session_state.stack)}/10</span>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Journal des opérations :**")
        for log in reversed(st.session_state.stack_log[-8:]):
            color = "#10b981" if "PUSH" in log else "#ef4444" if "POP" in log else "#94a3b8"
            st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.78rem;color:{color};padding:2px 0;">{log}</div>', unsafe_allow_html=True)

    with col_viz:
        st.markdown(f'<div class="info-box" style="border-left-color:#06b6d4;">Pile actuelle : <b>[{", ".join(map(str,st.session_state.stack))}]</b> &nbsp;|&nbsp; Sommet (TOP) = <b>{st.session_state.stack[-1] if st.session_state.stack else "vide"}</b></div>', unsafe_allow_html=True)
        st.plotly_chart(make_stack_fig(st.session_state.stack, st.session_state.stack_hl),
                        use_container_width=True, key=f"stack_{len(st.session_state.stack)}_{st.session_state.stack_log[-1] if st.session_state.stack_log else ''}")

# ── File ──────────────────────────────────────────────────────────────────────
with tab2:
    col_ctrl2, col_viz2 = st.columns([1, 3])
    with col_ctrl2:
        st.markdown("#### ⚙️ Opérations")
        if "queue" not in st.session_state:
            st.session_state.queue = [5, 2, 8]
            st.session_state.queue_log = ["File initialisée : [5, 2, 8]"]
            st.session_state.queue_hl = None

        val_enq = st.number_input("Valeur à enqueue", min_value=0, max_value=99, value=99, key="q_val")
        c3, c4 = st.columns(2)
        if c3.button("➡ ENQUEUE", use_container_width=True, type="primary"):
            if len(st.session_state.queue) < 8:
                st.session_state.queue.append(val_enq)
                st.session_state.queue_log.append(f"ENQUEUE {val_enq} → ajouté en queue")
                st.session_state.queue_hl = "enqueue"
            else:
                st.session_state.queue_log.append("File pleine ! (max 8)")
        if c4.button("⬅ DEQUEUE", use_container_width=True):
            if st.session_state.queue:
                deq = st.session_state.queue.pop(0)
                st.session_state.queue_log.append(f"DEQUEUE → {deq} sorti du front")
                st.session_state.queue_hl = "dequeue"
            else:
                st.session_state.queue_log.append("File vide !")
        if st.button("🗑 Réinitialiser", use_container_width=True, key="q_reset"):
            st.session_state.queue = []
            st.session_state.queue_log = ["File vidée"]
            st.session_state.queue_hl = None

        st.markdown("---")
        st.markdown(f'<span class="complexity-badge">ENQUEUE/DEQUEUE : O(1)</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">Taille : {len(st.session_state.queue)}/8</span>', unsafe_allow_html=True)
        st.markdown("---")
        for log in reversed(st.session_state.queue_log[-8:]):
            color = "#10b981" if "ENQUEUE" in log else "#ef4444" if "DEQUEUE" in log else "#94a3b8"
            st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.78rem;color:{color};padding:2px 0;">{log}</div>', unsafe_allow_html=True)

    with col_viz2:
        front_val = st.session_state.queue[0] if st.session_state.queue else "vide"
        st.markdown(f'<div class="info-box" style="border-left-color:#06b6d4;">File : <b>[{", ".join(map(str,st.session_state.queue))}]</b> &nbsp;|&nbsp; Front = <b>{front_val}</b></div>', unsafe_allow_html=True)
        st.plotly_chart(make_queue_fig(st.session_state.queue, st.session_state.queue_hl),
                        use_container_width=True, key=f"queue_{len(st.session_state.queue)}_{st.session_state.queue_log[-1] if st.session_state.queue_log else ''}")
        st.markdown("""
        <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem; margin-top:1rem;">
        <b>🔴 Rouge</b> = prochain élément sorti (FRONT)<br>
        <b>🟢 Vert</b> = dernier élément ajouté (REAR)<br>
        <b>🔵 Cyan</b> = éléments en attente<br><br>
        En pratique, les files sont souvent implémentées avec <b>collections.deque</b> en Python pour que ENQUEUE et DEQUEUE soient tous les deux O(1).
        </div>""", unsafe_allow_html=True)

# ── Applications ──────────────────────────────────────────────────────────────
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📚 Pile — usages réels")
        for title, desc, ex in [
            ("Undo/Redo", "Chaque action est empilée. Ctrl+Z dépile la dernière.", "Éditeurs de texte, Photoshop"),
            ("Appels de fonctions", "La call stack empile les fonctions en cours. Une récursion infinie = stack overflow.", "Python, Java, C"),
            ("Évaluation d'expressions", "Parcourir `(3+4)*2` avec une pile pour gérer la priorité des opérateurs.", "Compilateurs, calculatrices"),
            ("Parcours DFS", "Le DFS d'un graphe peut être implémenté avec une pile explicite au lieu de la récursion.", "Navigation de labyrinthe"),
        ]:
            st.markdown(f"""
            <div class="info-box" style="border-left-color:#7c3aed;margin-bottom:8px;font-size:0.82rem;">
            <b>{title}</b> — {desc}<br>
            <span style="color:#64748b;font-size:0.75rem;">Exemple : {ex}</span>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### 🚶 File — usages réels")
        for title, desc, ex in [
            ("Parcours BFS", "Le BFS d'un graphe utilise une file pour explorer niveau par niveau.", "Dijkstra, plus court chemin"),
            ("Buffer d'impression", "Les tâches d'impression s'ajoutent à la file, traitées dans l'ordre.", "Systèmes d'exploitation"),
            ("Traitement de requêtes", "Les requêtes serveur arrivent dans une file et sont traitées par les workers.", "Serveurs web, async Python"),
            ("Simulation", "Les clients arrivent dans une file d'attente, les caissiers les servent.", "Files de banques, hôpitaux"),
        ]:
            st.markdown(f"""
            <div class="info-box" style="border-left-color:#06b6d4;margin-bottom:8px;font-size:0.82rem;">
            <b>{title}</b> — {desc}<br>
            <span style="color:#64748b;font-size:0.75rem;">Exemple : {ex}</span>
            </div>""", unsafe_allow_html=True)
