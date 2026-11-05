# ============================================
# Page : top pizzas par chiffre d'affaires
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import get_connection, get_filtres

st.set_page_config(page_title="Top Pizzas", page_icon="🏆")

conn = get_connection()
condition_categorie, condition_taille = get_filtres(conn)

st.title("🏆 Top 10 des pizzas par chiffre d'affaires")
st.write("Les pizzas qui rapportent le plus — celles à mettre en avant dans la communication ou à ne surtout pas retirer de la carte.")

requete_top = f"""
SELECT pt.name AS pizza_name, SUM(od.quantity * p.price) AS ca
FROM order_details od
JOIN pizzas p ON od.pizza_id = p.pizza_id
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
WHERE {condition_categorie} AND {condition_taille}
GROUP BY pt.name
ORDER BY ca DESC
LIMIT 10
"""
df_top = pd.read_sql(requete_top, conn)

fig, ax = plt.subplots()
ax.barh(df_top["pizza_name"], df_top["ca"])
ax.invert_yaxis()
ax.set_xlabel("CA (€)")
st.pyplot(fig)

if not df_top.empty:
    meilleure_pizza = df_top.iloc[0]
    st.info(f"**{meilleure_pizza['pizza_name']}** est la pizza qui rapporte le plus, avec **{meilleure_pizza['ca']:,.2f} €** de chiffre d'affaires.")
