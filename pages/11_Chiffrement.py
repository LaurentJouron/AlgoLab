import streamlit as st
import plotly.graph_objects as go
import math, sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Chiffrement — Graphix", page_icon="🔐", layout="wide"
)
inject_css()
sidebar_nav()

# ── César ─────────────────────────────────────────────────────────────────────


def cesar_encode(text, shift):
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


def cesar_steps(text, shift):
    steps = []
    result = []
    for i, ch in enumerate(text):
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            orig_pos = ord(ch) - base
            enc_pos = (orig_pos + shift) % 26
            enc = chr(enc_pos + base)
            result.append(enc)
            steps.append(
                {
                    "index": i,
                    "char": ch,
                    "encoded": enc,
                    "orig_pos": orig_pos,
                    "enc_pos": enc_pos,
                    "result_so_far": "".join(result),
                    "desc": f"'{ch}' (position {orig_pos}) + décalage {shift} mod 26 = position {enc_pos} → '<b>{enc}</b>'",
                }
            )
        else:
            result.append(ch)
            steps.append(
                {
                    "index": i,
                    "char": ch,
                    "encoded": ch,
                    "orig_pos": None,
                    "enc_pos": None,
                    "result_so_far": "".join(result),
                    "desc": f"'{ch}' — non alphabétique, conservé tel quel",
                }
            )
    return steps


