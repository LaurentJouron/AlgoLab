import streamlit as st
import random, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Quiz — Graphix", page_icon="🎓", layout="wide")
inject_css()
sidebar_nav()

# ── Banque de questions ───────────────────────────────────────────────────────

QUESTIONS = [
    # ── Tri ──────────────────────────────────────────────────────────────────
    {"q": "Quelle est la complexité dans le pire cas du tri à bulles ?",
     "choices": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"], "answer": 2,
     "expl": "Le tri à bulles effectue n×(n-1)/2 comparaisons dans le pire cas → O(n²).", "cat": "Tri"},
    {"q": "Lequel de ces tris est dit 'stable' (préserve l'ordre des éléments égaux) ?",
     "choices": ["Tri rapide", "Tri fusion", "Tri à bulles", "Tri fusion et Tri à bulles"], "answer": 3,
     "expl": "Le tri fusion et le tri à bulles sont stables. Le tri rapide ne l'est pas dans sa version classique.", "cat": "Tri"},
    {"q": "Quelle est la complexité moyenne du tri rapide (quicksort) ?",
     "choices": ["O(n²)", "O(n)", "O(n log n)", "O(log n)"], "answer": 2,
     "expl": "En moyenne, le pivot divise le tableau équitablement → O(n log n). Pire cas O(n²) si le pivot est toujours minimal ou maximal.", "cat": "Tri"},
    {"q": "Le tri fusion utilise quelle technique algorithmique ?",
     "choices": ["Backtracking", "Programmation dynamique", "Glouton", "Diviser pour régner"], "answer": 3,
     "expl": "Le tri fusion divise le tableau en deux moitiés, les trie récursivement, puis les fusionne → paradigme Diviser pour régner.", "cat": "Tri"},
    # ── Recherche ────────────────────────────────────────────────────────────
    {"q": "La recherche binaire nécessite que le tableau soit :",
     "choices": ["Trié", "Non trié", "De taille paire", "Rempli d'entiers"], "answer": 0,
     "expl": "La recherche binaire repose sur la comparaison avec le milieu, ce qui n'est valide que sur un tableau trié.", "cat": "Recherche"},
    {"q": "Combien d'étapes maximum pour trouver un élément dans un tableau de 1024 éléments en recherche binaire ?",
     "choices": ["1024", "512", "10", "32"], "answer": 2,
     "expl": "log₂(1024) = 10. La recherche binaire divise l'espace par 2 à chaque étape → 10 comparaisons maximum.", "cat": "Recherche"},
    # ── Graphes ──────────────────────────────────────────────────────────────
    {"q": "Quelle structure de données utilise BFS (parcours en largeur) ?",
     "choices": ["Pile (LIFO)", "File (FIFO)", "Tas (Heap)", "Arbre binaire"], "answer": 1,
     "expl": "BFS explore niveau par niveau grâce à une file FIFO : on enfile les voisins et on défile pour explorer.", "cat": "Graphes"},
    {"q": "Quelle structure de données utilise DFS (parcours en profondeur) ?",
     "choices": ["File (FIFO)", "Pile (LIFO)", "File de priorité", "Tableau"], "answer": 1,
     "expl": "DFS utilise une pile (explicite ou via la récursion/call stack) pour explorer en profondeur avant de revenir en arrière.", "cat": "Graphes"},
    {"q": "L'algorithme de Dijkstra ne fonctionne pas correctement avec :",
     "choices": ["Des graphes orientés", "Des poids négatifs", "Des graphes denses", "Des poids décimaux"], "answer": 1,
     "expl": "Dijkstra suppose des poids positifs. Un arc négatif peut invalider un chemin déjà finalisé. Pour les poids négatifs, utiliser Bellman-Ford.", "cat": "Graphes"},
    {"q": "Quelle est la différence entre A* et Dijkstra ?",
     "choices": ["A* est plus lent", "A* utilise une heuristique pour guider la recherche", "Dijkstra trouve toujours le chemin optimal, pas A*", "A* ne fonctionne que sur des grilles"], "answer": 1,
     "expl": "A* ajoute une heuristique h(n) à Dijkstra : f(n)=g(n)+h(n). Elle guide la recherche vers la cible, réduisant les nœuds explorés.", "cat": "Graphes"},
    # ── Récursivité ──────────────────────────────────────────────────────────
    {"q": "Combien de mouvements minimum faut-il pour résoudre les Tours de Hanoï avec 5 disques ?",
     "choices": ["25", "31", "16", "10"], "answer": 1,
     "expl": "La formule est 2ⁿ-1. Pour n=5 : 2⁵-1 = 31 mouvements minimum.", "cat": "Récursivité"},
    {"q": "Le backtracking dans N-Reines consiste à :",
     "choices": ["Choisir aléatoirement les positions", "Revenir en arrière quand aucune position n'est valide", "Utiliser une file de priorité", "Trier les colonnes"], "answer": 1,
     "expl": "Le backtracking tente de placer une reine, et si aucune ligne valide n'existe dans la colonne courante, il retire la dernière reine placée et essaie la suivante.", "cat": "Récursivité"},
    # ── Complexité ───────────────────────────────────────────────────────────
    {"q": "Laquelle de ces complexités est la plus efficace ?",
     "choices": ["O(n²)", "O(n log n)", "O(log n)", "O(n)"], "answer": 2,
     "expl": "O(log n) < O(n) < O(n log n) < O(n²). O(log n) est typique de la recherche binaire.", "cat": "Complexité"},
    {"q": "La programmation dynamique résout les sous-problèmes :",
     "choices": ["Une seule fois en mémorisant les résultats", "Plusieurs fois sans mémorisation", "En parallèle", "Aléatoirement"], "answer": 0,
     "expl": "La DP évite les calculs redondants en mémorisant (memoization) ou en construisant une table ascendante (tabulation).", "cat": "Complexité"},
    {"q": "Quelle est la complexité spatiale de la table DP dans le problème du Sac à Dos 0/1 (n objets, capacité W) ?",
     "choices": ["O(n)", "O(W)", "O(n×W)", "O(n²)"], "answer": 2,
     "expl": "La table DP est de dimensions (n+1)×(W+1), soit O(n×W) en espace.", "cat": "Complexité"},
    # ── Huffman ──────────────────────────────────────────────────────────────
    {"q": "Dans la compression de Huffman, quel symbole reçoit le code le plus court ?",
     "choices": ["Le symbole rare", "Le symbole fréquent", "Le premier alphabétiquement", "Le dernier de la file"], "answer": 1,
     "expl": "Huffman attribue les codes les plus courts aux symboles les plus fréquents, minimisant la longueur totale du message compressé.", "cat": "Huffman"},
    {"q": "L'arbre de Huffman est construit en fusionnant :",
     "choices": ["Les deux nœuds de fréquence maximale", "Les deux nœuds de fréquence minimale", "Les nœuds aléatoirement", "Les feuilles uniquement"], "answer": 1,
     "expl": "À chaque étape, on fusionne les deux nœuds de plus faible fréquence depuis une file de priorité (min-heap).", "cat": "Huffman"},
]

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);color:#a78bfa;">🎓 MODE ÉDUCATIF</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Quiz Algorithmique</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Teste tes connaissances sur les algorithmes de Graphix. Chaque question est tirée aléatoirement. Réponds, découvre l\'explication, et progresse !</div>', unsafe_allow_html=True)

