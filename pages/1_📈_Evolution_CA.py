# ============================================
# Page : évolution du chiffre d'affaires
# ============================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import get_connection, get_filtres

st.set_page_config(page_title="Évolution du CA", page_icon="📈")

conn = get_connection()
condition_categorie, condition_taille = get_filtres(conn)

st.title("📈 Évolution du chiffre d'affaires par mois")
st.write("Ce graphique montre si les ventes sont stables sur l'année, ou s'il y a des mois plus forts que d'autres.")

requete_ca_mois = f"""
SELECT strftime('%Y-%m', o.date) AS mois, SUM(od.quantity * p.price) AS ca
FROM order_details od
JOIN pizzas p ON od.pizza_id = p.pizza_id
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
JOIN orders o ON od.order_id = o.order_id
WHERE {condition_categorie} AND {condition_taille}
GROUP BY mois
ORDER BY mois
"""
df_ca_mois = pd.read_sql(requete_ca_mois, conn)

# On remplace "2015-01" par "Janvier" etc. pour que ce soit plus lisible sur le graphique
noms_mois = {
    "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
    "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
    "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre",
}
df_ca_mois["mois_nom"] = df_ca_mois["mois"].str[5:7].map(noms_mois)

fig, ax = plt.subplots()
# marker="o" = un point rond sur chaque mois, pour bien voir chaque valeur sur la courbe
ax.plot(df_ca_mois["mois_nom"], df_ca_mois["ca"], marker="o")
ax.set_xlabel("Mois")
ax.set_ylabel("CA (€)")
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
st.pyplot(fig)

# Interprétation automatique : on retrouve le meilleur et le moins bon mois dans les données affichées
if not df_ca_mois.empty:
    meilleur_mois = df_ca_mois.loc[df_ca_mois["ca"].idxmax()]
    pire_mois = df_ca_mois.loc[df_ca_mois["ca"].idxmin()]
    st.info(
        f"Le meilleur mois est **{meilleur_mois['mois_nom']}** avec **{meilleur_mois['ca']:,.2f} €**, "
        f"contre **{pire_mois['ca']:,.2f} €** pour le mois le plus faible ({pire_mois['mois_nom']})."
    )