def make_cesar_grid(text, shift, current_index):
    """Grille alphabet original / chiffré avec la lettre active mise en valeur."""
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    shifted = alphabet[shift:] + alphabet[:shift]

    # Ligne originale
    orig_colors = [
        (
            "#f59e0b"
            if i == (ord(text[current_index].upper()) - ord("A"))
            and text[current_index].isalpha()
            else "#1e3a5f"
        )
        for i in range(26)
    ]
    # Ligne chiffrée
    if current_index < len(text) and text[current_index].isalpha():
        enc_pos = (ord(text[current_index].upper()) - ord("A") + shift) % 26
        enc_colors = [
            "#10b981" if i == enc_pos else "#111118" for i in range(26)
        ]
    else:
        enc_colors = ["#111118"] * 26

    fig = go.Figure()

    # Alphabet original (ligne du haut)
    fig.add_trace(
        go.Bar(
            x=alphabet,
            y=[1] * 26,
            marker=dict(
                color=orig_colors, line=dict(color="#0a0a0f", width=1)
            ),
            text=alphabet,
            textposition="inside",
            textfont=dict(size=11, color="white", family="Space Mono"),
            name="Original",
            showlegend=True,
            hoverinfo="none",
        )
    )
    # Alphabet chiffré (ligne du bas)
    fig.add_trace(
        go.Bar(
            x=alphabet,
            y=[1] * 26,
            marker=dict(color=enc_colors, line=dict(color="#0a0a0f", width=1)),
            text=shifted,
            textposition="inside",
            textfont=dict(size=11, color="white", family="Space Mono"),
            name="Chiffré (+" + str(shift) + ")",
            showlegend=True,
            hoverinfo="none",
        )
    )
    fig.update_layout(
        barmode="stack",
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        font=dict(color="#e2e8f0", family="DM Sans"),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        legend=dict(
            bgcolor="#111118",
            bordercolor="#1e1e2e",
            x=0,
            y=1.15,
            orientation="h",
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=160,
    )
    return fig


def make_cesar_progress(text, step_idx, steps):
    """Barre de progression du texte chiffré."""
    if step_idx < 0:
        return None
    s = steps[step_idx]
    result = s["result_so_far"]
    remaining = "_" * (len(text) - len(result))
    full = result + remaining

    colors = []
    for i, ch in enumerate(full):
        if i < len(result):
            colors.append("#10b981")
        else:
            colors.append("#1e293b")

    fig = go.Figure(
        go.Bar(
            x=list(range(len(full))),
            y=[1] * len(full),
            marker=dict(color=colors, line=dict(width=0)),
            text=list(full),
            textposition="inside",
            textfont=dict(size=12, color="white", family="Space Mono"),
            hoverinfo="none",
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, 1.5],
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        height=70,
        showlegend=False,
        bargap=0.05,
    )
    return fig


# ── RSA ───────────────────────────────────────────────────────────────────────


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def mod_inverse(e, phi):
    for d in range(2, phi):
        if (e * d) % phi == 1:
            return d
    return None


def rsa_compute(p, q, message):
    n = p * q
    phi = (p - 1) * (q - 1)
    e = next(c for c in range(2, phi) if math.gcd(c, phi) == 1)
    d = mod_inverse(e, phi)

    enc_pairs = []
    dec_pairs = []
    for ch in message:
        m = ord(ch)
        if m < n:
            c = pow(m, e, n)
            enc_pairs.append((ch, m, c))
    for ch, m, c in enc_pairs:
        m2 = pow(c, d, n)
        dec_pairs.append((c, m2, chr(m2)))

    return n, phi, e, d, enc_pairs, dec_pairs


def make_rsa_flow(enc_pairs, dec_pairs, e, d, n, highlight_idx=None):
    """Visualisation du flux M → C → M en barres groupées."""
    if not enc_pairs:
        return None
    chars = [p[0] for p in enc_pairs]
    m_vals = [p[1] for p in enc_pairs]
    c_vals = [p[2] for p in enc_pairs]
    m2_vals = [p[1] for p in dec_pairs] if dec_pairs else []

    hl_color_m = [
        "#f59e0b" if i == highlight_idx else "#7c3aed"
        for i in range(len(chars))
    ]
    hl_color_c = [
        "#ef4444" if i == highlight_idx else "#1e3a5f"
        for i in range(len(chars))
    ]
    hl_color_m2 = [
        "#10b981" if i == highlight_idx else "#1e293b"
        for i in range(len(chars))
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="m (ASCII original)",
            x=chars,
            y=m_vals,
            marker_color=hl_color_m,
            text=m_vals,
            textposition="outside",
            textfont=dict(size=9, color="white", family="Space Mono"),
        )
    )
    fig.add_trace(
        go.Bar(
            name=f"c = m^{e} mod {n} (chiffré)",
            x=chars,
            y=c_vals,
            marker_color=hl_color_c,
            text=c_vals,
            textposition="outside",
            textfont=dict(size=9, color="white", family="Space Mono"),
        )
    )
    if m2_vals:
        fig.add_trace(
            go.Bar(
                name=f"m' = c^{d} mod {n} (déchiffré)",
                x=chars,
                y=m2_vals,
                marker_color=hl_color_m2,
                text=m2_vals,
                textposition="outside",
                textfont=dict(size=9, color="white", family="Space Mono"),
            )
        )
    fig.update_layout(
        barmode="group",
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        font=dict(color="#e2e8f0", family="DM Sans"),
        xaxis=dict(showgrid=False, title="Caractères"),
        yaxis=dict(showgrid=True, gridcolor="#1e1e2e", title="Valeur"),
        legend=dict(bgcolor="#111118", bordercolor="#1e1e2e"),
        margin=dict(l=30, r=10, t=10, b=40),
        height=300,
    )
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;">🔐 CHIFFREMENT</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-title">Chiffrement César & RSA</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-desc">Deux paradigmes cryptographiques : <b>César</b> par décalage alphabétique (symétrique) et <b>RSA</b> par arithmétique modulaire (asymétrique). Chaque lettre chiffrée étape par étape.</div>',
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(
    ["🔄  César — Chiffrement symétrique", "🔑  RSA — Chiffrement asymétrique"]
)

