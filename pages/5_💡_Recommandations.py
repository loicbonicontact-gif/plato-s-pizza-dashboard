# ============================================
# Page : recommandations, limites et méthodologie
# ============================================

import streamlit as st

st.set_page_config(page_title="Recommandations", page_icon="💡")

st.title("💡 Ce qu'on en retient")
st.markdown("""
- **Jours chargés** : jeudi, vendredi et samedi concentrent le plus de commandes → prévoir plus de personnel ces jours-là.
- **Taille qui marche** : la taille L est largement la plus vendue → la mettre en avant dans la communication.
- **Pizzas à surveiller** : certaines pizzas (comme la Brie Carre) se vendent très peu → se poser la question de les retirer de la carte.
- **Panier moyen** : environ 2 pizzas par commande → voir si on peut vendre autre chose à côté (boisson, dessert) pour le faire monter.
""")

st.subheader("⚠️ Limites de l'analyse")
st.markdown("""
- On n'a qu'une seule année de données (2015), donc impossible de savoir si c'est pareil chaque année.
- Il n'y a que des pizzas dans les données, pas de boissons ni de desserts.
- On n'a aucune info sur les clients eux-mêmes (qui ils sont, où ils habitent).
""")

st.divider()

with st.expander("🔧 Méthodologie (comment ce tableau de bord a été construit)"):
    st.markdown("""
    **1. Base de données (SQL)**
    Les 4 fichiers CSV fournis (`orders`, `order_details`, `pizzas`, `pizza_types`) ont été chargés dans une
    base SQLite (`pizza.db`), avec 4 tables reliées par des clés primaires/étrangères (voir `create_db.ipynb`).
    Un contrôle qualité (valeurs manquantes, doublons, types, dates) a été fait avant l'insertion.

    **2. Analyse (SQL + Python)**
    Toutes les requêtes de cette application utilisent des **jointures SQL** entre `order_details`, `pizzas`,
    `pizza_types` et `orders` pour calculer le chiffre d'affaires (`quantité × prix`), car la base ne
    contient pas de colonne "total" toute faite. Le détail des requêtes et leurs résultats bruts sont
    dans `analysis.ipynb`.

    **3. Application (Streamlit)**
    Cette application relit `pizza.db` (jamais les CSV directement) via `pandas.read_sql()`, et les graphiques
    sont faits avec `matplotlib`. Les filtres (catégorie, taille) changent la condition `WHERE` des
    requêtes SQL, donc tous les chiffres et graphiques se recalculent en direct. L'application est
    découpée en plusieurs pages (dossier `pages/`) pour faciliter la navigation pendant la présentation.
    """)

st.caption("Projet Data Analyst — Plato's Pizza · SQL (SQLite) · Python (pandas) · Streamlit")
