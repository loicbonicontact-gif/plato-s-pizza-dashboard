# ============================================
# Page : activité par jour de la semaine
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import get_connection, get_filtres

st.set_page_config(page_title="Activité", page_icon="📅")

conn = get_connection()
condition_categorie, condition_taille = get_filtres(conn)

st.title("📅 Activité par jour de la semaine")
st.write("Utile pour organiser le planning de l'équipe en cuisine et en livraison : savoir quels jours sont les plus chargés.")

requete_jour = f"""
SELECT strftime('%w', o.date) AS jour_semaine, COUNT(DISTINCT od.order_id) AS nb_commandes
FROM order_details od
JOIN pizzas p ON od.pizza_id = p.pizza_id
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
JOIN orders o ON od.order_id = o.order_id
WHERE {condition_categorie} AND {condition_taille}
GROUP BY jour_semaine
ORDER BY jour_semaine
"""
df_jour = pd.read_sql(requete_jour, conn)
# Dans la base, les jours sont des chiffres (0 = dimanche, 1 = lundi, ...), on les remplace par des noms
noms_jours = {"0": "Dimanche", "1": "Lundi", "2": "Mardi", "3": "Mercredi", "4": "Jeudi", "5": "Vendredi", "6": "Samedi"}
df_jour["jour_semaine"] = df_jour["jour_semaine"].map(noms_jours)

fig, ax = plt.subplots()
ax.bar(df_jour["jour_semaine"], df_jour["nb_commandes"])
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
ax.set_ylabel("Nombre de commandes")
st.pyplot(fig)

if not df_jour.empty:
    jour_top = df_jour.loc[df_jour["nb_commandes"].idxmax()]
    jour_bas = df_jour.loc[df_jour["nb_commandes"].idxmin()]
    st.info(f"Le jour le plus actif est **{jour_top['jour_semaine']}** ({jour_top['nb_commandes']} commandes), le plus calme est **{jour_bas['jour_semaine']}** ({jour_bas['nb_commandes']} commandes).")
