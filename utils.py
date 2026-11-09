# ============================================
# Fonctions communes à toutes les pages
# ============================================
# Ce fichier évite de recopier 10 fois le même code de connexion,
# de filtres et de jointures sur chaque page de l'application.

import streamlit as st
import pandas as pd
import sqlite3
import datetime

# Les jointures sont toujours les mêmes : on les écrit une seule fois ici.
# Une ligne de vente = une ligne de commande (order_details) + le prix (pizzas)
# + le type/catégorie (pizza_types) + la date et l'heure (orders).
FROM_VENTES = """
FROM order_details od
JOIN pizzas p ON od.pizza_id = p.pizza_id
JOIN pizza_types pt ON p.pizza_type_id = pt.pizza_type_id
JOIN orders o ON od.order_id = o.order_id
"""

# Les jours sortent de SQLite en chiffres (0 = dimanche). On les remplace par des noms.
NOMS_JOURS = {"0": "Dimanche", "1": "Lundi", "2": "Mardi", "3": "Mercredi",
              "4": "Jeudi", "5": "Vendredi", "6": "Samedi"}
# Ordre d'affichage : on commence la semaine par lundi
ORDRE_JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

NOMS_MOIS = {"01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
             "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
             "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"}


def get_connection():
    # Ouvre une connexion vers la base pizza.db
    return sqlite3.connect("pizza.db")


def get_filtres(conn):
    # Récupère les catégories et tailles possibles pour remplir les menus déroulants
    categories = pd.read_sql("SELECT DISTINCT category FROM pizza_types ORDER BY category", conn)["category"].tolist()
    tailles = pd.read_sql("SELECT DISTINCT size FROM pizzas ORDER BY size", conn)["size"].tolist()
    # Première et dernière date de vente : elles servent de bornes au filtre de période
    bornes = pd.read_sql("SELECT MIN(date) AS debut, MAX(date) AS fin FROM orders", conn)
    date_min = datetime.date.fromisoformat(bornes["debut"][0])
    date_max = datetime.date.fromisoformat(bornes["fin"][0])

    st.sidebar.header("Filtres")
    categorie_choisie = st.sidebar.selectbox("Catégorie", options=["Toutes"] + categories)
    taille_choisie = st.sidebar.selectbox("Taille", options=["Toutes"] + tailles)
    periode = st.sidebar.date_input(
        "Période", value=(date_min, date_max), min_value=date_min, max_value=date_max
    )

    # "Toutes" = l'utilisateur ne filtre rien, on garde toutes les lignes
    condition_categorie = "1=1" if categorie_choisie == "Toutes" else f"pt.category = '{categorie_choisie}'"
    condition_taille = "1=1" if taille_choisie == "Toutes" else f"p.size = '{taille_choisie}'"

    # Pendant que l'utilisateur clique, il peut n'avoir choisi qu'une seule date :
    # dans ce cas on garde toute l'année le temps qu'il choisisse la deuxième.
    if isinstance(periode, (tuple, list)) and len(periode) == 2:
        debut, fin = periode
    else:
        debut, fin = date_min, date_max
    condition_periode = f"o.date BETWEEN '{debut.isoformat()}' AND '{fin.isoformat()}'"

    return condition_categorie, condition_taille, condition_periode
