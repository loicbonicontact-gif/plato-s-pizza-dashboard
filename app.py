# ============================================
# Application Streamlit - Plato's Pizza
# Page d'accueil = tableau de bord (vue d'ensemble)
# ============================================
# Les chiffres viennent de pizza.db (jamais des CSV directement).
# Les pages de détail sont dans le dossier pages/.

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_connection, get_filtres, FROM_VENTES, NOMS_JOURS, ORDRE_JOURS, NOMS_MOIS

st.set_page_config(page_title="Plato's Pizza — Accueil", page_icon="🍕", layout="wide")

conn = get_connection()

st.title("Plato's Pizza — Tableau de bord")
st.caption("Ventes 2015 · les filtres à gauche (catégorie, taille, période) s'appliquent à tous les chiffres et graphiques.")

# Les filtres de la barre latérale deviennent trois morceaux de WHERE
condition_categorie, condition_taille, condition_periode = get_filtres(conn)
WHERE = f"WHERE {condition_categorie} AND {condition_taille} AND {condition_periode}"

# --- Indicateurs clés (une seule requête) ---
requete_kpi = f"""
SELECT
    SUM(od.quantity * p.price) AS ca_total,
    COUNT(DISTINCT od.order_id) AS nb_commandes,
    SUM(od.quantity) AS nb_pizzas,
    COUNT(DISTINCT o.date) AS nb_jours,
    COUNT(DISTINCT strftime('%Y-%m', o.date)) AS nb_mois
{FROM_VENTES}
{WHERE}
"""
kpi = pd.read_sql(requete_kpi, conn)

# Si les filtres ne laissent aucune vente, on le dit et on s'arrête (sinon les graphiques plantent)
if kpi["nb_commandes"][0] == 0:
    st.warning("Aucune vente ne correspond à ces filtres. Élargis la période ou remets « Toutes ».")
    st.stop()

ca_total = kpi["ca_total"][0]
nb_commandes = kpi["nb_commandes"][0]
nb_pizzas = kpi["nb_pizzas"][0]
panier_moyen = ca_total / nb_commandes
ca_moyen_mois = ca_total / kpi["nb_mois"][0]
ca_moyen_jour = ca_total / kpi["nb_jours"][0]
pizzas_par_commande = nb_pizzas / nb_commandes

# --- Données des graphiques ---
# 1) CA par mois
df_mois = pd.read_sql(f"""
SELECT strftime('%m', o.date) AS num_mois, SUM(od.quantity * p.price) AS ca
{FROM_VENTES} {WHERE}
GROUP BY num_mois ORDER BY num_mois
""", conn)
df_mois["Mois"] = df_mois["num_mois"].map(NOMS_MOIS)

# 2) CA par jour de la semaine
df_jour = pd.read_sql(f"""
SELECT strftime('%w', o.date) AS num_jour, SUM(od.quantity * p.price) AS ca
{FROM_VENTES} {WHERE}
GROUP BY num_jour
""", conn)
df_jour["Jour"] = df_jour["num_jour"].map(NOMS_JOURS)

# 3) Top 10 pizzas (CA et quantité dans la même requête, l'utilisateur choisit l'affichage)
df_top = pd.read_sql(f"""
SELECT pt.name AS Pizza, SUM(od.quantity * p.price) AS ca, SUM(od.quantity) AS quantite
{FROM_VENTES} {WHERE}
GROUP BY pt.name
""", conn)

# 4) CA par catégorie
df_cat = pd.read_sql(f"""
SELECT pt.category AS Catégorie, SUM(od.quantity * p.price) AS ca
{FROM_VENTES} {WHERE}
GROUP BY pt.category
""", conn)

# 5) Nombre de commandes par jour de semaine et par heure (pour la carte de chaleur)
df_heat = pd.read_sql(f"""
SELECT strftime('%w', o.date) AS num_jour, CAST(strftime('%H', o.time) AS INTEGER) AS heure,
       COUNT(DISTINCT od.order_id) AS nb_commandes
{FROM_VENTES} {WHERE}
GROUP BY num_jour, heure
""", conn)
df_heat["Jour"] = df_heat["num_jour"].map(NOMS_JOURS)

