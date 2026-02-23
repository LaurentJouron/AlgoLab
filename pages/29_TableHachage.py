import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Table de Hachage — Graphix", page_icon="#️⃣", layout="wide")
inject_css()
sidebar_nav()

# ── Hash functions ────────────────────────────────────────────────────────────
def hash_fn(key, size, method="modulo"):
    if isinstance(key, int):
        h = key
    else:
        h = sum(ord(c) * (31 ** i) for i, c in enumerate(str(key))) % (10**9)
    if method == "modulo":   return h % size
    if method == "carré":    return (h * h // 100) % size
    if method == "djb2":
        v = 5381
        for c in str(key): v = ((v << 5) + v) + ord(c)
        return abs(v) % size
    return h % size

# ── Chaînage ──────────────────────────────────────────────────────────────────
def chaining_steps(keys, size, hash_method):
    table  = [[] for _ in range(size)]
    steps  = []
    steps.append({"table": [list(b) for b in table], "current_key": None, "current_idx": None,
                  "collisions": 0, "desc": f"Table de {size} buckets vide — méthode : {hash_method}"})
    collisions = 0
    for key in keys:
        idx = hash_fn(key, size, hash_method)
        if table[idx]:
            collisions += 1
            desc = f"🔴 Collision : <b>{key}</b> → bucket[{idx}] déjà occupé → chaîné"
        else:
            desc = f"✅ <b>{key}</b> → hash={idx} → bucket[{idx}] libre"
        table[idx].append(key)
        steps.append({"table": [list(b) for b in table], "current_key": key,
                      "current_idx": idx, "collisions": collisions, "desc": desc})
    steps.append({"table": [list(b) for b in table], "current_key": None, "current_idx": None,
                  "collisions": collisions,
                  "desc": f"✅ {len(keys)} clés insérées, {collisions} collision(s), facteur de charge = {len(keys)/size:.2f}"})
    return steps

# ── Sondage linéaire ──────────────────────────────────────────────────────────
def linear_probing_steps(keys, size, hash_method):
    table  = [None] * size
    steps  = []
    steps.append({"table": list(table), "current_key": None, "current_idx": None,
                  "probes": [], "collisions": 0,
                  "desc": f"Table de {size} slots vide — sondage linéaire"})
    collisions = 0
    for key in keys:
        idx   = hash_fn(key, size, hash_method)
        orig  = idx
        probes = [idx]
        probe_count = 0
        while table[idx] is not None and probe_count < size:
            idx = (idx + 1) % size
            probes.append(idx)
            probe_count += 1
        if probe_count > 0:
            collisions += 1
            desc = f"🔴 Collision : <b>{key}</b> → hash={orig} occupé → sondage → slot[{idx}] libre ({probe_count} sonde(s))"
        else:
            desc = f"✅ <b>{key}</b> → hash={idx} → slot libre"
        if probe_count < size:
            table[idx] = key
            steps.append({"table": list(table), "current_key": key, "current_idx": idx,
                          "probes": list(probes), "collisions": collisions, "desc": desc})
        else:
            steps.append({"table": list(table), "current_key": key, "current_idx": None,
                          "probes": list(probes), "collisions": collisions,
                          "desc": f"⚠️ Table pleine ! <b>{key}</b> ne peut pas être inséré"})
    steps.append({"table": list(table), "current_key": None, "current_idx": None,
                  "probes": [], "collisions": collisions,
                  "desc": f"✅ {sum(1 for t in table if t)} clés insérées sur {size} slots, {collisions} collision(s)"})
    return steps

# ── Figures ───────────────────────────────────────────────────────────────────
def make_chaining_fig(step, size):
    table, cur_idx = step["table"], step["current_idx"]
    fig = go.Figure()
    bucket_h = 0.8; max_chain = max((len(b) for b in table), default=1)
    max_chain = max(max_chain, 3)

    for i, bucket in enumerate(table):
        # Bucket label
        color_bucket = "#f59e0b" if i == cur_idx else "#1e3a5f"
        fig.add_shape(type="rect", x0=0, y0=-i*1.1, x1=1.0, y1=-i*1.1+bucket_h,
                      fillcolor=color_bucket, line=dict(color='#0a0a0f', width=1.5))
        fig.add_annotation(x=0.5, y=-i*1.1+bucket_h/2, text=f"[{i}]",
                           showarrow=False, font=dict(size=11, color='white', family='Space Mono'))
        # Chaîne
        for j, val in enumerate(bucket):
            c = "#10b981" if (i == cur_idx and j == len(bucket)-1) else "#7c3aed"
            x0_c = 1.3 + j * 1.1
            fig.add_shape(type="rect", x0=x0_c, y0=-i*1.1, x1=x0_c+0.9, y1=-i*1.1+bucket_h,
                          fillcolor=c, line=dict(color='#0a0a0f', width=1.5))
            fig.add_annotation(x=x0_c+0.45, y=-i*1.1+bucket_h/2, text=str(val),
                               showarrow=False, font=dict(size=10, color='white', family='Space Mono'))
            if j < len(bucket)-1:
                fig.add_annotation(x=x0_c+0.95, y=-i*1.1+bucket_h/2, text="→",
                                   showarrow=False, font=dict(size=12, color='#475569'))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#0a0a0f',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False,
                   range=[-0.1, 1.3 + (max_chain)*1.1]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False,
                   range=[-(size)*1.1+0.2, 0.9]),
        margin=dict(l=10, r=10, t=10, b=10), height=max(300, size * 38),
    )
    return fig

