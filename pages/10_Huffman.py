import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import heapq, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Huffman — Graphix", page_icon="📦", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithme ────────────────────────────────────────────────────────────────

class HNode:
    def __init__(self, char, freq, left=None, right=None):
        self.char  = char
        self.freq  = freq
        self.left  = left
        self.right = right
    def __lt__(self, other): return self.freq < other.freq

def build_huffman(text):
    freq = {}
    for c in text: freq[c] = freq.get(c, 0) + 1

    heap = [HNode(c, f) for c, f in sorted(freq.items())]
    heapq.heapify(heap)

    # Snapshots à chaque fusion
    snapshots = []
    snapshots.append({
        "heap": [(n.char, n.freq) for n in sorted(heap, key=lambda x: x.freq)],
        "desc": f"File initiale : {len(heap)} symboles — on fusionne toujours les 2 moins fréquents",
        "step": "init"
    })

    while len(heap) > 1:
        left  = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HNode(f"{left.char}+{right.char}", left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)
        snapshots.append({
            "heap": [(n.char, n.freq) for n in sorted(heap, key=lambda x: x.freq)],
            "desc": f"Fusion : <b>{left.char}</b>({left.freq}) + <b>{right.char}</b>({right.freq}) → nœud interne ({merged.freq})",
            "merged_left": left.char,
            "merged_right": right.char,
            "merged_freq": merged.freq,
            "step": "merge"
        })

    root = heap[0]

    # Générer les codes
    codes = {}
    def build_codes(node, prefix=""):
        if node is None: return
        if node.left is None and node.right is None:
            codes[node.char] = prefix or "0"
            return
        build_codes(node.left,  prefix + "0")
        build_codes(node.right, prefix + "1")
    build_codes(root)

    snapshots.append({
        "heap": [],
        "desc": "✅ Arbre complet — codes assignés. Les symboles fréquents ont les codes les plus courts.",
        "step": "done", "codes": codes
    })

    orig_bits = len(text) * 8
    comp_bits = sum(len(codes[c]) * freq[c] for c in freq)
    ratio     = (1 - comp_bits / orig_bits) * 100 if orig_bits > 0 else 0

    return snapshots, freq, codes, root, orig_bits, comp_bits, ratio

# ── Visualisation ─────────────────────────────────────────────────────────────

def make_freq_bar(freq, codes, highlight_chars=None):
    """Barres de fréquence colorées par longueur de code."""
    chars  = sorted(freq.keys(), key=lambda c: -freq[c])
    freqs  = [freq[c] for c in chars]
    labels = [repr(c) if c == ' ' else c for c in chars]
    code_lens = [len(codes.get(c, '?')) for c in chars]

    # Couleur selon longueur du code
    palette = ["#10b981","#06b6d4","#7c3aed","#f59e0b","#ef4444","#ec4899"]
    max_len = max(code_lens) if code_lens else 1
    bar_colors = [palette[min(cl-1, len(palette)-1)] for cl in code_lens]

    if highlight_chars:
        bar_colors = ["#ffffff" if c in highlight_chars else bc
                      for c, bc in zip(chars, bar_colors)]

    code_texts = [codes.get(c, '…') for c in chars]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=freqs,
        marker=dict(color=bar_colors, line=dict(color='#0a0a0f', width=1)),
        text=[f"{codes.get(c,'?')}" for c in chars],
        textposition='outside',
        textfont=dict(size=10, color='#e2e8f0', family='Space Mono'),
        hovertext=[f"'{c}': freq={freq[c]}, code={codes.get(c,'?')} ({len(codes.get(c,'?'))} bits)" for c in chars],
        hoverinfo='text',
    ))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
        font=dict(color='#e2e8f0', family='DM Sans'),
        xaxis=dict(showgrid=False, title="Symboles"),
        yaxis=dict(showgrid=True, gridcolor='#1e1e2e', title="Fréquence"),
        margin=dict(l=30, r=10, t=10, b=40),
        height=280, showlegend=False,
    )
    return fig

def make_queue_bar(heap_snapshot, highlight_left=None, highlight_right=None):
    """Visualise la file de priorité sous forme de barres."""
    if not heap_snapshot:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
                          height=200, margin=dict(l=10,r=10,t=10,b=10))
        return fig

    chars  = [h[0] for h in heap_snapshot]
    freqs  = [h[1] for h in heap_snapshot]
    labels = [c[:6] + '…' if len(c) > 6 else c for c in chars]

    colors = []
    for c in chars:
        if highlight_left  and c == highlight_left:  colors.append("#f59e0b")
        elif highlight_right and c == highlight_right: colors.append("#ef4444")
        else: colors.append("#1e3a5f")

    fig = go.Figure(go.Bar(
        x=labels, y=freqs,
        marker=dict(color=colors, line=dict(color='#0a0a0f', width=1)),
        text=freqs, textposition='outside',
        textfont=dict(size=10, color='#e2e8f0', family='Space Mono'),
    ))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
        font=dict(color='#e2e8f0', family='DM Sans'),
        xaxis=dict(showgrid=False, title="Nœuds dans la file"),
        yaxis=dict(showgrid=True, gridcolor='#1e1e2e', title="Fréquence"),
        margin=dict(l=30, r=10, t=10, b=40),
        height=220, showlegend=False,
    )
    return fig

