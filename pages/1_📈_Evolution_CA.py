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
st.markdown("""
**Pourquoi regarder ça ?** Avant de parler de produits ou de jours précis, la première question
à se poser est simple : est-ce que l'activité est stable sur l'année, ou est-ce qu'il y a des
périodes beaucoup plus fortes (ou plus faibles) que d'autres ? Si oui, il faut s'y préparer à
l'avance (stocks, personnel).
""")

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

# --- Chiffres clés du CA (ils suivent les filtres de la barre latérale) ---
if not df_ca_mois.empty:
    ca_annee = df_ca_mois["ca"].sum()
    ca_moyen = df_ca_mois["ca"].mean()
    mois_top = df_ca_mois.loc[df_ca_mois["ca"].idxmax()]
    mois_bas = df_ca_mois.loc[df_ca_mois["ca"].idxmin()]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("CA total", f"{ca_annee:,.0f} €")
    k2.metric("CA moyen par mois", f"{ca_moyen:,.0f} €")
    k3.metric("Meilleur mois", mois_top["mois_nom"], f"{mois_top['ca']:,.0f} €", delta_color="off")
    k4.metric("Mois le plus faible", mois_bas["mois_nom"], f"{mois_bas['ca']:,.0f} €", delta_color="off")

fig, ax = plt.subplots()
# marker="o" = un point rond sur chaque mois, pour bien voir chaque valeur sur la courbe
ax.plot(df_ca_mois["mois_nom"], df_ca_mois["ca"], marker="o")
ax.set_xlabel("Mois")
ax.set_ylabel("CA (€)")
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
st.pyplot(fig)

st.subheader("🔎 Analyse")

# Interprétation automatique : on retrouve le meilleur/pire mois et on calcule l'écart entre les deux
if not df_ca_mois.empty:
    meilleur_mois = df_ca_mois.loc[df_ca_mois["ca"].idxmax()]
    pire_mois = df_ca_mois.loc[df_ca_mois["ca"].idxmin()]
    ecart_pourcentage = (meilleur_mois["ca"] - pire_mois["ca"]) / pire_mois["ca"] * 100

    st.markdown(f"""
    - Le meilleur mois est **{meilleur_mois['mois_nom']}** avec **{meilleur_mois['ca']:,.2f} €** de chiffre d'affaires.
    - Le mois le plus faible est **{pire_mois['mois_nom']}** avec **{pire_mois['ca']:,.2f} €**.
    - L'écart entre les deux est d'environ **{ecart_pourcentage:.0f} %**, ce qui reste raisonnable : il n'y a pas de
      mois catastrophique ni de mois exceptionnel qui sort vraiment du lot.
    - **Ce que ça veut dire pour la pizzeria :** pas besoin de prévoir des renforts ou des stocks spéciaux pour
      un mois en particulier — l'activité est globalement régulière sur l'année.
    """)

    with st.expander("Voir les chiffres mois par mois"):
        st.dataframe(df_ca_mois[["mois_nom", "ca"]].rename(columns={"mois_nom": "Mois", "ca": "CA (€)"}), hide_index=True)