def make_probing_fig(step, size):
    table, cur_idx = step["table"], step["current_idx"]
    probes = set(step.get("probes", []))
    cols = min(size, 13)
    rows = (size + cols - 1) // cols
    fig = go.Figure()
    for i in range(size):
        row, col = i // cols, i % cols
        val = table[i]
        if i == cur_idx:           fill = "#10b981"
        elif i in probes:          fill = "#f59e0b"
        elif val is not None:      fill = "#7c3aed"
        else:                      fill = "#0f172a"
        fig.add_shape(type="rect", x0=col, y0=-row, x1=col+0.9, y1=-row+0.9,
                      fillcolor=fill, line=dict(color='#0a0a0f', width=1))
        label = str(val) if val is not None else str(i)
        color_txt = 'white' if val is not None or i in probes or i == cur_idx else '#334155'
        fig.add_annotation(x=col+0.45, y=-row+0.45, text=label, showarrow=False,
                           font=dict(size=9, color=color_txt, family='Space Mono'))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#0a0a0f',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-0.1, cols]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-(rows), 1]),
        margin=dict(l=10, r=10, t=10, b=10), height=max(200, rows*50+30),
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);color:#fcd34d;">#️⃣ TABLE DE HACHAGE</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Table de Hachage</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Accès, insertion et recherche en <b>O(1) amortis</b>. Une fonction de hachage convertit une clé en index. Quand deux clés tombent au même index — une <b>collision</b> — deux stratégies : le <b>chaînage</b> (listes liées) ou le <b>sondage linéaire</b> (chercher la prochaine case libre).</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔗 Chaînage", "🔍 Sondage linéaire", "📐 Fonctions de hachage"])

DEFAULT_KEYS = [23, 11, 45, 11, 67, 23, 89, 34, 12, 78]
DEFAULT_STR  = "chat chien chat oiseau chat cheval lapin"

