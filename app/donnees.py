"""Accès aux données du tableau de bord : tables gold lues dans PostgreSQL, contours des départements.

Les paramètres de connexion viennent de variables d'environnement (définies dans compose.yaml).
Valeurs par défaut = lancement depuis le poste (PostgreSQL publié sur le port 5433).
"""
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ASSETS = Path(__file__).parent / "assets"
DOM = {"971": "Guadeloupe", "972": "Martinique", "973": "Guyane", "974": "La Réunion", "976": "Mayotte"}


def _url():
    return URL.create(
        "postgresql+psycopg2",
        username=os.getenv("PG_USER", "dvf"), password=os.getenv("PG_PASSWORD", "dvf"),
        host=os.getenv("PG_HOST", "localhost"), port=int(os.getenv("PG_PORT", "5433")),
        database=os.getenv("PG_DB", "dvf"),
    )


@st.cache_resource
def geojson_metropole():
    """Contours simplifiés des départements de métropole (Corse comprise)."""
    return json.loads((ASSETS / "departements.geojson").read_text(encoding="utf-8"))


@st.cache_data
def noms_departements():
    noms = {f["properties"]["code"]: f["properties"]["nom"] for f in geojson_metropole()["features"]}
    noms.update(DOM)
    return noms


@st.cache_data(ttl=600, show_spinner="Lecture des tables gold dans PostgreSQL…")
def charger():
    """Retourne (departement, departement_mois, national_mois) sous forme de DataFrames pandas."""
    moteur = create_engine(_url(), pool_pre_ping=True)
    with moteur.connect() as c:
        dep = pd.read_sql(text("SELECT * FROM gold_departement"), c)
        mois = pd.read_sql(text("SELECT * FROM gold_departement_mois"), c)
        nat = pd.read_sql(text("SELECT * FROM gold_national_mois"), c)
    noms = noms_departements()
    for t in (dep, mois):
        t["departement"] = t["code_departement"].map(noms).fillna(t["code_departement"])
    dep["ecart_pct"] = dep["ecart_national"] * 100
    return dep, mois, nat