# ────────────────────────────────────────────────────────────────────────────
# TAB CÉSAR
# ────────────────────────────────────────────────────────────────────────────
with tab1:
    col_ctrl, col_viz = st.columns([1, 3])

    with col_ctrl:
        st.markdown("#### ⚙️ Paramètres")
        text_c = st.text_input(
            "Texte à chiffrer", value="HELLO GRAPHIX", key="cesar_text"
        ).upper()
        shift_c = st.slider("Décalage (clé)", 1, 25, 3, key="cesar_shift")

        encrypted_c = cesar_encode(text_c, shift_c)
        decrypted_c = cesar_encode(encrypted_c, 26 - shift_c)

        st.markdown(
            f'<span class="complexity-badge">O(n) · clé = {shift_c}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(
            f"""
        <div class="info-box" style="border-left-color:#7c3aed;">
        <b>Original :</b><br><code style="color:#e2e8f0;">{text_c}</code><br><br>
        <b>Chiffré :</b><br><code style="color:#f59e0b;">{encrypted_c}</code><br><br>
        <b>Déchiffré :</b><br><code style="color:#10b981;">{decrypted_c}</code>
        </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("#### 🧠 Formule")
        st.markdown(
            """
        <div class="info-box" style="border-left-color:#7c3aed; font-size:0.82rem;">
        <b>Chiffrement :</b> C = (M + k) mod 26<br>
        <b>Déchiffrement :</b> M = (C − k) mod 26<br><br>
        Vulnérable : seulement <b>25 clés possibles</b> → cassable par force brute en secondes.
        </div>""",
            unsafe_allow_html=True,
        )

    with col_viz:
        steps_c = cesar_steps(text_c, shift_c)
        alpha_only = [
            i for i, s in enumerate(steps_c) if s["orig_pos"] is not None
        ]

        step_idx = st.slider(
            "Lettre en cours", 0, len(steps_c) - 1, 0, key="cesar_step"
        )
        s = steps_c[step_idx]

        st.markdown(
            f'<div class="info-box" style="border-left-color:#7c3aed;">{s["desc"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("##### 🔤 Correspondance alphabets (original → chiffré)")
        st.plotly_chart(
            make_cesar_grid(text_c, shift_c, step_idx),
            width="stretch",
            key=f"cesar_grid_{step_idx}",
        )

        st.markdown("##### 📝 Texte en cours de chiffrement")
        prog_fig = make_cesar_progress(text_c, step_idx, steps_c)
        if prog_fig:
            st.plotly_chart(
                prog_fig, width="stretch", key=f"cesar_prog_{step_idx}"
            )

        # Table de correspondance complète
        st.markdown("---")
        st.markdown("##### 📋 Table de substitution complète")
        alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        shifted = alphabet[shift_c:] + alphabet[:shift_c]
        cols5 = st.columns(13)
        for i in range(13):
            cols5[i].markdown(
                f"""
            <div style="text-align:center;font-family:'Space Mono',monospace;font-size:0.75rem;
                        background:#111118;border:1px solid #1e1e2e;border-radius:4px;padding:4px 2px;">
                <div style="color:#94a3b8;">{alphabet[i]}</div>
                <div style="color:#7c3aed;">↓</div>
                <div style="color:#f59e0b;">{shifted[i]}</div>
            </div>""",
                unsafe_allow_html=True,
            )
        cols5b = st.columns(13)
        for i in range(13, 26):
            cols5b[i - 13].markdown(
                f"""
            <div style="text-align:center;font-family:'Space Mono',monospace;font-size:0.75rem;
                        background:#111118;border:1px solid #1e1e2e;border-radius:4px;padding:4px 2px;margin-top:4px;">
                <div style="color:#94a3b8;">{alphabet[i]}</div>
                <div style="color:#7c3aed;">↓</div>
                <div style="color:#f59e0b;">{shifted[i]}</div>
            </div>""",
                unsafe_allow_html=True,
            )

# ────────────────────────────────────────────────────────────────────────────
# TAB RSA
# ────────────────────────────────────────────────────────────────────────────
with tab2:
    col_ctrl, col_viz = st.columns([1, 3])

    with col_ctrl:
        st.markdown("#### ⚙️ Paramètres")
        st.markdown("*Petits nombres premiers pour la démo visuelle*")
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        p_rsa = st.selectbox("Premier p", primes, index=4, key="rsa_p")
        q_rsa = st.selectbox(
            "Premier q",
            [x for x in primes if x != p_rsa],
            index=5,
            key="rsa_q",
        )
        msg_rsa = st.text_input("Message", value="HI", key="rsa_msg")

        n_r, phi_r, e_r, d_r, enc_pairs, dec_pairs = rsa_compute(
            p_rsa, q_rsa, msg_rsa
        )

        st.markdown("---")
        st.markdown("#### 🗝️ Clés générées")
        st.markdown(
            f"""
        <div class="info-box" style="border-left-color:#ef4444; font-size:0.85rem;">
        n = {p_rsa} × {q_rsa} = <b>{n_r}</b><br>
        φ(n) = {p_rsa-1} × {q_rsa-1} = <b>{phi_r}</b><br><br>
        🔓 Clé publique : <b style="color:#06b6d4;">(e={e_r}, n={n_r})</b><br>
        🔒 Clé privée :   <b style="color:#ef4444;">(d={d_r}, n={n_r})</b>
        </div>""",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("#### 🧠 Formules")
        st.markdown(
            f"""
        <div class="info-box" style="border-left-color:#ef4444; font-size:0.82rem;">
        <b>Chiffrement :</b> c = m^e mod n<br>
        <b>Déchiffrement :</b> m = c^d mod n<br><br>
        e × d ≡ 1 (mod φ(n))<br><br>
        Sécurité : factoriser n en p×q est<br>
        <b>computationnellement infaisable</b><br>
        pour de grands nombres (2048+ bits).
        </div>""",
            unsafe_allow_html=True,
        )

    with col_viz:
        if any(ord(c) >= n_r for c in msg_rsa):
            st.warning(
                f"⚠️ Certains caractères ont une valeur ASCII ≥ {n_r}. Choisis de plus grands p et q."
            )
        else:
            hl_idx = st.slider(
                "Caractère mis en évidence",
                0,
                max(len(enc_pairs) - 1, 0),
                0,
                key="rsa_hl",
            )

            # Diagramme de flux M → C → M
            st.markdown("##### 🔄 Flux de chiffrement / déchiffrement")
            rsa_fig = make_rsa_flow(
                enc_pairs, dec_pairs, e_r, d_r, n_r, hl_idx
            )
            if rsa_fig:
                st.plotly_chart(
                    rsa_fig, width="stretch", key=f"rsa_flow_{hl_idx}"
                )

            # Détail de la lettre sélectionnée
            if hl_idx < len(enc_pairs):
                ch, m_val, c_val = enc_pairs[hl_idx]
                m2_val = (
                    dec_pairs[hl_idx][1] if hl_idx < len(dec_pairs) else "?"
                )
                st.markdown(
                    f"""
                <div class="info-box" style="border-left-color:#ef4444;">
                Lettre <b style="color:#f59e0b;">'{ch}'</b> | ASCII = <b>{m_val}</b><br><br>
                🔒 Chiffrement : {m_val}^{e_r} mod {n_r} = <b style="color:#ef4444;">{c_val}</b><br>
                🔓 Déchiffrement : {c_val}^{d_r} mod {n_r} = <b style="color:#10b981;">{m2_val}</b> → '<b>{chr(m2_val) if isinstance(m2_val, int) else '?'}</b>'
                </div>""",
                    unsafe_allow_html=True,
                )

            # Table de résultats
            st.markdown("---")
            st.markdown("##### 📋 Tableau complet")
            if enc_pairs:
                header_cols = st.columns(4)
                header_cols[0].markdown("**Lettre**")
                header_cols[1].markdown("**m (ASCII)**")
                header_cols[2].markdown(f"**c = m^{e_r} mod {n_r}**")
                header_cols[3].markdown(f"**m' = c^{d_r} mod {n_r}**")
                for i, (ch, m_v, c_v) in enumerate(enc_pairs):
                    m2 = dec_pairs[i][1] if i < len(dec_pairs) else "?"
                    row = st.columns(4)
                    bg = "background:#1e293b;" if i == hl_idx else ""
                    for col_j, val in zip(
                        row, [f"'{ch}'", str(m_v), str(c_v), str(m2)]
                    ):
                        col_j.markdown(
                            f'<div style="{bg}font-family:Space Mono,monospace;font-size:0.85rem;padding:4px;">{val}</div>',
                            unsafe_allow_html=True,
                        )
