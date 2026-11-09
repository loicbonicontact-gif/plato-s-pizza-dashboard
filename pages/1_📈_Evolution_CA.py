# ============================================
# Page : évolution du chiffre d'affaires
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_connection, get_filtres, FROM_VENTES, NOMS_MOIS

st.set_page_config(page_title="Évolution du CA", page_icon="📈", layout="wide")

conn = get_connection()
condition_categorie, condition_taille, condition_periode = get_filtres(conn)

st.title("📈 Évolution du chiffre d'affaires par mois")
st.caption("Question : l'activité est-elle stable sur l'année, ou y a-t-il des périodes à anticiper (stocks, personnel) ?")

requete_ca_mois = f"""
SELECT strftime('%m', o.date) AS num_mois, SUM(od.quantity * p.price) AS ca
{FROM_VENTES}
WHERE {condition_categorie} AND {condition_taille} AND {condition_periode}
GROUP BY num_mois
ORDER BY num_mois
"""
df_ca_mois = pd.read_sql(requete_ca_mois, conn)

if df_ca_mois.empty:
    st.warning("Aucune vente ne correspond à ces filtres.")
    st.stop()

# On remplace "01" par "Janvier" etc. pour que ce soit plus lisible
df_ca_mois["Mois"] = df_ca_mois["num_mois"].map(NOMS_MOIS)

# --- Chiffres clés (ils suivent les filtres) ---
mois_top = df_ca_mois.loc[df_ca_mois["ca"].idxmax()]
mois_bas = df_ca_mois.loc[df_ca_mois["ca"].idxmin()]
k1, k2, k3, k4 = st.columns(4)
k1.metric("CA total", f"{df_ca_mois['ca'].sum():,.0f} $")
k2.metric("CA moyen par mois", f"{df_ca_mois['ca'].mean():,.0f} $")
k3.metric("Meilleur mois", mois_top["Mois"], f"{mois_top['ca']:,.0f} $", delta_color="off")
k4.metric("Mois le plus faible", mois_bas["Mois"], f"{mois_bas['ca']:,.0f} $", delta_color="off")

fig = px.line(df_ca_mois, x="Mois", y="ca", markers=True, labels={"ca": "CA ($)"})
# Trait pointillé = moyenne mensuelle
fig.add_hline(y=df_ca_mois["ca"].mean(), line_dash="dot", annotation_text="moyenne")
st.plotly_chart(fig, width="stretch")

# --- Analyse (calculée à partir des chiffres affichés) ---
ecart = (mois_top["ca"] - mois_bas["ca"]) / mois_bas["ca"] * 100
st.subheader("🔎 Analyse")
st.markdown(f"""
- Meilleur mois : **{mois_top['Mois']}** ({mois_top['ca']:,.0f} $). Mois le plus faible : **{mois_bas['Mois']}** ({mois_bas['ca']:,.0f} $).
- Écart entre les deux : environ **{ecart:.0f} %**.
- **Lecture :** {"l'activité est régulière, pas besoin de renfort saisonnier particulier." if ecart < 25 else "l'écart est important : il faut anticiper les mois forts (stocks, personnel)."}
""")

with st.expander("Voir les chiffres mois par mois"):
    st.dataframe(df_ca_mois[["Mois", "ca"]].rename(columns={"ca": "CA ($)"}), hide_index=True)
