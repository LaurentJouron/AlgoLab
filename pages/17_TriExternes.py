import streamlit as st
import plotly.graph_objects as go
import random, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(page_title="Tris Linéaires — Graphix", page_icon="🪣", layout="wide")
inject_css()
sidebar_nav()

# ── Counting Sort ─────────────────────────────────────────────────────────────
def counting_sort_steps(arr, max_val):
    steps, count, output = [], [0]*(max_val+1), [0]*len(arr)
    steps.append({"phase":"init","arr":list(arr),"count":list(count),"output":None,
                  "hl_arr":[],"hl_count":[],"desc":"Tableau initial — on va compter chaque valeur"})
    for i, v in enumerate(arr):
        count[v] += 1
        steps.append({"phase":"count","arr":list(arr),"count":list(count),"output":None,
                      "hl_arr":[i],"hl_count":[v],
                      "desc":f"arr[{i}]={v} → count[{v}] passe à {count[v]}"})
    steps.append({"phase":"count_done","arr":list(arr),"count":list(count),"output":None,
                  "hl_arr":[],"hl_count":[],"desc":"Comptage terminé — chaque case = nb d'occurrences de cette valeur"})
    for i in range(1, max_val+1):
        count[i] += count[i-1]
        steps.append({"phase":"cumul","arr":list(arr),"count":list(count),"output":None,
                      "hl_arr":[],"hl_count":[i],
                      "desc":f"Cumul : count[{i}] += count[{i-1}] → {count[i]} (nb d'éléments ≤ {i})"})
    steps.append({"phase":"cumul_done","arr":list(arr),"count":list(count),"output":None,
                  "hl_arr":[],"hl_count":[],"desc":"Comptage cumulatif prêt — count[v] = dernière position de v dans la sortie"})
    for i in range(len(arr)-1, -1, -1):
        v = arr[i]; count[v] -= 1; output[count[v]] = v
        steps.append({"phase":"place","arr":list(arr),"count":list(count),"output":list(output),
                      "hl_arr":[i],"hl_count":[v],
                      "desc":f"Placer arr[{i}]={v} → output[{count[v]}]={v}"})
    steps.append({"phase":"done","arr":list(output),"count":list(count),"output":list(output),
                  "hl_arr":list(range(len(output))),"hl_count":[],
                  "desc":"✅ Tableau trié ! Counting Sort : O(n+k) sans aucune comparaison"})
    return steps

