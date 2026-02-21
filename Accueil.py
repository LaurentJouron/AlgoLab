import streamlit as st
import sys, os, base64
from PIL import Image

sys.path.append(os.path.dirname(__file__))
from utils.styles import inject_css, sidebar_nav

_favicon = Image.open(
    os.path.join(os.path.dirname(__file__), "assets", "favicon.ico")
)

st.set_page_config(
    page_title="Graphix — Visualisateur d'Algorithmes",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar_nav()
with st.sidebar:
    st.markdown("---")
    st.markdown(
        '<div class="nav-label">À propos</div>', unsafe_allow_html=True
    )
    st.caption(
        "Application de démonstration d'algorithmes classiques avec visualisation interactive étape par étape."
    )


# ── Hero ──────────────────────────────────────────────────────────────────────
def _get_logo_b64():
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


logo_b64 = _get_logo_b64()
if logo_b64:
    st.markdown(
        f"""
    <div style="display:flex;align-items:center;gap:1.5rem;margin-bottom:0.5rem;">
        <img src="data:image/png;base64,{logo_b64}"
             style="width:72px;height:72px;border-radius:50%;
                    box-shadow:0 0 24px rgba(191,30,46,0.5);flex-shrink:0;" />
        <div>
            <div class="hero-badge" style="margin-bottom:6px;">DÉMO PROFESSIONNELLE · v2.0</div>
            <div class="hero-title" style="margin:0;">Graphix</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="hero-badge">DÉMO PROFESSIONNELLE · v2.0</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-title">Graphix</div>', unsafe_allow_html=True
    )


st.markdown(
    '<div class="hero-sub">Explorez et visualisez les algorithmes fondamentaux de l\'informatique en temps réel. Chaque étape expliquée, chaque décision tracée.</div>',
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        '<div class="stat-box"><div class="stat-num">12</div><div class="stat-label">Pages</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        '<div class="stat-box"><div class="stat-num">20+</div><div class="stat-label">Algorithmes</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        '<div class="stat-box"><div class="stat-num">4</div><div class="stat-label">Paradigmes</div></div>',
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        '<div class="stat-box"><div class="stat-num">100%</div><div class="stat-label">Interactif</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("### Choisir un algorithme")
st.markdown("<br>", unsafe_allow_html=True)

# ── Cards ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
    <div class="algo-card purple">
        <div class="card-icon">📊</div>
        <div class="card-title">Algorithmes de Tri</div>
        <div class="card-desc">Visualisez pas à pas le tri à bulles, tri fusion et tri rapide. Comparez leurs performances et complexités temporelles sur des données aléatoires.</div>
        <span class="card-tag tag-purple">O(n²) → O(n log n)</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Tri.py", label="▶ Ouvrir le Tri")

with col2:
    st.markdown(
        """
    <div class="algo-card cyan">
        <div class="card-icon">🗼</div>
        <div class="card-title">Tours de Hanoï</div>
        <div class="card-desc">Observez la résolution récursive emblématique des tours de Hanoï. Chaque mouvement de disque illustré avec sa logique sous-jacente.</div>
        <span class="card-tag tag-cyan">O(2ⁿ) récursif</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Hanoi.py", label="▶ Ouvrir Hanoï")

col3, col4 = st.columns(2)

with col3:
    st.markdown(
        """
    <div class="algo-card amber">
        <div class="card-icon">🎒</div>
        <div class="card-title">Sac à Dos (Knapsack)</div>
        <div class="card-desc">Résolution par programmation dynamique du problème du sac à dos 0/1. Visualisation de la table DP et reconstruction de la solution optimale.</div>
        <span class="card-tag tag-amber">Prog. Dynamique · NP-difficile</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_SacADos.py", label="▶ Ouvrir Sac à Dos")

with col4:
    st.markdown(
        """
    <div class="algo-card green">
        <div class="card-icon">🕸️</div>
        <div class="card-title">Algorithmes de Graphes</div>
        <div class="card-desc">Explorez Dijkstra pour le chemin le plus court et BFS/DFS pour le parcours de graphes. Visualisation des nœuds explorés en temps réel.</div>
        <span class="card-tag tag-green">Dijkstra · BFS · DFS</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/4_Graphes.py", label="▶ Ouvrir Graphes")

col5, col6 = st.columns(2)

with col5:
    st.markdown(
        """
    <div class="algo-card purple">
        <div class="card-icon">🔍</div>
        <div class="card-title">Recherche Binaire</div>
        <div class="card-desc">Trouver un élément dans un tableau trié en divisant l'espace par deux à chaque étape. La zone active, le pivot et les zones éliminées visualisés en temps réel.</div>
        <span class="card-tag tag-purple">O(log n) · Diviser pour régner</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/5_RechercheB.py", label="▶ Ouvrir Recherche Binaire")

with col6:
    st.markdown(
        """
    <div class="algo-card red">
        <div class="card-icon">♛</div>
        <div class="card-title">N-Reines</div>
        <div class="card-desc">Placer N reines sur un échiquier sans qu'elles se menacent. Le backtracking explore chaque possibilité et recule dès qu'un conflit est détecté.</div>
        <span class="card-tag tag-red">Backtracking · O(N!)</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/6_NReines.py", label="▶ Ouvrir N-Reines")

col7, col8 = st.columns(2)

with col7:
    st.markdown(
        """
    <div class="algo-card green">
        <div class="card-icon">🧬</div>
        <div class="card-title">Jeu de la Vie de Conway</div>
        <div class="card-desc">Un automate cellulaire fascinant : des structures complexes émergent de 4 règles simples. Glider, Canon de Gosper, oscillateurs et plus encore.</div>
        <span class="card-tag tag-green">Automate cellulaire · O(n×m)</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/7_Conway.py", label="▶ Ouvrir Jeu de la Vie")

with col8:
    st.markdown(
        """
    <div class="algo-card amber">
        <div class="card-icon">🌀</div>
        <div class="card-title">Labyrinthe</div>
        <div class="card-desc">Deux algorithmes en un : DFS génère un labyrinthe parfait, puis BFS trouve le chemin le plus court. Génération et résolution animées étape par étape.</div>
        <span class="card-tag tag-amber">DFS génération · BFS résolution</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/8_Labyrinthe.py", label="▶ Ouvrir Labyrinthe")

col9, col10 = st.columns(2)

with col9:
    st.markdown(
        """
    <div class="algo-card green">
        <div class="card-icon">🌳</div>
        <div class="card-title">Arbres Binaires de Recherche</div>
        <div class="card-desc">Insertion, recherche, suppression et parcours animés (in-order, pré-order, post-order). Chaque nœud visité est coloré en temps réel.</div>
        <span class="card-tag tag-green">O(log n) moy. · Récursif</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/9_ArbresBinaires.py", label="▶ Ouvrir Arbres Binaires")

with col10:
    st.markdown(
        """
    <div class="algo-card cyan">
        <div class="card-icon">📦</div>
        <div class="card-title">Compression de Huffman</div>
        <div class="card-desc">Construction de l'arbre de Huffman étape par étape. Les symboles fréquents reçoivent les codes les plus courts. Table des codes et taux de compression.</div>
        <span class="card-tag tag-cyan">O(n log n) · Compression sans perte</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/10_Huffman.py", label="▶ Ouvrir Huffman")

col11, col12 = st.columns(2)

with col11:
    st.markdown(
        """
    <div class="algo-card red">
        <div class="card-icon">🔐</div>
        <div class="card-title">Chiffrement César & RSA</div>
        <div class="card-desc">Deux paradigmes cryptographiques : César par décalage alphabétique (symétrique) et RSA par arithmétique modulaire (asymétrique, clé publique/privée).</div>
        <span class="card-tag tag-red">Cryptographie · Symétrique & Asymétrique</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/11_Chiffrement.py", label="▶ Ouvrir Chiffrement")

with col12:
    st.markdown(
        """
    <div class="algo-card amber">
        <div class="card-icon">⭐</div>
        <div class="card-title">Algorithme A*</div>
        <div class="card-desc">Chemin optimal sur grille avec heuristique Manhattan. Plus efficace que Dijkstra grâce à f(n)=g(n)+h(n). Open set violet, chemin cyan.</div>
        <span class="card-tag tag-amber">O((V+E) log V) · Heuristique</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/12_AStar.py", label="▶ Ouvrir A*")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("### 🛠️ Outils")
st.markdown("<br>", unsafe_allow_html=True)
col13, col14 = st.columns(2)

with col13:
    st.markdown(
        """
    <div class="algo-card cyan">
        <div class="card-icon">📈</div>
        <div class="card-title">Dashboard & Performances</div>
        <div class="card-desc">Benchmark en temps réel des algorithmes sur ta machine. Comparaison des tris, recherche linéaire vs binaire, et visualisation des courbes de complexité.</div>
        <span class="card-tag tag-cyan">Temps réels · Comparatif</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/0_Dashboard.py", label="▶ Ouvrir Dashboard")

with col14:
    st.markdown(
        """
    <div class="algo-card purple">
        <div class="card-icon">🎓</div>
        <div class="card-title">Quiz Algorithmique</div>
        <div class="card-desc">Teste tes connaissances avec 16 questions sur les algorithmes de Graphix. Score, explications détaillées et filtrage par thème.</div>
        <span class="card-tag tag-purple">16 questions · Éducatif</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/13_Quiz.py", label="▶ Ouvrir Quiz")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown(
    "<p style=\"color:#64748b;font-size:0.8rem;font-family:'Space Mono',monospace;text-align:center;\">Graphix · Construit avec Python & Streamlit</p>",
    unsafe_allow_html=True,
)
