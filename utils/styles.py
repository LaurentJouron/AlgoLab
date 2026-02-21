import streamlit as st
from pathlib import Path
import base64

# Chemin vers le fichier CSS, résolu depuis l'emplacement de ce fichier
_CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"
_LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"


def _get_logo_b64():
    if _LOGO_PATH.exists():
        return base64.b64encode(_LOGO_PATH.read_bytes()).decode()
    return None


def inject_css():
    """Lit style.css et l'injecte dans la page Streamlit."""
    css = _CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def sidebar_nav():
    """Barre de navigation latérale commune à toutes les pages."""
    logo_b64 = _get_logo_b64()
    with st.sidebar:
        if logo_b64:
            st.markdown(
                f"""
            <div style="display:flex;align-items:center;gap:0.6rem;padding:4px 0 12px 0;">
                <img src="data:image/png;base64,{logo_b64}"
                     style="width:36px;height:36px;border-radius:50%;
                            box-shadow:0 0 10px rgba(191,30,46,0.5);flex-shrink:0;" />
                <span class="sidebar-title">Graphix</span>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="sidebar-title" style="padding:4px 0 12px 0;">Graphix</div>',
                unsafe_allow_html=True,
            )
        st.markdown("---")
        st.markdown(
            '<div class="nav-label">Navigation</div>', unsafe_allow_html=True
        )
        st.page_link("Accueil.py", label="🏠 Accueil")
        st.markdown(
            '<div style="color:#475569;font-size:0.7rem;font-family:Space Mono,monospace;padding:6px 0 2px 0;text-transform:uppercase;letter-spacing:1px;">── Algorithmes ──</div>',
            unsafe_allow_html=True,
        )
        st.page_link("pages/1_Tri.py", label="📊 Algorithmes de Tri")
        st.page_link("pages/2_Hanoi.py", label="🗼 Tours de Hanoï")
        st.page_link("pages/3_SacADos.py", label="🎒 Sac à Dos")
        st.page_link("pages/4_Graphes.py", label="🕸️ Graphes")
        st.page_link("pages/5_RechercheB.py", label="🔍 Recherche Binaire")
        st.page_link("pages/6_NReines.py", label="♛ N-Reines")
        st.page_link("pages/7_Conway.py", label="🧬 Jeu de la Vie")
        st.page_link("pages/8_Labyrinthe.py", label="🌀 Labyrinthe")
        st.page_link("pages/9_ArbresBinaires.py", label="🌳 Arbres Binaires")
        st.page_link("pages/10_Huffman.py", label="📦 Huffman")
        st.page_link("pages/11_Chiffrement.py", label="🔐 Chiffrement")
        st.page_link("pages/12_AStar.py", label="⭐ A*")
        st.markdown(
            '<div style="color:#475569;font-size:0.7rem;font-family:Space Mono,monospace;padding:6px 0 2px 0;text-transform:uppercase;letter-spacing:1px;">── Outils ──</div>',
            unsafe_allow_html=True,
        )
        st.page_link("pages/0_Dashboard.py", label="📈 Dashboard")
        st.page_link("pages/13_Quiz.py", label="🎓 Quiz")
