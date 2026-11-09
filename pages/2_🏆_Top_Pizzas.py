# ============================================
# Page : top et flop des pizzas
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_connection, get_filtres, FROM_VENTES

st.set_page_config(page_title="Top Pizzas", page_icon="🏆", layout="wide")

conn = get_connection()
condition_categorie, condition_taille, condition_periode = get_filtres(conn)

st.title("🏆 Top et flop des pizzas")
st.caption("Question : quelles pizzas mettre en avant, et lesquelles questionner ?")

# Une seule requête : CA et quantité pour chaque pizza (on garde aussi la catégorie)
requete = f"""
SELECT pt.name AS Pizza, pt.category AS Catégorie,
       SUM(od.quantity * p.price) AS ca, SUM(od.quantity) AS quantite
{FROM_VENTES}
WHERE {condition_categorie} AND {condition_taille} AND {condition_periode}
GROUP BY pt.name, pt.category
"""
df = pd.read_sql(requete, conn)

if df.empty:
    st.warning("Aucune vente ne correspond à ces filtres.")
    st.stop()

mesure = st.radio("Classer par", ["Chiffre d'affaires", "Quantité vendue"], horizontal=True)
colonne = "ca" if mesure == "Chiffre d'affaires" else "quantite"
libelle = "CA ($)" if colonne == "ca" else "Pizzas vendues"

top = df.sort_values(colonne, ascending=False).head(10)
flop = df.sort_values(colonne, ascending=True).head(5)

g1, g2 = st.columns([3, 2])
with g1:
    st.subheader("Top 10")
    fig = px.bar(top, x=colonne, y="Pizza", orientation="h", color="Catégorie", labels={colonne: libelle})
    fig.update_yaxes(autorange="reversed")  # meilleure pizza en haut
    st.plotly_chart(fig, width="stretch")
with g2:
    st.subheader("5 pizzas les moins vendues")
    st.dataframe(flop[["Pizza", "Catégorie", "ca", "quantite"]].rename(
        columns={"ca": "CA ($)", "quantite": "Quantité"}), hide_index=True)

# --- Analyse (calculée à partir des chiffres affichés) ---
meilleure = top.iloc[0]
pire = flop.iloc[0]
# Quelle catégorie revient le plus souvent dans le top 10 ?
cat_frequente = top["Catégorie"].value_counts()
st.subheader("🔎 Analyse")
st.markdown(f"""
- **{meilleure['Pizza']}** est en tête ({meilleure['ca']:,.0f} $ de CA, {meilleure['quantite']:,.0f} pizzas vendues).
- La catégorie la plus présente dans ce top 10 est **{cat_frequente.index[0]}** ({cat_frequente.iloc[0]} pizzas sur {len(top)}).
- À l'autre bout, **{pire['Pizza']}** ({pire['ca']:,.0f} $ de CA, {pire['quantite']:,.0f} pizzas) : à surveiller, vaut-il la peine de la garder au menu ?
- **À savoir :** le classement en CA et en quantité n'est pas le même. Une pizza chère peut rapporter plus sans être la plus commandée : change l'option « Classer par » pour comparer.
""")
