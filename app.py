# ============================================
# Application Streamlit - Plato's Pizza
# Page d'accueil
# ============================================
# But : afficher les chiffres de vente dans une page web,
# en allant les chercher dans pizza.db (jamais dans les CSV directement).
# Les autres pages sont dans le dossier pages/.

import streamlit as st
import pandas as pd
from utils import get_connection, get_filtres

st.set_page_config(page_title="Plato's Pizza — Accueil", page_icon="🍕")

conn = get_connection()

# --- Titre et introduction ---
st.title("🍕 Plato's Pizza — Tableau de bord")
st.markdown("""
Ce tableau de bord répond à une question simple : **comment se portent les ventes de Plato's Pizza, et sur quoi faut-il agir ?**

Les chiffres viennent des commandes de l'année **2015** (21 350 commandes, 48 620 pizzas vendues).
Utilise le menu à gauche pour naviguer entre les pages, et les filtres pour te concentrer sur une
catégorie ou une taille de pizza en particulier (les filtres s'appliquent sur toutes les pages).
""")

with st.expander("🎯 Les questions auxquelles répond ce tableau de bord"):
    st.markdown("""
    1. **Combien l'entreprise a-t-elle gagné, et est-ce stable sur l'année ?** → page "Évolution du CA".
    2. **Quelles pizzas rapportent le plus (et le moins) ?** → page "Top pizzas".
    3. **Quelle catégorie de pizza pèse le plus dans les ventes ?** → page "Catégories".
    4. **Quand faut-il prévoir le plus de monde en cuisine/livraison ?** → page "Activité".
    5. **Combien dépense un client en moyenne par commande ?** → chiffres clés ci-dessous.

    Ces questions ont été choisies parce que ce sont celles qu'une direction de pizzeria se pose pour
    décider où mettre ses efforts (quelles pizzas pousser, quand renforcer l'équipe).
    """)

st.divider()

# --- Filtres (dans la barre latérale, partagés par toutes les pages) ---
condition_categorie, condition_taille = get_filtres(conn)

# --- Indicateurs clés ---
requete_kpi = f"""
SELECT
    SUM(od.quantity * p.price) AS ca_total,
    COUNT(DISTINCT od.order_id) AS nb_commandes
FROM order_details od
JOIN pizzas p ON od.pizza_id = p.pizza_id
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
WHERE {condition_categorie} AND {condition_taille}
"""
kpi = pd.read_sql(requete_kpi, conn)
ca_total = kpi["ca_total"][0] if kpi["ca_total"][0] is not None else 0
nb_commandes = kpi["nb_commandes"][0] if kpi["nb_commandes"][0] is not None else 0
panier_moyen = ca_total / nb_commandes if nb_commandes else 0

st.subheader("📊 Les chiffres clés")
col1, col2, col3 = st.columns(3)
col1.metric("Chiffre d'affaires", f"{ca_total:,.2f} €")
col2.metric("Nombre de commandes", f"{nb_commandes}")
col3.metric("Panier moyen", f"{panier_moyen:,.2f} €")
st.caption("Le panier moyen correspond à peu près à 2 pizzas par commande.")

st.caption("Projet Data Analyst — Plato's Pizza · SQL (SQLite) · Python (pandas) · Streamlit")
