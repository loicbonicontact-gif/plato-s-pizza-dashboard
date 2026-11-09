# Plato's Pizza — Analyse de l'activité

Projet Data Analyst (SQL · Python · Streamlit) autour des données de ventes de la pizzeria **Plato's Pizza**.
L'objectif : construire une base de données SQL, l'analyser, et rendre les résultats accessibles dans une
application Streamlit interactive pour la direction.

## Contenu du dépôt

- `data/` — fichiers CSV sources (`orders`, `order_details`, `pizzas`, `pizza_types`)
- `create_db.ipynb` — notebook qui crée la base SQLite `pizza.db` à partir des CSV (contrôle qualité inclus)
- `analysis.ipynb` — requêtes SQL d'analyse, interprétations et graphiques
- `app.py` — page d'accueil de l'application Streamlit
- `utils.py` — fonctions partagées par toutes les pages (connexion à la base, filtres catégorie/taille/période, jointures communes)
- `pages/` — les autres pages de l'application Streamlit (une page par thème d'analyse)
- `pizza.db` — base de données générée (non versionnée, voir ci-dessous comment la recréer)

## Installation

1. Avoir Python installé (3.9 ou plus récent).
2. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```

## Préparer la base de données

La base `pizza.db` n'est pas incluse dans le dépôt (elle est recréée à partir des CSV).

1. Ouvrir le notebook `create_db.ipynb` (par exemple avec Jupyter ou VS Code).
2. Exécuter toutes les cellules dans l'ordre.
3. Un fichier `pizza.db` est créé à la racine du projet.

## Lancer l'application

Une fois `pizza.db` créé, lancer dans un terminal, depuis le dossier du projet :

```
streamlit run app.py
```

L'application s'ouvre dans le navigateur. Un menu à gauche permet de naviguer entre les différentes pages
(évolution du chiffre d'affaires, top pizzas, catégories, activité par jour, recommandations), et des filtres
(catégorie, taille) permettent d'affiner les résultats sur chaque page.

## Principaux constats et recommandations

- En 2015, Plato's Pizza a réalisé **817 860 € de chiffre d'affaires** sur 21 350 commandes, soit un panier
  moyen d'environ **38 €** (un peu plus de 2 pizzas par commande).
- Les jours les plus chargés sont **jeudi, vendredi et samedi**, avec deux pics dans la journée : **12h-13h**
  et **17h-19h**.
- La taille **L** est largement la plus vendue (près de la moitié du chiffre d'affaires).
- Les 4 catégories de pizzas (Classic, Supreme, Chicken, Veggie) se vendent de façon assez équilibrée.
- **The Thai Chicken Pizza** et **The Barbecue Chicken Pizza** rapportent le plus ; **The Brie Carre Pizza**
  est nettement la moins vendue.

**Recommandations :**
- Renforcer les équipes en cuisine/livraison sur les jours et créneaux les plus chargés.
- Mettre en avant la taille L et les pizzas de la catégorie Chicken dans la communication.
- Reconsidérer la place de The Brie Carre Pizza et des tailles XL/XXL sur la carte (ventes très faibles).
- Étudier l'ajout de produits complémentaires (boissons, desserts) pour faire progresser le panier moyen.

## Limites

- Les données ne couvrent qu'une seule année (2015) : impossible de savoir si ces résultats se répètent
  d'une année sur l'autre.
- Le jeu de données ne contient que des pizzas, pas de boissons ni de desserts.
- Aucune information sur les clients (profil, localisation) n'est disponible, ce qui limite l'analyse à
  l'échelle des commandes et des produits.
