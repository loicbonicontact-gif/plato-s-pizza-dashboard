# ============================================
# Fonctions communes à toutes les pages
# ============================================
# Ce fichier évite de recopier 10 fois le même code de connexion
# et de filtres sur chaque page de l'application.

import streamlit as st
import pandas as pd
import sqlite3


def get_connection():
    # Ouvre une connexion vers la base pizza.db
    return sqlite3.connect("pizza.db")


def get_filtres(conn):
    # Récupère les catégories et tailles possibles pour remplir les menus déroulants
    categories = pd.read_sql("SELECT DISTINCT category FROM pizza_types ORDER BY category", conn)["category"].tolist()
    tailles = pd.read_sql("SELECT DISTINCT size FROM pizzas ORDER BY size", conn)["size"].tolist()

    st.sidebar.header("Filtres")
    categorie_choisie = st.sidebar.selectbox("Catégorie", options=["Toutes"] + categories)
    taille_choisie = st.sidebar.selectbox("Taille", options=["Toutes"] + tailles)

    # "Toutes" = l'utilisateur ne filtre rien, on garde toutes les lignes
    condition_categorie = "1=1" if categorie_choisie == "Toutes" else f"pt.category = '{categorie_choisie}'"
    condition_taille = "1=1" if taille_choisie == "Toutes" else f"p.size = '{taille_choisie}'"

    return condition_categorie, condition_taille
