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

st.title("📅 Activité par jour et par heure")
st.markdown("""
**Pourquoi regarder ça ?** Pour bien organiser le planning de l'équipe (cuisine, livraison), il faut
savoir non seulement quels jours sont les plus chargés, mais aussi à quelle heure de la journée les
commandes arrivent le plus.
""")

st.subheader("Par jour de la semaine")

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
    ecart_jour = (jour_top["nb_commandes"] - jour_bas["nb_commandes"]) / jour_bas["nb_commandes"] * 100
    st.markdown(f"""
    - Le jour le plus actif est **{jour_top['jour_semaine']}** ({jour_top['nb_commandes']} commandes).
    - Le jour le plus calme est **{jour_bas['jour_semaine']}** ({jour_bas['nb_commandes']} commandes).
    - L'écart entre les deux est d'environ **{ecart_jour:.0f} %** — la fin de semaine est nettement plus
      chargée que le début de semaine.
    """)

st.divider()
st.subheader("Par heure de la journée")

requete_heure = f"""
SELECT strftime('%H', o.time) AS heure, COUNT(DISTINCT od.order_id) AS nb_commandes
FROM order_details od
JOIN pizzas p ON od.pizza_id = p.pizza_id
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
JOIN orders o ON od.order_id = o.order_id
WHERE {condition_categorie} AND {condition_taille}
GROUP BY heure
ORDER BY heure
"""
df_heure = pd.read_sql(requete_heure, conn)

fig2, ax2 = plt.subplots()
ax2.bar(df_heure["heure"], df_heure["nb_commandes"])
ax2.set_xlabel("Heure")
ax2.set_ylabel("Nombre de commandes")
st.pyplot(fig2)

if not df_heure.empty:
    heure_top = df_heure.loc[df_heure["nb_commandes"].idxmax()]
    st.markdown(f"""
    - Le pic d'activité est à **{heure_top['heure']}h** avec **{heure_top['nb_commandes']} commandes**.
    - On voit en général deux pics dans la journée : le **midi** et le **soir**, logique pour une pizzeria
      (repas du midi et dîner). L'activité est quasi nulle avant 11h et après 22h.
    - **Ce que ça veut dire pour la pizzeria :** renforcer l'équipe sur ces deux créneaux, surtout les jours
      identifiés ci-dessus (jeudi, vendredi, samedi).
    """)
