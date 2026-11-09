# ============================================
# Page : activité par jour et par heure
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_connection, get_filtres, FROM_VENTES, NOMS_JOURS, ORDRE_JOURS

st.set_page_config(page_title="Activité", page_icon="📅", layout="wide")

conn = get_connection()
condition_categorie, condition_taille, condition_periode = get_filtres(conn)
WHERE = f"WHERE {condition_categorie} AND {condition_taille} AND {condition_periode}"

st.title("📅 Activité par jour et par heure")
st.caption("Question : quand faut-il prévoir le plus de monde en cuisine et en livraison ?")

# Par jour : nombre de commandes ET chiffre d'affaires
df_jour = pd.read_sql(f"""
SELECT strftime('%w', o.date) AS num_jour,
       COUNT(DISTINCT od.order_id) AS nb_commandes,
       SUM(od.quantity * p.price) AS ca
{FROM_VENTES} {WHERE}
GROUP BY num_jour
""", conn)

# Par heure : nombre de commandes
df_heure = pd.read_sql(f"""
SELECT CAST(strftime('%H', o.time) AS INTEGER) AS heure, COUNT(DISTINCT od.order_id) AS nb_commandes
{FROM_VENTES} {WHERE}
GROUP BY heure
ORDER BY heure
""", conn)

if df_jour.empty:
    st.warning("Aucune vente ne correspond à ces filtres.")
    st.stop()

df_jour["Jour"] = df_jour["num_jour"].map(NOMS_JOURS)

# --- Par jour ---
st.subheader("Par jour de la semaine")
mesure = st.radio("Mesurer en", ["Nombre de commandes", "Chiffre d'affaires"], horizontal=True)
colonne = "nb_commandes" if mesure == "Nombre de commandes" else "ca"
fig = px.bar(df_jour, x="Jour", y=colonne, labels={"nb_commandes": "Commandes", "ca": "CA ($)"},
             category_orders={"Jour": ORDRE_JOURS})
st.plotly_chart(fig, width="stretch")

jours_tries = df_jour.sort_values(colonne, ascending=False)
jour_top = jours_tries.iloc[0]
jour_bas = jours_tries.iloc[-1]
ecart_jour = (jour_top[colonne] - jour_bas[colonne]) / jour_bas[colonne] * 100
trois_jours = ", ".join(jours_tries["Jour"].head(3))
st.markdown(f"""
- Jour le plus actif : **{jour_top['Jour']}** ; le plus calme : **{jour_bas['Jour']}**. Écart : environ **{ecart_jour:.0f} %**.
- Les 3 jours les plus chargés : **{trois_jours}**.
""")

st.divider()

# --- Par heure ---
st.subheader("Par heure de la journée")
fig = px.bar(df_heure, x="heure", y="nb_commandes", labels={"heure": "Heure", "nb_commandes": "Commandes"})
st.plotly_chart(fig, width="stretch")

heures_tries = df_heure.sort_values("nb_commandes", ascending=False)
top_heures = ", ".join(f"{h}h" for h in heures_tries["heure"].head(3).sort_values())
st.markdown(f"""
- Les 3 heures les plus chargées : **{top_heures}**.
- **Ce que ça veut dire :** renforcer l'équipe sur ces heures-là, surtout les jours les plus chargés ci-dessus.
""")
