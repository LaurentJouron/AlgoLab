import streamlit as st
import sys, os
sys.path.append(os.path.dirname(__file__))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Graphix — Visualisateur d'Algorithmes",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar_nav()
with st.sidebar:
    st.markdown("---")
    st.markdown('<div class="nav-label">À propos</div>', unsafe_allow_html=True)
    st.caption("Application de démonstration d'algorithmes classiques avec visualisation interactive étape par étape.")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-badge">DÉMO PROFESSIONNELLE · v1.0</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Graphix</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Explorez et visualisez les algorithmes fondamentaux de l\'informatique en temps réel. Chaque étape expliquée, chaque décision tracée.</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="stat-box"><div class="stat-num">8</div><div class="stat-label">Catégories</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="stat-box"><div class="stat-num">15+</div><div class="stat-label">Algorithmes</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="stat-box"><div class="stat-num">∞</div><div class="stat-label">Paramètres</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="stat-box"><div class="stat-num">100%</div><div class="stat-label">Interactif</div></div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("### Choisir un algorithme")
st.markdown("<br>", unsafe_allow_html=True)

# ── Cards ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="algo-card purple">
        <div class="card-icon">📊</div>
        <div class="card-title">Algorithmes de Tri</div>
        <div class="card-desc">Visualisez pas à pas le tri à bulles, tri fusion et tri rapide. Comparez leurs performances et complexités temporelles sur des données aléatoires.</div>
        <span class="card-tag tag-purple">O(n²) → O(n log n)</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Tri.py", label="▶ Ouvrir le Tri")

with col2:
    st.markdown("""
    <div class="algo-card cyan">
        <div class="card-icon">🗼</div>
        <div class="card-title">Tours de Hanoï</div>
        <div class="card-desc">Observez la résolution récursive emblématique des tours de Hanoï. Chaque mouvement de disque illustré avec sa logique sous-jacente.</div>
        <span class="card-tag tag-cyan">O(2ⁿ) récursif</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Hanoi.py", label="▶ Ouvrir Hanoï")

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class="algo-card amber">
        <div class="card-icon">🎒</div>
        <div class="card-title">Sac à Dos (Knapsack)</div>
        <div class="card-desc">Résolution par programmation dynamique du problème du sac à dos 0/1. Visualisation de la table DP et reconstruction de la solution optimale.</div>
        <span class="card-tag tag-amber">Prog. Dynamique · NP-difficile</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_SacADos.py", label="▶ Ouvrir Sac à Dos")

with col4:
    st.markdown("""
    <div class="algo-card green">
        <div class="card-icon">🕸️</div>
        <div class="card-title">Algorithmes de Graphes</div>
        <div class="card-desc">Explorez Dijkstra pour le chemin le plus court et BFS/DFS pour le parcours de graphes. Visualisation des nœuds explorés en temps réel.</div>
        <span class="card-tag tag-green">Dijkstra · BFS · DFS</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_Graphes.py", label="▶ Ouvrir Graphes")

col5, col6 = st.columns(2)

with col5:
    st.markdown("""
    <div class="algo-card purple">
        <div class="card-icon">🔍</div>
        <div class="card-title">Recherche Binaire</div>
        <div class="card-desc">Trouver un élément dans un tableau trié en divisant l'espace par deux à chaque étape. La zone active, le pivot et les zones éliminées visualisés en temps réel.</div>
        <span class="card-tag tag-purple">O(log n) · Diviser pour régner</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/5_RechercheB.py", label="▶ Ouvrir Recherche Binaire")

with col6:
    st.markdown("""
    <div class="algo-card red">
        <div class="card-icon">♛</div>
        <div class="card-title">N-Reines</div>
        <div class="card-desc">Placer N reines sur un échiquier sans qu'elles se menacent. Le backtracking explore chaque possibilité et recule dès qu'un conflit est détecté.</div>
        <span class="card-tag tag-red">Backtracking · O(N!)</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/6_NReines.py", label="▶ Ouvrir N-Reines")

col7, col8 = st.columns(2)

with col7:
    st.markdown("""
    <div class="algo-card green">
        <div class="card-icon">🧬</div>
        <div class="card-title">Jeu de la Vie de Conway</div>
        <div class="card-desc">Un automate cellulaire fascinant : des structures complexes émergent de 4 règles simples. Glider, Canon de Gosper, oscillateurs et plus encore.</div>
        <span class="card-tag tag-green">Automate cellulaire · O(n×m)</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/7_Conway.py", label="▶ Ouvrir Jeu de la Vie")

with col8:
    st.markdown("""
    <div class="algo-card amber">
        <div class="card-icon">🌀</div>
        <div class="card-title">Labyrinthe</div>
        <div class="card-desc">Deux algorithmes en un : DFS génère un labyrinthe parfait, puis BFS trouve le chemin le plus court. Génération et résolution animées étape par étape.</div>
        <span class="card-tag tag-amber">DFS génération · BFS résolution</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/8_Labyrinthe.py", label="▶ Ouvrir Labyrinthe")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;font-size:0.8rem;font-family:\'Space Mono\',monospace;text-align:center;">Graphix · Construit avec Python & Streamlit</p>', unsafe_allow_html=True)
