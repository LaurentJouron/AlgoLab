# ⚡ Graphix — Visualisateur d'Algorithmes

Application de démonstration professionnelle des algorithmes classiques, construite avec **Python** et **Streamlit**.

## 🚀 Installation & Lancement

### 1. Prérequis
- Python 3.12+
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
graphix/
├── Accueil.py              ← Page d'accueil (navigation principale)
├── requirements.txt
├── .gitignore
├── assets/
│   └── style.css           ← CSS global partagé
├── utils/
│   └── styles.py           ← Lecture et injection du CSS
└── pages/
    ├── 1_Tri.py            ← Tri à bulles, Tri fusion, Tri rapide
    ├── 2_Hanoi.py          ← Tours de Hanoï
    ├── 3_SacADos.py        ← Sac à dos 0/1 (Programmation Dynamique)
    ├── 4_Graphes.py        ← Dijkstra, BFS, DFS
    ├── 5_RechercheB.py     ← Recherche Binaire
    ├── 6_NReines.py        ← N-Reines (Backtracking)
    ├── 7_Conway.py         ← Jeu de la Vie de Conway
    └── 8_Labyrinthe.py     ← Génération DFS + Résolution BFS
```

---

## 🧩 Algorithmes inclus

| Page | Algorithmes | Complexité |
|------|-------------|------------|
| 📊 Tri | Tri à bulles, Tri fusion, Tri rapide | O(n²) → O(n log n) |
| 🗼 Hanoï | Tours de Hanoï récursif | O(2ⁿ) |
| 🎒 Sac à dos | Knapsack 0/1 — Programmation Dynamique | O(n × W) |
| 🕸️ Graphes | Dijkstra, BFS, DFS | O((V+E) log V) |
| 🔍 Recherche Binaire | Recherche dans tableau trié | O(log n) |
| ♛ N-Reines | Backtracking sur échiquier N×N | O(N!) |
| 🧬 Jeu de la Vie | Automate cellulaire de Conway | O(n×m) |
| 🌀 Labyrinthe | Génération DFS + Résolution BFS | O(n×m) |

---

## 🌐 Déploiement sur Streamlit Cloud

```bash
# 1. Créer le dépôt GitHub "graphix"
git init
git add .
git commit -m "Initial commit — Graphix"
git remote add origin https://github.com/TON_USERNAME/graphix.git
git branch -M main
git push -u origin main
```

Puis sur [share.streamlit.io](https://share.streamlit.io) :
- Repository : `TON_USERNAME/graphix`
- Branch : `main`
- Main file : `Accueil.py`

---

*Construit avec Python & Streamlit*
