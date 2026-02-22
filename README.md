# 🌲 Graphix — Visualisateur d'Algorithmes

Application de démonstration professionnelle des algorithmes classiques, construite avec **Python** et **Streamlit**. Chaque algorithme est visualisé étape par étape avec animations interactives.

🚀 **Live** : [graphix.streamlit.app](https://graphix.streamlit.app)

---

## 🛠️ Installation & Lancement

### Prérequis
- Python 3.12+
- pip

### Installer les dépendances
```bash
pip install -r requirements.txt
```

### Lancer l'application
```bash
streamlit run Accueil.py
```

L'application s'ouvre automatiquement à `http://localhost:8501`

---

## 📂 Structure du projet

```
graphix/
├── Accueil.py               ← Page d'accueil (navigation)
├── requirements.txt
├── assets/
│   ├── style.css            ← CSS global
│   └── favicon.ico          ← Logo ikigai 生き甲斐
├── utils/
│   └── styles.py            ← Injection CSS + sidebar navigation
└── pages/
    ├── 0_Dashboard.py       ← Benchmark temps réels
    ├── 1_Tri.py             ← Tri à bulles, fusion, rapide
    ├── 2_Hanoi.py           ← Tours de Hanoï (récursif)
    ├── 3_SacADos.py         ← Sac à dos 0/1 (DP)
    ├── 4_Graphes.py         ← Dijkstra, BFS, DFS
    ├── 5_RechercheB.py      ← Recherche binaire
    ├── 6_NReines.py         ← N-Reines (backtracking)
    ├── 7_Conway.py          ← Jeu de la Vie de Conway
    ├── 8_Labyrinthe.py      ← Génération DFS + Résolution BFS
    ├── 9_ArbresBinaires.py  ← Arbres binaires de recherche
    ├── 10_Huffman.py        ← Compression de Huffman
    ├── 11_Chiffrement.py    ← Chiffrement César & RSA
    ├── 12_AStar.py          ← Algorithme A*
    ├── 13_Quiz.py           ← Quiz algorithmique
    ├── 14_HeapSort.py       ← Tri par tas (Heap Sort)
    ├── 15_Kruskal.py        ← Kruskal & Prim (ACM)
    ├── 16_Fibonacci.py      ← Fibonacci : récursif / mémo / itératif
    ├── 17_TriExternes.py    ← Counting Sort & Radix Sort
    ├── 18_Levenshtein.py    ← Distance de Levenshtein
    ├── 19_MonteCarlo.py     ← Estimation de π par Monte Carlo
    └── 20_PageRank.py       ← PageRank (algorithme Google)
```

---

## 🧩 Algorithmes inclus (v3.0)

### 📊 Tri & Recherche
| Page | Algorithmes | Complexité |
|------|-------------|------------|
| 📊 Tri | Tri à bulles, Tri fusion, Tri rapide | O(n²) → O(n log n) |
| 🔍 Recherche Binaire | Recherche dans tableau trié | O(log n) |
| 🌲 Heap Sort | Tri par tas avec vue arbre binaire | O(n log n) garanti |
| 🪣 Counting & Radix | Tris sans comparaison | O(n+k) / O(d×n) |

### 🔄 Récursivité & Programmation Dynamique
| Page | Algorithmes | Complexité |
|------|-------------|------------|
| 🗼 Hanoï | Tours de Hanoï récursif | O(2ⁿ) |
| 🎒 Sac à dos | Knapsack 0/1 — DP | O(n × W) |
| 🌀 Fibonacci | Récursif / Mémoïsation / Itératif | O(2ⁿ) → O(n) |
| ✏️ Levenshtein | Distance d'édition entre chaînes | O(m×n) |

### 🕸️ Graphes & Chemins
| Page | Algorithmes | Complexité |
|------|-------------|------------|
| 🕸️ Graphes | Dijkstra, BFS, DFS | O((V+E) log V) |
| 🌀 Labyrinthe | Génération DFS + Résolution BFS | O(n×m) |
| ⭐ A* | Pathfinding heuristique (Manhattan) | O((V+E) log V) |
| 🌉 Kruskal & Prim | Arbre couvrant minimal | O(E log E) |
| 🌐 PageRank | Algorithme original de Google (1998) | O(k·(V+E)) |

### 🧬 Automates & Structures
| Page | Algorithmes | Complexité |
|------|-------------|------------|
| ♛ N-Reines | Backtracking sur échiquier | O(N!) |
| 🧬 Jeu de la Vie | Automate cellulaire de Conway | O(n×m) |
| 🌳 Arbres Binaires | Insertion, recherche, parcours | O(log n) moy. |

### 🔐 Compression & Cryptographie
| Page | Algorithmes | Complexité |
|------|-------------|------------|
| 📦 Huffman | Compression sans perte | O(n log n) |
| 🔐 Chiffrement | César (symétrique) + RSA (asymétrique) | — |

### 🎲 Probabilités
| Page | Algorithmes | Complexité |
|------|-------------|------------|
| 🎲 Monte Carlo | Estimation de π par simulation | O(n) |

### 🛠️ Outils
| Page | Description |
|------|-------------|
| 📈 Dashboard | Benchmark temps réels sur votre machine |
| 🎓 Quiz | 16 questions sur tous les algorithmes |

---

## 🌐 Déploiement sur Streamlit Cloud

```bash
git add .
git commit -m "v3.0 — 19 pages, 30+ algorithmes"
git push
```

Sur [share.streamlit.io](https://share.streamlit.io) :
- **Repository** : `LaurentJouron/graphix`
- **Branch** : `main`
- **Main file** : `Accueil.py`

---

## 🎨 Design

- **Thème** : dark mode personnalisé (fond `#0a0a0f`)
- **Police** : DM Sans + Space Mono (monospace)
- **Logo** : ikigai 生き甲斐 (favicon.ico rouge)
- **CSS** : `assets/style.css` partagé via `utils/styles.py`

---

*Graphix v3.0 — Construit avec Python & Streamlit*
