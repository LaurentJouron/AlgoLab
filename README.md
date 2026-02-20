# ⚡ Graphix — Visualisateur d'Algorithmes

Application de démonstration professionnelle des algorithmes classiques, construite avec **Python** et **Streamlit**.

## 🚀 Installation & Lancement

### 1. Prérequis
- Python 3.9+
- pip

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
streamlit run Accueil.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`

---

## 📂 Structure du projet

```
algo_app/
├── Accueil.py              ← Page d'accueil (navigation principale)
├── requirements.txt
├── utils/
│   └── styles.py           ← CSS global partagé
├── assets/
│   └── style.css           ← fichier de style CSS
└── pages/
    ├── 1_Tri.py            ← Tri à bulles, Tri fusion, Tri rapide
    ├── 2_Hanoi.py          ← Tours de Hanoï
    ├── 3_SacADos.py        ← Sac à dos 0/1 (Programmation Dynamique)
    └── 4_Graphes.py        ← Dijkstra, BFS, DFS
```

---

## 🧩 Algorithmes inclus

| Page | Algorithmes | Complexité |
|------|-------------|------------|
| 📊 Tri | Tri à bulles, Tri fusion, Tri rapide | O(n²) → O(n log n) |
| 🗼 Hanoï | Tours de Hanoï récursif | O(2ⁿ) |
| 🎒 Sac à dos | Knapsack 0/1 — Programmation Dynamique | O(n × W) |
| 🕸️ Graphes | Dijkstra, BFS, DFS | O((V+E) log V) |

---

## ✨ Fonctionnalités

- **Animation étape par étape** avec contrôle de vitesse (Lente / Normale / Rapide)
- **Navigation manuelle** (bouton Étape suivante / précédente)
- **Paramètres interactifs** (taille des données, objets, capacité, nœuds...)
- **Visualisations Plotly** interactives et colorées
- **Table DP** animée pour le Sac à dos
- **Reconstruction du chemin** optimal pour Dijkstra
- Interface sombre et professionnelle

---

*Construit avec Python & Streamlit*