# Init session
if "quiz_score"    not in st.session_state: st.session_state.quiz_score    = 0
if "quiz_total"    not in st.session_state: st.session_state.quiz_total    = 0
if "quiz_q"        not in st.session_state: st.session_state.quiz_q        = None
if "quiz_answered" not in st.session_state: st.session_state.quiz_answered = False
if "quiz_choice"   not in st.session_state: st.session_state.quiz_choice   = None
if "quiz_history"  not in st.session_state: st.session_state.quiz_history  = []
if "quiz_cat"      not in st.session_state: st.session_state.quiz_cat      = "Toutes"

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### 📊 Score")
    score = st.session_state.quiz_score
    total = st.session_state.quiz_total
    pct   = int(score/total*100) if total > 0 else 0

    st.markdown(f'<div class="stat-box"><div class="stat-num">{score}/{total}</div><div class="stat-label">Bonnes réponses</div></div>', unsafe_allow_html=True)
    if total > 0:
        color = "#10b981" if pct >= 70 else "#f59e0b" if pct >= 40 else "#ef4444"
        st.markdown(f'<div style="background:#111118;border:1px solid #1e1e2e;border-radius:8px;padding:0.8rem;text-align:center;margin-top:8px;"><div style="color:{color};font-size:1.5rem;font-weight:700;">{pct}%</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎯 Filtrer par thème")
    cats = ["Toutes"] + sorted(set(q["cat"] for q in QUESTIONS))
    cat  = st.selectbox("Catégorie", cats, key="quiz_cat_sel")
    st.session_state.quiz_cat = cat

    if st.button("↺ Réinitialiser le score", width='stretch'):
        st.session_state.quiz_score    = 0
        st.session_state.quiz_total    = 0
        st.session_state.quiz_q        = None
        st.session_state.quiz_answered = False
        st.session_state.quiz_history  = []
        st.rerun()

    st.markdown("---")
    st.markdown("#### 📋 Historique")
    for item in reversed(st.session_state.quiz_history[-6:]):
        icon = "✅" if item["correct"] else "❌"
        st.markdown(f'<div style="font-size:0.75rem;color:#64748b;padding:2px 0;">{icon} {item["cat"]}</div>', unsafe_allow_html=True)

with col_viz:
    filtered = [q for q in QUESTIONS if st.session_state.quiz_cat == "Toutes" or q["cat"] == st.session_state.quiz_cat]

    if not st.session_state.quiz_q or st.session_state.quiz_answered:
        if st.button("➡️ Nouvelle question", width='stretch', type="primary"):
            st.session_state.quiz_q        = random.choice(filtered)
            st.session_state.quiz_answered = False
            st.session_state.quiz_choice   = None
            st.rerun()

    q = st.session_state.quiz_q

    if q:
        cat_colors = {"Tri":"#7c3aed","Recherche":"#7c3aed","Graphes":"#10b981",
                      "Récursivité":"#06b6d4","Complexité":"#f59e0b","Huffman":"#06b6d4"}
        ccolor = cat_colors.get(q["cat"], "#94a3b8")
        st.markdown(f'<span class="page-badge" style="background:rgba(0,0,0,0.2);border:1px solid {ccolor}44;color:{ccolor};">{q["cat"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="page-title" style="font-size:1.3rem;margin:12px 0;">{q["q"]}</div>', unsafe_allow_html=True)

        if not st.session_state.quiz_answered:
            for i, choice in enumerate(q["choices"]):
                if st.button(choice, width='stretch', key=f"choice_{i}"):
                    st.session_state.quiz_choice   = i
                    st.session_state.quiz_answered = True
                    st.session_state.quiz_total   += 1
                    correct = (i == q["answer"])
                    if correct: st.session_state.quiz_score += 1
                    st.session_state.quiz_history.append({"cat": q["cat"], "correct": correct})
                    st.rerun()
        else:
            chosen  = st.session_state.quiz_choice
            correct = (chosen == q["answer"])

            for i, choice in enumerate(q["choices"]):
                if i == q["answer"]:
                    st.markdown(f'<div style="background:rgba(16,185,129,0.15);border:1px solid #10b981;border-radius:8px;padding:0.7rem 1rem;margin:4px 0;color:#10b981;font-family:DM Sans,sans-serif;">✅ {choice}</div>', unsafe_allow_html=True)
                elif i == chosen and chosen != q["answer"]:
                    st.markdown(f'<div style="background:rgba(239,68,68,0.15);border:1px solid #ef4444;border-radius:8px;padding:0.7rem 1rem;margin:4px 0;color:#ef4444;font-family:DM Sans,sans-serif;">❌ {choice}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="background:#111118;border:1px solid #1e1e2e;border-radius:8px;padding:0.7rem 1rem;margin:4px 0;color:#64748b;font-family:DM Sans,sans-serif;">{choice}</div>', unsafe_allow_html=True)

            st.markdown("---")
            color_box = "#10b981" if correct else "#ef4444"
            result_txt = "🎉 Bonne réponse !" if correct else "💡 Pas tout à fait…"
            st.markdown(f'<div class="info-box" style="border-left-color:{color_box};"><b>{result_txt}</b><br><br>{q["expl"]}</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="info-box" style="border-left-color:#7c3aed;font-size:1rem;text-align:center;">Clique sur <b>➡️ Nouvelle question</b> pour commencer !</div>', unsafe_allow_html=True)
