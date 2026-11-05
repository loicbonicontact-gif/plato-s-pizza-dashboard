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

st.title("🍕 Répartition du chiffre d'affaires par catégorie et par taille")
st.markdown("""
**Pourquoi regarder ça ?** Plato's Pizza propose 4 catégories (Classic, Supreme, Chicken, Veggie) et
5 tailles (S, M, L, XL, XXL). Savoir lesquelles pèsent vraiment dans les ventes permet de simplifier
la carte si certaines options sont presque jamais choisies.
""")

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

st.subheader("Par catégorie")
fig, ax = plt.subplots()
ax.pie(df_categorie["ca"], labels=df_categorie["categorie"], autopct="%1.1f%%")
st.pyplot(fig)

if not df_categorie.empty:
    categorie_top = df_categorie.iloc[0]
    categorie_bas = df_categorie.iloc[-1]
    part = categorie_top["ca"] / df_categorie["ca"].sum() * 100
    ecart = df_categorie["ca"].max() - df_categorie["ca"].min()
    st.markdown(f"""
    - La catégorie **{categorie_top['categorie']}** est en tête avec **{part:.1f}%** du chiffre d'affaires affiché.
    - La catégorie la plus faible est **{categorie_bas['categorie']}**, mais l'écart avec les autres reste modéré
      (environ **{ecart:,.0f} €** entre la première et la dernière catégorie).
    - **Ce que ça veut dire :** le portefeuille de produits est équilibré, aucune catégorie n'est négligeable.
      Pas besoin de tout miser sur une seule famille de pizzas.
    """)

st.divider()
st.subheader("Par taille")

requete_taille = f"""
SELECT p.size AS taille, SUM(od.quantity * p.price) AS ca
FROM order_details od
JOIN pizzas p ON od.pizza_id = p.pizza_id
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
WHERE {condition_categorie} AND {condition_taille}
GROUP BY p.size
ORDER BY ca DESC
"""
df_taille = pd.read_sql(requete_taille, conn)

fig2, ax2 = plt.subplots()
ax2.bar(df_taille["taille"], df_taille["ca"])
ax2.set_xlabel("Taille")
ax2.set_ylabel("CA (€)")
st.pyplot(fig2)

if not df_taille.empty:
    taille_top = df_taille.iloc[0]
    part_taille = taille_top["ca"] / df_taille["ca"].sum() * 100
    st.markdown(f"""
    - La taille **{taille_top['taille']}** domine très largement, avec **{part_taille:.1f}%** du chiffre d'affaires.
    - Les tailles XL et XXL sont quasi anecdotiques : elles existent dans le catalogue mais ne sont presque
      jamais commandées.
    - **Ce que ça veut dire :** la taille la plus vendue mérite d'être mise en avant (menus, promotions), et on
      peut se poser la question de garder ou non les tailles qui se vendent très peu.
    """)

    with st.expander("Voir les chiffres par taille"):
        st.dataframe(df_taille.rename(columns={"taille": "Taille", "ca": "CA (€)"}), hide_index=True)
