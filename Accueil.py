import streamlit as st

st.set_page_config(
    page_title="Graphix — Visualisateur d'Algorithmes",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Global ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

:root {
    --bg:       #0a0a0f;
    --surface:  #111118;
    --border:   #1e1e2e;
    --accent1:  #7c3aed;
    --accent2:  #06b6d4;
    --accent3:  #f59e0b;
    --accent4:  #10b981;
    --text:     #e2e8f0;
    --muted:    #64748b;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    color: var(--text) !important;
}

/* Remove default streamlit padding */
.block-container { padding-top: 2rem !important; }

/* Cards */
.algo-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.algo-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 4px 0 0 4px;
}
.algo-card.purple::before { background: var(--accent1); }
.algo-card.cyan::before   { background: var(--accent2); }
.algo-card.amber::before  { background: var(--accent3); }
.algo-card.green::before  { background: var(--accent4); }

.algo-card:hover {
    border-color: #333350;
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}

.card-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.card-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.card-desc { color: var(--muted); font-size: 0.9rem; line-height: 1.6; }
.card-tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    margin-top: 1rem;
}
.tag-purple { background: rgba(124,58,237,0.2); color: #a78bfa; border: 1px solid rgba(124,58,237,0.3); }
.tag-cyan   { background: rgba(6,182,212,0.2);  color: #67e8f9; border: 1px solid rgba(6,182,212,0.3); }
.tag-amber  { background: rgba(245,158,11,0.2); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
.tag-green  { background: rgba(16,185,129,0.2); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }

.hero-badge {
    display: inline-block;
    background: rgba(124,58,237,0.15);
    border: 1px solid rgba(124,58,237,0.3);
    color: #a78bfa;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    line-height: 1.1;
    background: linear-gradient(135deg, #e2e8f0 0%, #7c3aed 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
}
.hero-sub { color: var(--muted); font-size: 1.1rem; line-height: 1.7; max-width: 600px; }

.stat-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.5rem;
    text-align: center;
}
.stat-num {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent2);
}
.stat-label { color: var(--muted); font-size: 0.8rem; margin-top: 0.2rem; }

.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

/* Sidebar nav */
.nav-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    color: var(--muted);
    text-transform: uppercase;
    padding: 0.5rem 0;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="nav-label">⚡ Graphix</div>', unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        '<div class="nav-label">Navigation</div>', unsafe_allow_html=True
    )
    st.page_link(
        "Accueil.py",
        label="🏠 Accueil",
    )
    st.page_link("pages/1_Tri.py", label="📊 Algorithmes de Tri")
    st.page_link("pages/2_Hanoi.py", label="🗼 Tours de Hanoï")
    st.page_link("pages/3_SacADos.py", label="🎒 Sac à Dos")
    st.page_link("pages/4_Graphes.py", label="🕸️ Graphes")
    st.markdown("---")
    st.markdown(
        '<div class="nav-label">À propos</div>', unsafe_allow_html=True
    )
    st.caption(
        "Application de démonstration d'algorithmes classiques avec visualisation interactive étape par étape."
    )

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-badge">DÉMO PROFESSIONNELLE · v1.0</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="hero-title">Graphix</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Explorez et visualisez les algorithmes fondamentaux de l\'informatique en temps réel. Chaque étape expliquée, chaque décision tracée.</div>',
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# Stats
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        '<div class="stat-box"><div class="stat-num">4</div><div class="stat-label">Catégories</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        '<div class="stat-box"><div class="stat-num">10+</div><div class="stat-label">Algorithmes</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        '<div class="stat-box"><div class="stat-num">∞</div><div class="stat-label">Paramètres</div></div>',
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

# Cards
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

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown(
    "<p style=\"color: #64748b; font-size: 0.8rem; font-family: 'Space Mono', monospace; text-align:center;\">Graphix · Construit avec Python & Streamlit</p>",
    unsafe_allow_html=True,
)
