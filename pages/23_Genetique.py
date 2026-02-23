import streamlit as st
import plotly.graph_objects as go
import random, math, sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, sidebar_nav

st.set_page_config(
    page_title="Algorithme Génétique — Graphix", page_icon="🧬", layout="wide"
)
inject_css()
sidebar_nav()


# ── Problème : trouver le maximum de f(x) sur [0, 2π] ────────────────────────
def fitness(x):
    return math.sin(x) * math.cos(0.5 * x) + 0.5 * math.sin(3 * x)


def genetic_steps(pop_size=20, n_gen=40, mutation_rate=0.15, seed=42):
    rng = random.Random(seed)
    population = [rng.uniform(0, 2 * math.pi) for _ in range(pop_size)]
    steps = []

    def record(gen, pop, op=""):
        fits = [fitness(x) for x in pop]
        best = max(range(len(pop)), key=lambda i: fits[i])
        steps.append(
            {
                "gen": gen,
                "pop": list(pop),
                "fits": list(fits),
                "best_x": pop[best],
                "best_f": fits[best],
                "mean_f": sum(fits) / len(fits),
                "op": op,
                "desc": f"Génération {gen} — meilleur f(x)=<b>{fits[best]:.4f}</b> à x=<b>{pop[best]:.4f}</b>"
                + (f" — {op}" if op else ""),
            }
        )

    record(0, population, "Population initiale aléatoire")

    for gen in range(1, n_gen + 1):
        fits = [fitness(x) for x in population]
        min_f = min(fits)
        shifted = [f - min_f + 1e-9 for f in fits]
        total = sum(shifted)

        # Sélection par roulette
        def pick():
            r, acc = rng.random() * total, 0
            for i, s in enumerate(shifted):
                acc += s
                if acc >= r:
                    return population[i]
            return population[-1]

        new_pop = []
        for _ in range(pop_size):
            p1, p2 = pick(), pick()
            # Croisement
            alpha = rng.random()
            child = alpha * p1 + (1 - alpha) * p2
            # Mutation
            if rng.random() < mutation_rate:
                child += rng.gauss(0, 0.3)
            child = max(0, min(2 * math.pi, child))
            new_pop.append(child)

        population = new_pop
        op = "Sélection + Croisement + Mutation" if gen % 5 == 0 else ""
        record(gen, population, op)

    return steps


