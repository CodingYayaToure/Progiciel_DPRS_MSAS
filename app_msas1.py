import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Suivi des conventions DPRS", layout="wide")

# Connexion à la base de données SQLite
DB_PATH = "dprs_msas.db"

def create_connection():
    return sqlite3.connect(DB_PATH)

# Fonction pour exécuter une requête SQL
def execute_query(query, params=()):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

# Fonction pour récupérer les données depuis la base de données
def get_data_from_db(query, params=()):
    conn = create_connection()
    data = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return data

# Fonction pour initialiser la base de données
def initialize_database():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conventions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        regions TEXT,
        districts TEXT,
        etablissement TEXT,
        titre TEXT,
        date_signature TEXT,
        duree TEXT,
        objet TEXT,
        engagements_msnas TEXT,
        engagements_structures TEXT,
        observations TEXT
    )
    """)
    conn.commit()
    conn.close()

# Initialiser la base de données
initialize_database()

# **Mot de passe unique pour sécuriser l'accès**
PASSWORD = "secure_ms@s17"

def check_password():
    """Vérifie si le mot de passe est correct."""
    if "password_correct" not in st.session_state:
        st.text_input("Mot de passe :", type="password", key="password")
        if st.button("Se connecter"):
            if st.session_state["password"] == PASSWORD:
                st.session_state["password_correct"] = True
                del st.session_state["password"]
            else:
                st.error("Mot de passe incorrect.")
    elif st.session_state["password_correct"]:
        return True
    return False

# Vérifiez si l'utilisateur est authentifié
if check_password():
    # Récupérer les données actuelles
    query = "SELECT * FROM conventions"
    data = get_data_from_db(query)

    # Barre latérale avec le logo
    with st.sidebar:
        st.image("ministere_sante.png", width=300)  # Logo à gauche
        st.markdown("## Suivi des conventions DPRS")

    # Barre de recherche au-dessus des données actuelles
    st.title("Suivi des Conventions DPRS")
    st.markdown("### Recherche dans les Données Actuelles")
    search_term = st.text_input("Rechercher dans les données", "")

    # Filtrer les données selon la recherche
    filtered_data = data.copy()
    if search_term:
        filtered_data = filtered_data[
            filtered_data.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        ]

    # Afficher les données actuelles
    st.markdown("### Données Actuelles")
    if not filtered_data.empty:
        st.dataframe(filtered_data.reset_index(drop=True), width=1800)
    else:
        st.warning("Aucune donnée ne correspond à votre recherche.")

    # Section Horizontale : Ajouter et Modifier une Entrée
    st.markdown("---")
    st.subheader("Ajouter et Modifier une Entrée")

    col1, col2 = st.columns(2)  # Deux colonnes pour afficher côte à côte

    # **Colonne 1 : Ajouter une Nouvelle Entrée**
    with col1:
        st.write("### Ajouter une Nouvelle Entrée")
        with st.form(key="add_form"):
            region = st.text_input("Région").upper()
            district = st.text_input("Districts Sanitaires")
            etablissement = st.text_input("Etablissement de santé / EPS-Centre et Postes de santé")
            titre = st.text_input("Titre de la convention")
            date_signature = st.date_input("Date de Signature")
            duree = st.text_input("Durée de la convention")
            objet = st.text_area("Objet de la convention", height=100)
            engagements_msnas = st.text_area("Engagements du MSNAS", height=100)
            engagements_structures = st.text_area("Engagements des Structures Sanitaires", height=100)
            observations = st.text_area("Observations", height=100)

            if st.form_submit_button("Ajouter"):
                try:
                    query = """
                    INSERT INTO conventions (regions, districts, etablissement, titre, date_signature, duree, objet, engagements_msnas, engagements_structures, observations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    params = (region, district, etablissement, titre, date_signature.strftime('%d-%m-%Y'), duree, objet, engagements_msnas, engagements_structures, observations)
                    execute_query(query, params)
                    st.success("Nouvelle entrée ajoutée avec succès !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de l'ajout de l'entrée : {e}")

    # **Colonne 2 : Modifier une Entrée**
    with col2:
        st.write("### Modifier une Entrée")
        if not data.empty:
            entry_id = st.selectbox("ID de l'entrée à modifier", options=data['id'])
            if entry_id:
                row_data = data[data['id'] == entry_id].iloc[0]
                with st.form(key="edit_form"):
                    region = st.text_input("Région", value=row_data['regions']).upper()
                    district = st.text_input("Districts Sanitaires", value=row_data['districts'])
                    etablissement = st.text_input("Etablissement de santé / EPS-Centre et Postes de santé", value=row_data['etablissement'])
                    titre = st.text_input("Titre de la convention", value=row_data['titre'])
                    date_signature = st.date_input("Date de Signature", value=pd.to_datetime(row_data['date_signature'], format='%d-%m-%Y').date())
                    duree = st.text_input("Durée de la convention", value=row_data['duree'])
                    objet = st.text_area("Objet de la convention", value=row_data['objet'], height=100)
                    engagements_msnas = st.text_area("Engagements du MSNAS", value=row_data['engagements_msnas'], height=100)
                    engagements_structures = st.text_area("Engagements des Structures Sanitaires", value=row_data['engagements_structures'], height=100)
                    observations = st.text_area("Observations", value=row_data['observations'], height=100)

                    if st.form_submit_button("Mettre à jour"):
                        try:
                            query = """
                            UPDATE conventions
                            SET regions = ?, districts = ?, etablissement = ?, titre = ?, date_signature = ?, duree = ?, objet = ?, engagements_msnas = ?, engagements_structures = ?, observations = ?
                            WHERE id = ?
                            """
                            params = (region, district, etablissement, titre, date_signature.strftime('%d-%m-%Y'), duree, objet, engagements_msnas, engagements_structures, observations, entry_id)
                            execute_query(query, params)
                            st.success("Entrée mise à jour avec succès !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de la mise à jour de l'entrée : {e}")

    # Section Supprimer une Entrée
    st.markdown("---")
    st.subheader("Supprimer une Entrée")
    if not data.empty:
        delete_id = st.selectbox("ID de l'entrée à supprimer", options=data['id'])
        if st.button("Supprimer"):
            try:
                query = "DELETE FROM conventions WHERE id = ?"
                execute_query(query, (delete_id,))
                st.success("Entrée supprimée avec succès !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de la suppression de l'entrée : {e}")
