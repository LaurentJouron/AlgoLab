import streamlit as st
from pathlib import Path

# Chemin vers le fichier CSS, résolu depuis l'emplacement de ce fichier
_CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"


def inject_css():
    """Lit style.css et l'injecte dans la page Streamlit."""
    css = _CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def sidebar_nav():
    """Barre de navigation latérale commune à toutes les pages."""
    with st.sidebar:
        st.markdown('<div class="nav-label">⚡ Graphix</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)
        st.page_link("Accueil.py",            label="🏠 Accueil")
        st.page_link("pages/1_Tri.py",        label="📊 Algorithmes de Tri")
        st.page_link("pages/2_Hanoi.py",      label="🗼 Tours de Hanoï")
        st.page_link("pages/3_SacADos.py",    label="🎒 Sac à Dos")
        st.page_link("pages/4_Graphes.py",    label="🕸️ Graphes")
        st.page_link("pages/5_RechercheB.py", label="🔍 Recherche Binaire")
        st.page_link("pages/6_NReines.py",    label="♛ N-Reines")
        st.page_link("pages/7_Conway.py",     label="🧬 Jeu de la Vie")
        st.page_link("pages/8_Labyrinthe.py", label="🌀 Labyrinthe")