# --- Rangée de chiffres clés ---
mois_top = df_mois.loc[df_mois["ca"].idxmax()]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Chiffre d'affaires", f"{ca_total:,.0f} €")
c2.metric("Commandes", f"{nb_commandes:,}")
c3.metric("Panier moyen", f"{panier_moyen:,.2f} €")
c4.metric("Pizzas vendues", f"{nb_pizzas:,}")
c5, c6, c7, c8 = st.columns(4)
c5.metric("CA moyen par mois", f"{ca_moyen_mois:,.0f} €")
c6.metric("CA moyen par jour", f"{ca_moyen_jour:,.0f} €")
c7.metric("Pizzas par commande", f"{pizzas_par_commande:.1f}")
c8.metric("Meilleur mois", mois_top["Mois"], f"{mois_top['ca']:,.0f} €", delta_color="off")

st.divider()

# --- Ligne 1 : évolution + jours de la semaine ---
g1, g2 = st.columns(2)
with g1:
    st.subheader("CA par mois")
    fig = px.line(df_mois, x="Mois", y="ca", markers=True, labels={"ca": "CA (€)"})
    # Trait pointillé = moyenne mensuelle, pour voir d'un coup d'œil qui est au-dessus ou en dessous
    fig.add_hline(y=df_mois["ca"].mean(), line_dash="dot", annotation_text="moyenne")
    st.plotly_chart(fig, width="stretch")
with g2:
    st.subheader("CA par jour de la semaine")
    fig = px.bar(df_jour, x="Jour", y="ca", labels={"ca": "CA (€)"},
                 category_orders={"Jour": ORDRE_JOURS})
    st.plotly_chart(fig, width="stretch")
    jour_top = df_jour.loc[df_jour["ca"].idxmax()]
    jour_bas = df_jour.loc[df_jour["ca"].idxmin()]
    st.caption(f"**{jour_top['Jour']}** rapporte le plus ({jour_top['ca']:,.0f} €), **{jour_bas['Jour']}** le moins ({jour_bas['ca']:,.0f} €).")

# --- Ligne 2 : top pizzas + catégories ---
g3, g4 = st.columns(2)
with g3:
    st.subheader("Top 10 des pizzas")
    mesure = st.radio("Classer par", ["Chiffre d'affaires", "Quantité vendue"], horizontal=True)
    colonne = "ca" if mesure == "Chiffre d'affaires" else "quantite"
    top10 = df_top.sort_values(colonne, ascending=False).head(10)
    fig = px.bar(top10, x=colonne, y="Pizza", orientation="h",
                 labels={"ca": "CA (€)", "quantite": "Pizzas vendues"})
    # On remet la meilleure pizza en haut du graphique
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, width="stretch")
with g4:
    st.subheader("Répartition du CA par catégorie")
    fig = px.pie(df_cat, names="Catégorie", values="ca", hole=0.45)
    st.plotly_chart(fig, width="stretch")
    cat_top = df_cat.loc[df_cat["ca"].idxmax()]
    st.caption(f"**{cat_top['Catégorie']}** pèse {cat_top['ca'] / df_cat['ca'].sum():.0%} du CA affiché.")

# --- Ligne 3 : carte de chaleur jour x heure ---
st.subheader("Quand les clients commandent-ils ? (nombre de commandes)")
# On transforme la liste en tableau : une ligne par jour, une colonne par heure
tableau = df_heat.pivot_table(index="Jour", columns="heure", values="nb_commandes", fill_value=0)
tableau = tableau.reindex([j for j in ORDRE_JOURS if j in tableau.index])
fig = px.imshow(tableau, aspect="auto", color_continuous_scale="YlOrRd",
                labels={"x": "Heure", "y": "", "color": "Commandes"})
st.plotly_chart(fig, width="stretch")
heure_top = df_heat.groupby("heure")["nb_commandes"].sum().idxmax()
st.caption(f"Plus la case est foncée, plus il y a de commandes. Heure la plus chargée : **{heure_top}h**.")

with st.expander("🎯 Les questions auxquelles répond ce tableau de bord"):
    st.markdown("""
    1. **Combien l'entreprise a-t-elle gagné, et est-ce stable sur l'année ?** → CA par mois, page « Évolution du CA ».
    2. **Quelles pizzas rapportent le plus (et le moins) ?** → Top 10, page « Top Pizzas ».
    3. **Quelle catégorie et quelle taille pèsent le plus ?** → page « Catégories ».
    4. **Quand prévoir le plus de monde en cuisine/livraison ?** → carte de chaleur, page « Activité ».
    5. **Combien dépense un client par commande ?** → panier moyen.

    Pour les conclusions et les limites, va sur la page « Recommandations ».
    """)

st.caption("Projet Data Analyst — Plato's Pizza · SQL (SQLite) · Python (pandas) · Plotly · Streamlit")