# ── Radix Sort ────────────────────────────────────────────────────────────────
def radix_sort_steps(arr):
    steps, current = [], list(arr)
    max_val = max(arr)
    n_digits = len(str(max_val))
    steps.append({"phase":"init","arr":list(current),"buckets":None,"pass_num":0,"digit_name":"",
                  "desc":f"Tableau initial — {n_digits} passe(s) nécessaire(s) (une par chiffre)"})
    exp = 1
    for d in range(n_digits):
        name = ["unités","dizaines","centaines","milliers"][d] if d < 4 else f"10^{d}"
        buckets = [[] for _ in range(10)]
        for v in current:
            buckets[(v // exp) % 10].append(v)
        steps.append({"phase":"distribute","arr":list(current),"buckets":[list(b) for b in buckets],
                      "pass_num":d+1,"digit_name":name,
                      "desc":f"Passe {d+1} — chiffre des <b>{name}</b> : répartition dans les seaux 0–9"})
        current = [v for b in buckets for v in b]
        steps.append({"phase":"collect","arr":list(current),"buckets":[list(b) for b in buckets],
                      "pass_num":d+1,"digit_name":name,
                      "desc":f"Passe {d+1} — collecte des seaux dans l'ordre : tableau partiellement trié"})
        exp *= 10
    steps.append({"phase":"done","arr":list(current),"buckets":None,"pass_num":n_digits,"digit_name":"",
                  "desc":f"✅ Trié en {n_digits} passe(s) — Radix Sort : O(d×n), stable, sans comparaison"})
    return steps

# ── Figures ───────────────────────────────────────────────────────────────────
def bar_fig(arr, highlights, phase, title=""):
    colors = []
    for i in range(len(arr)):
        if phase == "done":             colors.append("#10b981")
        elif i in highlights:           colors.append("#f59e0b")
        else:                           colors.append("#7c3aed")
    fig = go.Figure(go.Bar(
        x=list(range(len(arr))), y=arr,
        marker=dict(color=colors, line=dict(color='#0a0a0f', width=1)),
        text=arr, textposition='outside',
        textfont=dict(size=11, color='#e2e8f0', family='Space Mono'),
    ))
    fig.update_layout(paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
                      font=dict(color='#e2e8f0'),
                      xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                      yaxis=dict(showgrid=True, gridcolor='#1e1e2e', zeroline=False),
                      margin=dict(l=10,r=10,t=30 if title else 10,b=10),
                      title=dict(text=title, font=dict(color='#94a3b8',size=12), x=0.5) if title else None,
                      height=220, showlegend=False, bargap=0.1)
    return fig

def count_fig(count, hl_count, phase):
    colors = []
    for i in range(len(count)):
        if i in hl_count:                   colors.append("#f59e0b")
        elif phase in ("cumul","cumul_done"): colors.append("#06b6d4")
        elif count[i] > 0:                   colors.append("#7c3aed")
        else:                                colors.append("#1e293b")
    fig = go.Figure(go.Bar(
        x=[str(i) for i in range(len(count))], y=count,
        marker=dict(color=colors, line=dict(color='#0a0a0f', width=1)),
        text=count, textposition='outside',
        textfont=dict(size=10, color='#e2e8f0', family='Space Mono'),
    ))
    fig.update_layout(paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
                      font=dict(color='#e2e8f0'),
                      xaxis=dict(showgrid=False, title="Valeur"),
                      yaxis=dict(showgrid=True, gridcolor='#1e1e2e',
                                 title="Cumul" if phase in ("cumul","cumul_done") else "Occurrences"),
                      margin=dict(l=40,r=10,t=10,b=40), height=200, showlegend=False)
    return fig

def buckets_fig(buckets):
    palette = ["#7c3aed","#06b6d4","#10b981","#f59e0b","#ef4444",
               "#ec4899","#8b5cf6","#14b8a6","#84cc16","#f97316"]
    traces = []
    for d, bucket in enumerate(buckets):
        label = str(d)
        content = ", ".join(str(v) for v in bucket) if bucket else "vide"
        traces.append(go.Bar(
            x=[label], y=[max(len(bucket), 0.15)],
            marker=dict(color=palette[d], line=dict(color='#0a0a0f', width=1)),
            text=[content], textposition='inside',
            textfont=dict(size=9, color='white', family='Space Mono'),
            showlegend=False, name=f"seau {d}",
        ))
    fig = go.Figure(traces)
    fig.update_layout(paper_bgcolor='#0a0a0f', plot_bgcolor='#111118',
                      barmode='group', font=dict(color='#e2e8f0'),
                      xaxis=dict(showgrid=False, title="Seau (chiffre)"),
                      yaxis=dict(showgrid=True, gridcolor='#1e1e2e', title="Nb éléments"),
                      margin=dict(l=40,r=10,t=10,b=40), height=220, showlegend=False)
    return fig

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<span class="page-badge" style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);color:#fcd34d;">🪣 TRIS LINÉAIRES</span>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Counting Sort & Radix Sort</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Contrairement aux tris classiques (O(n log n)), ces algorithmes ne comparent <b>jamais deux éléments</b>. Ils exploitent la structure des données pour trier en <b>O(n)</b>. Counting compte les occurrences, Radix trie chiffre par chiffre.</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊  Counting Sort — O(n+k)", "🪣  Radix Sort — O(d×n)"])

# ── Counting Sort ─────────────────────────────────────────────────────────────
with tab1:
    col_ctrl, col_viz = st.columns([1, 3])
    with col_ctrl:
        st.markdown("#### ⚙️ Paramètres")
        n_cs    = st.slider("Taille", 6, 14, 8, key="cs_n")
        max_cs  = st.slider("Valeur max (k)", 5, 20, 9, key="cs_max")
        seed_cs = st.slider("Graine", 0, 99, 7, key="cs_seed")
        random.seed(seed_cs)
        arr_cs   = [random.randint(0, max_cs) for _ in range(n_cs)]
        steps_cs = counting_sort_steps(arr_cs, max_cs)
        st.markdown(f'<span class="complexity-badge">O(n+k) · n={n_cs}, k={max_cs+1}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{len(steps_cs)} étapes</span>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""
        <div class="info-box" style="border-left-color:#f59e0b; font-size:0.82rem;">
        <b>3 phases :</b><br><br>
        <b>1. Comptage</b> — count[v] = nb d'occurrences de v<br><br>
        <b>2. Cumul</b> — count[v] = nb d'éléments ≤ v<br>
        → donne la position finale de v<br><br>
        <b>3. Placement</b> — on place chaque élément à sa position, en parcourant à l'envers pour rester <b>stable</b>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("🟣 **Violet** = éléments du tableau")
        st.markdown("🟡 **Jaune** = élément/case actif")
        st.markdown("🔵 **Cyan** = cumul en cours")
        st.markdown("🟢 **Vert** = trié")
        st.markdown("*Glisse le slider pour avancer étape par étape*")
    with col_viz:
        si = st.slider("Étape", 0, len(steps_cs)-1, 0, key="cs_step")
        s  = steps_cs[si]
        st.markdown(f'<div class="info-box" style="border-left-color:#f59e0b;">{s["desc"]}</div>', unsafe_allow_html=True)
        arr_show = s["output"] if s["output"] and s["phase"] in ("place","done") else s["arr"]
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### 📥 Tableau")
            st.plotly_chart(bar_fig(arr_show, s["hl_arr"], s["phase"]),
                            use_container_width=True, key=f"cs_arr_{si}")
        with col_b:
            st.markdown("##### 🧮 Tableau de comptage")
            st.plotly_chart(count_fig(s["count"], s["hl_count"], s["phase"]),
                            use_container_width=True, key=f"cs_count_{si}")

# ── Radix Sort ────────────────────────────────────────────────────────────────
with tab2:
    col_ctrl2, col_viz2 = st.columns([1, 3])
    with col_ctrl2:
        st.markdown("#### ⚙️ Paramètres")
        n_rs    = st.slider("Taille", 6, 14, 8, key="rs_n")
        max_rs  = st.slider("Valeur max", 10, 999, 99, key="rs_max")
        seed_rs = st.slider("Graine", 0, 99, 12, key="rs_seed")
        random.seed(seed_rs)
        arr_rs   = [random.randint(1, max_rs) for _ in range(n_rs)]
        steps_rs = radix_sort_steps(arr_rs)
        n_passes = len(str(max_rs))
        st.markdown(f'<span class="complexity-badge">O(d×n) · d={n_passes} passe(s)</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="complexity-badge" style="margin-top:6px;display:inline-block;">{len(steps_rs)} étapes</span>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""
        <div class="info-box" style="border-left-color:#06b6d4; font-size:0.82rem;">
        <b>Idée :</b> trier chiffre par chiffre,<br>du moins significatif au plus significatif.<br><br>
        Pour chaque passe :<br>
        1. Répartir dans <b>10 seaux</b> (0–9) selon le chiffre courant<br>
        2. Recollectionner les seaux dans l'ordre<br><br>
        Chaque passe utilise un tri <b>stable</b> → l'ordre des passes précédentes est préservé.
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("🎨 **10 couleurs** = 10 seaux (0–9)")
        st.markdown("🟢 **Vert** = trié définitivement")
        st.markdown("*Glisse le slider pour voir chaque passe*")
    with col_viz2:
        si2 = st.slider("Étape", 0, len(steps_rs)-1, 0, key="rs_step")
        s2  = steps_rs[si2]
        st.markdown(f'<div class="info-box" style="border-left-color:#06b6d4;">{s2["desc"]}</div>', unsafe_allow_html=True)
        st.markdown("##### 📥 Tableau courant")
        hl_rs = list(range(len(s2["arr"]))) if s2["phase"] == "done" else []
        st.plotly_chart(bar_fig(s2["arr"], hl_rs, s2["phase"]),
                        use_container_width=True, key=f"rs_arr_{si2}")
        if s2.get("buckets"):
            st.markdown(f"##### 🪣 Seaux — chiffre des {s2['digit_name']}")
            st.plotly_chart(buckets_fig(s2["buckets"]),
                            use_container_width=True, key=f"rs_buckets_{si2}")