# ── Chaînage ──────────────────────────────────────────────────────────────────
with tab1:
    col_ctrl, col_viz = st.columns([1, 3])
    with col_ctrl:
        st.markdown("#### ⚙️ Paramètres")
        size_c  = st.slider("Taille de la table", 4, 15, 7, key="ht_size_c")
        raw_c   = st.text_input("Clés (entiers)", "23 11 45 67 23 89 34 11", key="ht_keys_c")
        hm_c    = st.selectbox("Fonction de hachage", ["modulo","djb2"], key="ht_hm_c")
        try:
            keys_c = [int(v) for v in raw_c.split()][:12]
        except:
            keys_c = DEFAULT_KEYS[:8]

        steps_c = chaining_steps(keys_c, size_c, hm_c)
        n_col_c = steps_c[-1]["collisions"]
        load_c  = len(keys_c) / size_c

        st.markdown(f'<span class="complexity-badge">Recherche O(1+α) moy.</span>', unsafe_allow_html=True)
        st.metric("Collisions", n_col_c)
        st.metric("Facteur de charge α", f"{load_c:.2f}")
        st.markdown("---")
        st.markdown(f"""
        <div class="info-box" style="border-left-color:#7c3aed; font-size:0.82rem;">
        Chaque bucket contient une <b>liste chaînée</b>.<br>
        En cas de collision, on ajoute simplement à la liste.<br><br>
        <b>Recherche :</b> hash(clé) → parcourir la liste<br>
        Moyenne O(1 + α) où α = n/m est le facteur de charge.<br><br>
        ✅ Simple à implémenter<br>
        ❌ Perte de localité mémoire (pointeurs)
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("🟡 **Jaune** = bucket ciblé")
        st.markdown("🟢 **Vert** = élément venant d'être inséré")
        st.markdown("🟣 **Violet** = éléments existants")

    with col_viz:
        si_c = st.slider("Étape", 0, len(steps_c)-1, 0, key="ht_step_c")
        s = steps_c[si_c]
        st.markdown(f'<div class="info-box" style="border-left-color:#7c3aed;">{s["desc"]}</div>', unsafe_allow_html=True)
        st.plotly_chart(make_chaining_fig(s, size_c), use_container_width=True,
                        key=f"ht_chain_{si_c}_{size_c}_{raw_c}")

# ── Sondage linéaire ──────────────────────────────────────────────────────────
with tab2:
    col_ctrl2, col_viz2 = st.columns([1, 3])
    with col_ctrl2:
        st.markdown("#### ⚙️ Paramètres")
        size_p  = st.slider("Taille de la table", 8, 20, 13, key="ht_size_p")
        raw_p   = st.text_input("Clés (entiers)", "14 17 19 21 30 14 50 7 19", key="ht_keys_p")
        hm_p    = st.selectbox("Fonction de hachage", ["modulo","carré","djb2"], key="ht_hm_p")
        try:
            keys_p = [int(v) for v in raw_p.split()][:12]
        except:
            keys_p = [14,17,19,21,30,14,50,7,19]

        steps_p = linear_probing_steps(keys_p, size_p, hm_p)
        n_col_p = steps_p[-1]["collisions"]
        filled  = sum(1 for t in steps_p[-1]["table"] if t is not None)
        st.markdown(f'<span class="complexity-badge">O(1/(1-α)) amortis</span>', unsafe_allow_html=True)
        st.metric("Collisions", n_col_p)
        st.metric("Taux de remplissage", f"{filled}/{size_p} = {filled/size_p:.0%}")
        st.markdown("---")
        st.markdown(f"""
        <div class="info-box" style="border-left-color:#06b6d4; font-size:0.82rem;">
        Tout est dans un <b>tableau continu</b>.<br>
        Collision → chercher le prochain slot libre : idx = (idx+1) % size<br><br>
        <b>Problème :</b> "clustering" — les collisions s'accumulent en grappes et les sondages s'allongent.<br><br>
        ✅ Meilleure localité cache (tableau contigu)<br>
        ❌ Dégradation si α > 0.7 (remplissage > 70%)
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("🟢 **Vert** = slot cible (insertion réussie)")
        st.markdown("🟡 **Jaune** = slots sondés (en chemin)")
        st.markdown("🟣 **Violet** = occupé par autre clé")

    with col_viz2:
        si_p = st.slider("Étape", 0, len(steps_p)-1, 0, key="ht_step_p")
        s2   = steps_p[si_p]
        st.markdown(f'<div class="info-box" style="border-left-color:#06b6d4;">{s2["desc"]}</div>', unsafe_allow_html=True)
        st.plotly_chart(make_probing_fig(s2, size_p), use_container_width=True,
                        key=f"ht_probe_{si_p}_{size_p}_{raw_p}")

        # Distribution des longueurs de chaînes
        table = s2["table"]
        if any(t is not None for t in table):
            occ_per_slot = [1 if t is not None else 0 for t in table]
            fig3 = go.Figure(go.Bar(
                x=[f"slot {i}" for i in range(size_p)], y=occ_per_slot,
                marker=dict(color=["#7c3aed" if t is not None else "#0f172a" for t in table],
                            line=dict(color='#0a0a0f', width=1)),
                text=[str(t) if t is not None else "" for t in table],
                textposition='outside',
                textfont=dict(size=9, color='#e2e8f0', family='Space Mono'),
            ))
            fig3.update_layout(
                paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
                font=dict(color='#e2e8f0'),
                xaxis=dict(showgrid=False, tickfont=dict(size=8)),
                yaxis=dict(showgrid=False, showticklabels=False),
                margin=dict(l=10,r=10,t=10,b=40), height=140, showlegend=False,
            )
            st.plotly_chart(fig3, use_container_width=True, key=f"ht_dist_{si_p}_{size_p}")

# ── Fonctions de hachage ──────────────────────────────────────────────────────
with tab3:
    st.markdown("#### 📐 Comparaison des fonctions de hachage")
    st.markdown("Pour une même liste de clés et une même table, voir comment chaque fonction les distribue.")
    size_demo = st.slider("Taille table de démo", 5, 15, 10, key="ht_demo_size")
    keys_demo = list(range(1, 21))
    cols_fn = st.columns(3)
    for col_fn, fn in zip(cols_fn, ["modulo","carré","djb2"]):
        buckets = [[] for _ in range(size_demo)]
        for k in keys_demo:
            buckets[hash_fn(k, size_demo, fn)].append(k)
        lens = [len(b) for b in buckets]
        collisions_d = sum(max(0, l-1) for l in lens)
        fig_fn = go.Figure(go.Bar(
            x=[f"[{i}]" for i in range(size_demo)], y=lens,
            marker=dict(color=["#ef4444" if l > 1 else "#7c3aed" if l == 1 else "#0f172a"
                               for l in lens],
                        line=dict(color='#0a0a0f', width=1)),
            text=lens, textposition='outside',
            textfont=dict(size=9, color='#e2e8f0', family='Space Mono'),
        ))
        fig_fn.update_layout(
            paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
            font=dict(color='#e2e8f0'),
            title=dict(text=f"Fonction : {fn} ({collisions_d} collisions)",
                       font=dict(size=11, color='#94a3b8'), x=0.5),
            xaxis=dict(showgrid=False, tickfont=dict(size=9)),
            yaxis=dict(showgrid=True, gridcolor='#1e1e2e'),
            margin=dict(l=20,r=10,t=35,b=30), height=200, showlegend=False,
        )
        col_fn.plotly_chart(fig_fn, use_container_width=True, key=f"ht_fn_{fn}_{size_demo}")
