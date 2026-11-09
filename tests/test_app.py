# Tests automatiques : on vérifie que chaque page s'ouvre sans erreur
# et que les chiffres cités dans les recommandations sont vrais dans la base.
# Lancer avec : python3 -m pytest tests -q   (depuis le dossier du projet)

import glob
import os
import sqlite3
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

# On travaille toujours depuis la racine du projet (là où se trouvent app.py et pizza.db)
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
PAGES = [os.path.join(RACINE, "app.py")] + sorted(glob.glob(os.path.join(RACINE, "pages", "*.py")))


@pytest.mark.parametrize("page", PAGES)
def test_page_sans_filtre(page):
    # La page s'ouvre sans aucune erreur
    at = AppTest.from_file(page, default_timeout=60).run()
    assert not at.exception, at.exception


@pytest.mark.parametrize("page", [p for p in PAGES if "Recommandations" not in p])
def test_page_avec_filtres(page):
    # On choisit une catégorie et une taille, la page doit rester sans erreur
    at = AppTest.from_file(page, default_timeout=60).run()
    at.sidebar.selectbox[0].select("Veggie").run()
    at.sidebar.selectbox[1].select("L").run()
    assert not at.exception, at.exception


@pytest.mark.parametrize("page", [p for p in PAGES if "Recommandations" not in p])
def test_page_sans_resultat(page):
    # Combinaison sans ventes possible : on choisit une période d'un seul jour très creux
    # (le 1er janvier + XXL + Veggie n'a sûrement aucune vente) -> message, pas de plantage
    import datetime
    at = AppTest.from_file(page, default_timeout=60).run()
    at.sidebar.selectbox[1].select("XXL").run()
    at.sidebar.date_input[0].set_value((datetime.date(2015, 1, 1), datetime.date(2015, 1, 1))).run()
    assert not at.exception, at.exception


def test_chiffres_cles_accueil():
    # Les chiffres de l'accueil doivent correspondre à ceux du notebook
    at = AppTest.from_file(os.path.join(RACINE, "app.py"), default_timeout=60).run()
    valeurs = {m.label: m.value for m in at.metric}
    assert valeurs["Chiffre d'affaires"] == "817,860 €"
    assert valeurs["Commandes"] == "21,350"
    assert valeurs["Panier moyen"] == "38.31 €"
    assert valeurs["Pizzas vendues"] == "49,574"


def test_filtre_periode_reduit_le_ca():
    # Un seul mois choisi : le CA doit baisser fortement
    import datetime
    at = AppTest.from_file(os.path.join(RACINE, "app.py"), default_timeout=60).run()
    at.sidebar.date_input[0].set_value((datetime.date(2015, 1, 1), datetime.date(2015, 1, 31))).run()
    ca = {m.label: m.value for m in at.metric}["Chiffre d'affaires"]
    assert ca != "817,860 €"


# --- Chiffres cités dans la page Recommandations ---
@pytest.fixture
def conn():
    return sqlite3.connect("pizza.db")


def test_recommandations_chiffres(conn):
    base = """FROM order_details od JOIN pizzas p ON od.pizza_id=p.pizza_id
              JOIN pizza_types pt ON p.pizza_type_id=pt.pizza_type_id JOIN orders o ON od.order_id=o.order_id"""
    tailles = pd.read_sql(f"SELECT p.size, SUM(od.quantity) q {base} GROUP BY p.size", conn).set_index("size")["q"]
    assert tailles["XL"] == 552 and tailles["XXL"] == 28 and tailles.idxmax() == "L"
    pizzas = pd.read_sql(f"SELECT pt.name, SUM(od.quantity) q, SUM(od.quantity*p.price) ca {base} GROUP BY pt.name", conn).set_index("name")
    assert pizzas["q"].idxmin() == "The Brie Carre Pizza" and pizzas.loc["The Brie Carre Pizza", "q"] == 490
    assert set(pizzas["ca"].nlargest(2).index) == {"The Thai Chicken Pizza", "The Barbecue Chicken Pizza"}
    jours = pd.read_sql("SELECT strftime('%w',date) j, COUNT(*) n FROM orders GROUP BY j", conn).set_index("j")["n"]
    assert set(jours.nlargest(3).index) == {"4", "5", "6"}  # jeudi, vendredi, samedi
    heures = pd.read_sql("SELECT CAST(strftime('%H',time) AS INT) h, COUNT(*) n FROM orders GROUP BY h", conn).set_index("h")["n"]
    assert set(heures.nlargest(2).index) == {12, 13}
