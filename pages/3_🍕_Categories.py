# ============================================
# Page : répartition par catégorie
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import get_connection, get_filtres

st.set_page_config(page_title="Catégories", page_icon="🍕")

conn = get_connection()
condition_categorie, condition_taille = get_filtres(conn)

st.title("🍕 Répartition du chiffre d'affaires par catégorie")
st.write("Permet de voir si une catégorie de pizza domine largement les ventes, ou si c'est plutôt équilibré entre les 4 catégories.")

requete_categorie = f"""
SELECT pt.category AS categorie, SUM(od.quantity * p.price) AS ca
FROM order_details od
JOIN pizzas p ON od.pizza_id = p.pizza_id
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
WHERE {condition_categorie} AND {condition_taille}
GROUP BY pt.category
ORDER BY ca DESC
"""
df_categorie = pd.read_sql(requete_categorie, conn)

fig, ax = plt.subplots()
ax.pie(df_categorie["ca"], labels=df_categorie["categorie"], autopct="%1.1f%%")
st.pyplot(fig)

if not df_categorie.empty:
    categorie_top = df_categorie.iloc[0]
    part = categorie_top["ca"] / df_categorie["ca"].sum() * 100
    st.info(f"La catégorie **{categorie_top['categorie']}** est en tête avec **{part:.1f}%** du chiffre d'affaires affiché.")
