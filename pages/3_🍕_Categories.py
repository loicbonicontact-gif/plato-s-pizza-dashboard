# ============================================
# Page : répartition par catégorie et par taille
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_connection, get_filtres, FROM_VENTES

st.set_page_config(page_title="Catégories", page_icon="🍕", layout="wide")

conn = get_connection()
condition_categorie, condition_taille, condition_periode = get_filtres(conn)
WHERE = f"WHERE {condition_categorie} AND {condition_taille} AND {condition_periode}"

st.title("🍕 Catégories et tailles")
st.caption("Question : quelles catégories et quelles tailles pèsent vraiment dans les ventes ? (utile pour simplifier la carte)")

# CA et quantité dans la même requête, pour chaque catégorie
df_categorie = pd.read_sql(f"""
SELECT pt.category AS Catégorie, SUM(od.quantity * p.price) AS ca, SUM(od.quantity) AS quantite
{FROM_VENTES} {WHERE}
GROUP BY pt.category
""", conn)

# Idem pour chaque taille
df_taille = pd.read_sql(f"""
SELECT p.size AS Taille, SUM(od.quantity * p.price) AS ca, SUM(od.quantity) AS quantite
{FROM_VENTES} {WHERE}
GROUP BY p.size
""", conn)

if df_categorie.empty:
    st.warning("Aucune vente ne correspond à ces filtres.")
    st.stop()

mesure = st.radio("Mesurer en", ["Chiffre d'affaires", "Quantité vendue"], horizontal=True)
colonne = "ca" if mesure == "Chiffre d'affaires" else "quantite"
libelle = "CA ($)" if colonne == "ca" else "Pizzas vendues"

g1, g2 = st.columns(2)
with g1:
    st.subheader("Par catégorie")
    fig = px.pie(df_categorie, names="Catégorie", values=colonne, hole=0.45)
    st.plotly_chart(fig, width="stretch")
with g2:
    st.subheader("Par taille")
    # Les tailles sont rangées de la plus petite à la plus grande
    fig = px.bar(df_taille, x="Taille", y=colonne, labels={colonne: libelle},
                 category_orders={"Taille": ["S", "M", "L", "XL", "XXL"]})
    st.plotly_chart(fig, width="stretch")

# --- Analyse (calculée à partir des chiffres affichés) ---
cat_top = df_categorie.sort_values(colonne, ascending=False).iloc[0]
cat_bas = df_categorie.sort_values(colonne, ascending=False).iloc[-1]
part_cat = cat_top[colonne] / df_categorie[colonne].sum()
taille_top = df_taille.sort_values(colonne, ascending=False).iloc[0]
part_taille = taille_top[colonne] / df_taille[colonne].sum()
# Part des très grandes tailles, toujours mesurée en quantité vendue
grandes = df_taille[df_taille["Taille"].isin(["XL", "XXL"])]["quantite"].sum()
part_grandes = grandes / df_taille["quantite"].sum()

st.subheader("🔎 Analyse")
st.markdown(f"""
- Catégorie en tête : **{cat_top['Catégorie']}** ({part_cat:.1%}). La plus faible : **{cat_bas['Catégorie']}**.
- Taille en tête : **{taille_top['Taille']}** ({part_taille:.1%}).
- Les tailles **XL et XXL** représentent **{part_grandes:.1%}** des pizzas vendues.
- **Lecture :** {"elles se vendent très peu : on peut se demander si elles méritent leur place sur la carte." if part_grandes < 0.05 else "elles pèsent assez pour justifier leur place sur la carte."}
""")

with st.expander("Voir les chiffres détaillés"):
    st.markdown("**Par catégorie**")
    st.dataframe(df_categorie.rename(columns={"ca": "CA ($)", "quantite": "Quantité"}), hide_index=True)
    st.markdown("**Par taille**")
    st.dataframe(df_taille.rename(columns={"ca": "CA ($)", "quantite": "Quantité"}), hide_index=True)
