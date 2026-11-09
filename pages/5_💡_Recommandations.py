# ============================================
# Page : recommandations, limites et méthodologie
# ============================================

import streamlit as st

st.set_page_config(page_title="Recommandations", page_icon="💡", layout="wide")

st.title("💡 Ce qu'on en retient")
st.caption("Conclusions calculées sur toute l'année 2015, sans filtre (voir les autres pages pour explorer avec les filtres).")
st.markdown("""
- **Jours chargés** : jeudi, vendredi et samedi concentrent le plus de commandes → prévoir plus de personnel ces jours-là.
- **Heures chargées** : deux pics, le midi (12h-13h) et le soir (17h-19h) → renforcer cuisine et livraison sur ces créneaux.
- **Taille qui marche** : la taille L est largement la plus vendue → la mettre en avant (menus, promotions).
- **Tailles à questionner** : XL et XXL se vendent presque jamais (552 et 28 pizzas sur l'année) → se demander si elles méritent leur place sur la carte.
- **Pizzas à pousser** : The Thai Chicken et The Barbecue Chicken rapportent le plus (catégorie Chicken, prix plus élevé).
- **Pizzas à surveiller** : The Brie Carre se vend très peu (490 unités) → se poser la question de la retirer de la carte.
- **Panier moyen** : environ 2 pizzas par commande (38,31 €) → voir si on peut vendre autre chose à côté (boisson, dessert) pour le faire monter.
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
    interactifs sont faits avec `plotly`. Les filtres (catégorie, taille, période) changent la condition `WHERE` des
    requêtes SQL, donc tous les chiffres et graphiques se recalculent en direct. L'application est
    découpée en plusieurs pages (dossier `pages/`) pour faciliter la navigation pendant la présentation.
    """)

st.caption("Projet Data Analyst — Plato's Pizza · SQL (SQLite) · Python (pandas) · Streamlit")
