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
st.markdown("""
**Pourquoi regarder ça ?** Toutes les pizzas ne se valent pas : certaines rapportent beaucoup plus
que d'autres. Savoir lesquelles permet de décider quoi mettre en avant (menu, pub) et quoi, à
l'inverse, retirer de la carte si ça ne se vend presque pas.
""")

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

st.subheader("🔎 Analyse")

if not df_top.empty:
    meilleure_pizza = df_top.iloc[0]
    st.markdown(f"""
    - **{meilleure_pizza['pizza_name']}** est la pizza qui rapporte le plus, avec **{meilleure_pizza['ca']:,.2f} €**
      de chiffre d'affaires.
    - On remarque que les pizzas en tête de ce classement sont surtout de la catégorie *Chicken* — ce sont des
      pizzas vendues un peu plus cher, donc chaque vente rapporte plus, même sans être forcément les plus
      commandées en quantité.
    """)

# Requête séparée : les pizzas qui se vendent le moins (flop), utile pour la même page
requete_flop = f"""
SELECT pt.name AS pizza_name, SUM(od.quantity * p.price) AS ca
FROM order_details od
JOIN pizzas p ON od.pizza_id = p.pizza_id
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
WHERE {condition_categorie} AND {condition_taille}
GROUP BY pt.name
ORDER BY ca ASC
LIMIT 5
"""
df_flop = pd.read_sql(requete_flop, conn)

if not df_flop.empty:
    pire_pizza = df_flop.iloc[0]
    st.markdown(f"""
    - À l'inverse, **{pire_pizza['pizza_name']}** est la pizza qui rapporte le moins (**{pire_pizza['ca']:,.2f} €**).
      C'est une pizza à surveiller : vaut-il la peine de la garder au menu ?
    """)

    with st.expander("Voir les 5 pizzas qui se vendent le moins"):
        st.dataframe(df_flop.rename(columns={"pizza_name": "Pizza", "ca": "CA (€)"}), hide_index=True)