def make_encoding_visual(text, codes):
    """Affiche le texte original et son encodage bit à bit."""
    if not codes: return None
    segments = []
    palette  = ["#7c3aed","#06b6d4","#10b981","#f59e0b","#ef4444","#ec4899"]
    char_colors = {}
    for i, c in enumerate(sorted(set(text))):
        char_colors[c] = palette[i % len(palette)]

    bits_total = sum(len(codes.get(c,'')) for c in text)
    orig_bits  = len(text) * 8

    # Créer une représentation visuelle des bits
    x_pos, bit_data, colors_data, hover_data = [], [], [], []
    pos = 0
    for ch in text[:30]:  # limiter à 30 chars pour la lisibilité
        code = codes.get(ch, '')
        for bit in code:
            x_pos.append(pos)
            bit_data.append(bit)
            colors_data.append(char_colors.get(ch, '#334155'))
            hover_data.append(f"'{ch}' → bit {bit}")
            pos += 1

    fig = go.Figure(go.Bar(
        x=list(range(len(bit_data))),
        y=[1] * len(bit_data),
        marker=dict(color=colors_data, line=dict(width=0)),
        text=bit_data, textposition='inside',
        textfont=dict(size=9, color='white', family='Space Mono'),
        hovertext=hover_data, hoverinfo='text',
    ))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 1.5]),
        margin=dict(l=10, r=10, t=10, b=20),
        height=80, showlegend=False, bargap=0.05,
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(6,182,212,0.15);border:1px solid rgba(6,182,212,0.3);color:#67e8f9;">📦 COMPRESSION HUFFMAN</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Compression de Huffman</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Algorithme de compression sans perte : les symboles fréquents reçoivent les codes les plus courts. Observe la file de priorité se vider au fil des fusions.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

EXAMPLES = {
    "abracadabra":                  "abracadabra",
    "hello world":                   "hello world",
    "mississippi":                   "mississippi",
    "aaabbbcccddde":                 "aaabbbcccddde",
    "Personnalisé":                  "",
}

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    choice = st.selectbox("Texte d'exemple", list(EXAMPLES.keys()))
    if choice == "Personnalisé":
        text = st.text_input("Ton texte", value="bonjour graphix")
    else:
        text = EXAMPLES[choice]

    if not text: text = "hello"

    snapshots, freq, codes, root, orig_bits, comp_bits, ratio = build_huffman(text)

    st.markdown("---")
    st.markdown("#### 📊 Résultats")
    st.metric("Bits originaux (ASCII 8-bit)", f"{orig_bits}")
    st.metric("Bits compressés (Huffman)",    f"{comp_bits}")
    col_r1, col_r2 = st.columns(2)
    col_r1.metric("Gain",  f"{ratio:.1f} %")
    col_r2.metric("Fusions", f"{len(snapshots)-2}")

    st.markdown("---")
    st.markdown("#### 🧠 Principe")
    st.markdown("""
    <div class="info-box" style="border-left-color:#06b6d4; font-size:0.82rem;">
    1. Compter la fréquence de chaque symbole<br>
    2. Mettre tous les symboles dans une <b>file de priorité</b><br>
    3. Extraire les 2 nœuds de plus faible fréquence<br>
    4. Les fusionner en un nœud interne<br>
    5. Répéter jusqu'à n'avoir qu'une <b>racine</b><br>
    6. Parcourir l'arbre : gauche=<b>0</b>, droite=<b>1</b>
    </div>
    """, unsafe_allow_html=True)

with col_viz:
    # Slider d'étape
    step_idx = st.slider("Étape de construction", 0, len(snapshots)-1, 0, key="hf_step")
    s = snapshots[step_idx]

    st.markdown(f'<div class="info-box" style="border-left-color:#06b6d4;">{s["desc"]}</div>', unsafe_allow_html=True)

    # File de priorité à cette étape
    st.markdown("##### 📋 File de priorité (min-heap)")
    hl = s.get("merged_left")
    hr = s.get("merged_right")
    st.plotly_chart(make_queue_bar(s["heap"], hl, hr), width='stretch', key=f"hf_queue_{step_idx}")

    st.markdown("##### 📊 Fréquences & Codes Huffman")
    # Codes finaux toujours visibles (pour comprendre l'objectif)
    st.plotly_chart(make_freq_bar(freq, codes, {hl, hr} if hl else None),
                    width='stretch', key=f"hf_freq_{step_idx}")

    # Encodage visuel
    st.markdown("##### 🔢 Flux de bits encodé (30 premiers caractères)")
    enc_fig = make_encoding_visual(text, codes)
    if enc_fig:
        st.plotly_chart(enc_fig, width='stretch', key=f"hf_enc_{step_idx}")

    # Table des codes
    st.markdown("---")
    st.markdown("##### 📋 Table des codes")
    sorted_codes = sorted(codes.items(), key=lambda x: (len(x[1]), x[0]))
    n_cols = min(len(sorted_codes), 5)
    if n_cols:
        rcols = st.columns(n_cols)
        for j, (char, code) in enumerate(sorted_codes):
            display = "' '" if char == ' ' else f"'{char}'"
            col_idx = j % n_cols
            rcols[col_idx].markdown(f"""
            <div style="background:#111118;border:1px solid #1e1e2e;border-radius:8px;
                        padding:0.5rem;text-align:center;font-family:'Space Mono',monospace;
                        font-size:0.8rem;margin-bottom:6px;">
                <div style="color:#06b6d4;font-size:1.1rem;font-weight:700;">{display}</div>
                <div style="color:#fcd34d;letter-spacing:2px;">{code}</div>
                <div style="color:#64748b;font-size:0.7rem;">{freq.get(char,0)}× · {len(code)} bits</div>
            </div>""", unsafe_allow_html=True)
