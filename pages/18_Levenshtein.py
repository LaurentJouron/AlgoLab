import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Levenshtein — Graphix", page_icon="✏️", layout="wide")
inject_css()
sidebar_nav()

# ── Algorithme ────────────────────────────────────────────────────────────────
def levenshtein_steps(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    steps = []
    steps.append({"dp": [row[:] for row in dp], "i": 0, "j": 0, "op": "init",
                  "desc": "Initialisation : ligne 0 = nb insertions, colonne 0 = nb suppressions"})
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
                op, desc = "match", f"'{s1[i-1]}' = '{s2[j-1]}' — même lettre, coût 0 → dp[{i}][{j}] = {dp[i][j]}"
            else:
                ins  = dp[i][j-1] + 1
                sup  = dp[i-1][j] + 1
                repl = dp[i-1][j-1] + 1
                dp[i][j] = min(ins, sup, repl)
                best = "insertion" if dp[i][j]==ins else "suppression" if dp[i][j]==sup else "remplacement"
                op   = "edit"
                desc = f"'{s1[i-1]}' ≠ '{s2[j-1]}' → min(ins={ins}, sup={sup}, repl={repl}) = <b>{dp[i][j]}</b> ({best})"
            steps.append({"dp": [row[:] for row in dp], "i": i, "j": j, "op": op, "desc": desc})
    # Chemin de retour
    path, ci, cj = [], m, n
    while ci > 0 or cj > 0:
        path.append((ci, cj))
        if ci == 0:                                          cj -= 1
        elif cj == 0:                                        ci -= 1
        elif dp[ci][cj] == dp[ci-1][cj-1] and s1[ci-1] == s2[cj-1]: ci -= 1; cj -= 1
        elif dp[ci][cj] == dp[ci-1][cj-1] + 1:             ci -= 1; cj -= 1
        elif dp[ci][cj] == dp[ci][cj-1] + 1:               cj -= 1
        else:                                                ci -= 1
    path.append((0, 0)); path.reverse()
    steps.append({"dp": [row[:] for row in dp], "i": m, "j": n, "op": "done",
                  "path": path,
                  "desc": f"✅ Distance({s1}, {s2}) = <b>{dp[m][n]}</b> opération(s)"})
    return steps, dp[m][n]

# ── Visualisation table DP ────────────────────────────────────────────────────
def make_dp_fig(dp, s1, s2, ci, cj, op, path=None):
    m, n = len(s1), len(s2)
    path_set = set(path) if path else set()
    # Couleur de fond de chaque cellule via shapes
    cell_colors = {}
    for i in range(m+1):
        for j in range(n+1):
            if (i,j) in path_set:        cell_colors[(i,j)] = "rgba(16,185,129,0.35)"
            elif i == ci and j == cj:
                if op == "edit":         cell_colors[(i,j)] = "rgba(245,158,11,0.45)"
                elif op == "match":      cell_colors[(i,j)] = "rgba(124,58,237,0.4)"
                else:                    cell_colors[(i,j)] = "rgba(6,182,212,0.3)"
            elif i <= ci and j <= cj:    cell_colors[(i,j)] = "rgba(30,58,95,0.5)"
            else:                        cell_colors[(i,j)] = "rgba(15,23,42,0.2)"

    fig = go.Figure()
    # Heatmap de fond
    z = [[dp[i][j] for j in range(n+1)] for i in range(m+1)]
    fig.add_trace(go.Heatmap(z=z,
        x=list(range(n+1)), y=list(range(m+1)),
        colorscale=[[0,"#0f172a"],[0.4,"#1e3a5f"],[1,"#312e81"]],
        showscale=False, xgap=3, ygap=3,
        hovertemplate="dp[%{y}][%{x}] = %{z}<extra></extra>"))

    # Annotations : valeurs + en-têtes
    annotations = []
    # En-tête colonnes : "" + lettres de s2
    for j in range(n+1):
        label = "" if j == 0 else s2[j-1]
        annotations.append(dict(x=j, y=m+0.7, text=f"<b>{label}</b>", showarrow=False,
                                 font=dict(size=14, color="#06b6d4", family="Space Mono"),
                                 xanchor="center"))
    # En-tête lignes : "" + lettres de s1
    for i in range(m+1):
        label = "" if i == 0 else s1[i-1]
        annotations.append(dict(x=-0.7, y=i, text=f"<b>{label}</b>", showarrow=False,
                                 font=dict(size=14, color="#f59e0b", family="Space Mono"),
                                 xanchor="center"))
    # Valeurs DP
    for i in range(m+1):
        for j in range(n+1):
            color = "#10b981" if (i,j) in path_set else \
                    "#f59e0b" if (i==ci and j==cj and op=="edit") else \
                    "#a78bfa" if (i==ci and j==cj) else "#e2e8f0"
            annotations.append(dict(x=j, y=i, text=str(dp[i][j]), showarrow=False,
                                     font=dict(size=13, color=color, family="Space Mono"),
                                     xanchor="center"))
    fig.update_layout(
        paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False,
                   range=[-1.2, n+0.5]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False,
                   range=[-0.5, m+1.2], autorange=False),
        annotations=annotations,
        margin=dict(l=30, r=20, t=30, b=20),
        height=max(300, (m+2)*46),
    )
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;">✏️ LEVENSHTEIN</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Distance de Levenshtein</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Nombre minimal d\'opérations (insertion, suppression, remplacement) pour transformer un mot en un autre. La table DP se remplit cellule par cellule — chaque case = coût optimal pour ce préfixe.</div>', unsafe_allow_html=True)