# ── Figure population ─────────────────────────────────────────────────────────
def make_gen_fig(step):
    xs = [i * 0.02 for i in range(315)]
    ys = [fitness(x) for x in xs]

    fig = go.Figure()
    # Courbe de la fonction
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            line=dict(color="#334155", width=2),
            name="f(x)",
            showlegend=True,
        )
    )
    # Population
    pop_y = [fitness(x) for x in step["pop"]]
    fig.add_trace(
        go.Scatter(
            x=step["pop"],
            y=pop_y,
            mode="markers",
            marker=dict(
                size=9,
                color=pop_y,
                colorscale=[[0, "#1e3a5f"], [0.5, "#7c3aed"], [1, "#f59e0b"]],
                line=dict(color="#0a0a0f", width=1),
                showscale=True,
                colorbar=dict(
                    title=dict(
                        text="Fitness", font=dict(color="#94a3b8", size=10)
                    ),
                    tickfont=dict(color="#94a3b8", size=9),
                    len=0.6,
                ),
            ),
            name="Individus",
            showlegend=True,
        )
    )
    # Meilleur individu
    fig.add_trace(
        go.Scatter(
            x=[step["best_x"]],
            y=[step["best_f"]],
            mode="markers",
            marker=dict(
                size=16,
                color="#10b981",
                symbol="star",
                line=dict(color="#0a0a0f", width=1.5),
            ),
            name=f"Meilleur (x={step['best_x']:.3f})",
            showlegend=True,
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        font=dict(color="#e2e8f0", family="DM Sans"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1e1e2e",
            title="x",
            range=[0, 2 * math.pi],
        ),
        yaxis=dict(showgrid=True, gridcolor="#1e1e2e", title="f(x)"),
        legend=dict(
            bgcolor="#111118", bordercolor="#1e1e2e", font=dict(size=10)
        ),
        margin=dict(l=50, r=60, t=30, b=50),
        height=380,
        title=dict(
            text=f"Génération {step['gen']} — {len(step['pop'])} individus",
            font=dict(color="#94a3b8", size=12),
            x=0.5,
        ),
    )
    return fig


def make_convergence_fig(steps):
    gens = [s["gen"] for s in steps]
    bests = [s["best_f"] for s in steps]
    means = [s["mean_f"] for s in steps]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=gens,
            y=means,
            mode="lines",
            name="Fitness moyenne",
            line=dict(color="#7c3aed", width=1.5, dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=gens,
            y=bests,
            mode="lines",
            name="Meilleur individu",
            line=dict(color="#10b981", width=2),
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#111118",
        font=dict(color="#e2e8f0", family="DM Sans"),
        xaxis=dict(showgrid=True, gridcolor="#1e1e2e", title="Génération"),
        yaxis=dict(showgrid=True, gridcolor="#1e1e2e", title="Fitness"),
        legend=dict(
            bgcolor="#111118", bordercolor="#1e1e2e", font=dict(size=10)
        ),
        margin=dict(l=50, r=20, t=10, b=50),
        height=220,
    )
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(
    '<span class="page-badge" style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#6ee7b7;">🧬 ALGORITHME GÉNÉTIQUE</span>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-title">Algorithme Génétique</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="page-desc">Trouver le maximum d\'une fonction complexe en <b>évoluant une population</b> de solutions. Chaque génération : sélection des meilleurs, croisement pour combiner leurs gènes, mutation pour explorer de nouveaux territoires. Inspiré de la sélection naturelle de Darwin.</div>',
    unsafe_allow_html=True,
)

col_ctrl, col_viz = st.columns([1, 3])

with col_ctrl:
    st.markdown("#### ⚙️ Paramètres")
    pop_size = st.slider("Taille population", 10, 60, 20, key="ga_pop")
    n_gen = st.slider("Nombre de générations", 10, 80, 40, key="ga_gen")
    mut_rate = st.slider(
        "Taux de mutation", 0.01, 0.5, 0.15, step=0.01, key="ga_mut"
    )
    seed_ga = st.slider("Graine", 0, 99, 42, key="ga_seed")

    steps_ga = genetic_steps(pop_size, n_gen, mut_rate, seed_ga)
    best = steps_ga[-1]

    st.metric("Meilleur f(x) final", f"{best['best_f']:.5f}")
    st.metric("Meilleur x", f"{best['best_x']:.5f}")
    st.markdown(
        f'<span class="complexity-badge">O(G × P) · {n_gen} générations</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        """
    <div class="info-box" style="border-left-color:#10b981; font-size:0.82rem;">
    <b>3 opérateurs génétiques :</b><br><br>
    🎯 <b>Sélection</b> (roulette)<br>
    Les individus avec la meilleure fitness ont plus de chances d'être choisis comme parents.<br><br>
    🔀 <b>Croisement</b><br>
    Deux parents génèrent un enfant par combinaison linéaire : α·p1 + (1-α)·p2<br><br>
    🎲 <b>Mutation</b><br>
    Avec probabilité {mut:.0%}, ajouter un bruit gaussien σ=0.3 pour explorer de nouvelles zones.
    </div>""".format(
            mut=mut_rate
        ),
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("⭐ **Étoile verte** = meilleur individu")
    st.markdown("🟡 **Jaune** = fitness élevée")
    st.markdown("🔵 **Bleu foncé** = fitness faible")
    st.markdown("*Glisse pour voir l'évolution génération par génération*")

with col_viz:
    step_idx = st.slider("Génération", 0, len(steps_ga) - 1, 0, key="ga_step")
    s = steps_ga[step_idx]
    st.markdown(
        f'<div class="info-box" style="border-left-color:#10b981;">{s["desc"]}</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        make_gen_fig(s),
        use_container_width=True,
        key=f"ga_pop_{step_idx}_{seed_ga}_{pop_size}",
    )
    st.markdown("##### 📈 Convergence de la population")
    st.plotly_chart(
        make_convergence_fig(steps_ga[: step_idx + 1]),
        use_container_width=True,
        key=f"ga_conv_{step_idx}_{seed_ga}",
    )