col_ctrl, col_viz = st.columns([1, 3])

EXAMPLES = [("chat","chien"),("kitten","sitting"),("python","typhon"),
            ("bonjour","bonsoir"),("algo","altruiste")]

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    ex_choice = st.selectbox("Exemple", [f"{a} → {b}" for a,b in EXAMPLES] + ["✏️ Personnalisé"])
    if "Personnalisé" in ex_choice:
        s1 = st.text_input("Mot source", "chat", max_chars=10)
        s2 = st.text_input("Mot cible",  "chien", max_chars=10)
    else:
        idx = [f"{a} → {b}" for a,b in EXAMPLES].index(ex_choice)
        s1, s2 = EXAMPLES[idx]
    s1, s2 = s1[:10], s2[:10]
    steps, dist = levenshtein_steps(s1, s2)
    st.markdown(f'<span class="complexity-badge">O(m×n) — {len(s1)+1}×{len(s2)+1} cellules</span>', unsafe_allow_html=True)
    st.metric("Distance", dist, help=f"Il faut {dist} opération(s) pour transformer '{s1}' en '{s2}'")
    st.markdown("---")
    st.markdown("""
    <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
    <b>Récurrence :</b><br>
    Si s1[i] == s2[j] :<br>
    &nbsp;&nbsp;dp[i][j] = dp[i-1][j-1] <i>(match, coût 0)</i><br><br>
    Sinon :<br>
    &nbsp;&nbsp;dp[i][j] = 1 + min(<br>
    &nbsp;&nbsp;&nbsp;&nbsp;dp[i][j-1],   <i>insertion</i><br>
    &nbsp;&nbsp;&nbsp;&nbsp;dp[i-1][j],   <i>suppression</i><br>
    &nbsp;&nbsp;&nbsp;&nbsp;dp[i-1][j-1]  <i>remplacement</i><br>
    &nbsp;&nbsp;)
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("🟢 **Vert** = chemin optimal")
    st.markdown("🟡 **Jaune** = cellule active (édition)")
    st.markdown("🟣 **Violet** = cellule active (match)")
    st.markdown("🔵 **Bleu** = calculée")
    st.markdown("*Glisse le slider pour remplir la table*")

with col_viz:
    step_idx = st.slider("Étape", 0, len(steps)-1, 0, key="lev_step")
    s = steps[step_idx]
    st.markdown(f'<div class="info-box" style="border-left-color:#10b981;">{s["desc"]}</div>', unsafe_allow_html=True)
    st.markdown(f"##### 📋 Table DP — <span style='color:#f59e0b'>lignes={s1}</span>, <span style='color:#06b6d4'>colonnes={s2}</span>", unsafe_allow_html=True)
    fig = make_dp_fig(s["dp"], s1, s2, s["i"], s["j"], s["op"], s.get("path"))
    st.plotly_chart(fig, use_container_width=True, key=f"lev_{step_idx}")

    # Reconstruction des opérations (étape finale)
    if s.get("path") and len(s["path"]) > 1:
        st.markdown("---")
        st.markdown("##### 🔍 Opérations optimales")
        ops = []
        for k in range(1, len(s["path"])):
            pi, pj = s["path"][k-1]; ci2, cj2 = s["path"][k]
            if   ci2==pi+1 and cj2==pj+1 and s1[pi]==s2[pj]: ops.append(("match",      s1[pi], s2[pj], "#10b981"))
            elif ci2==pi+1 and cj2==pj+1:                     ops.append(("remplacement",s1[pi], s2[pj], "#f59e0b"))
            elif ci2==pi   and cj2==pj+1:                     ops.append(("insertion",   "·",   s2[pj], "#06b6d4"))
            elif ci2==pi+1 and cj2==pj:                       ops.append(("suppression", s1[pi],"·",    "#ef4444"))
        icons = {"match":"=","remplacement":"→","insertion":"+","suppression":"−"}
        cols  = st.columns(min(len(ops), 10))
        for k, (op_name, cf, ct, col) in enumerate(ops):
            cols[k % len(cols)].markdown(f"""
            <div style="text-align:center;background:#111118;border:1px solid #1e1e2e;
                        border-top:3px solid {col};border-radius:6px;padding:5px 3px;
                        font-family:'Space Mono',monospace;font-size:0.72rem;margin-bottom:4px;">
                <div style="color:{col};font-size:1.1rem;">{icons[op_name]}</div>
                <div style="color:#e2e8f0;">{cf}→{ct}</div>
                <div style="color:#64748b;font-size:0.65rem;">{op_name[:4]}</div>
            </div>""", unsafe_allow_html=True)
