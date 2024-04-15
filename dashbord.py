import streamlit as st
import pandas as pd
from datetime import datetime
import mysql.connector
import matplotlib.pyplot as plt
import calendar
import plotly.graph_objects as go 
import pickle
from pathlib import Path
import streamlit_authenticator

# Import des bibliothèques nécessaires pour le modèle de machine learning
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score



#image_path = st.image('C:\\Users\\lenovo\\Downloads\\.jpeg')

# ----------USER AUTHNTIFICTION ----------
names = ["Peter pParker", "Rebecca Miller"]
usernames = ["pparker", "rmiler"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file :
    hash






# Fonction pour établir la connexion à la base de données MySQL
def etablir_connexion():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sonatel"
    )
    return conn



# Fonction pour saisir les données sur les livrables
def saisie_donnees(conn):
    st.title("DASHBOARD OSF : Suivis et visualisation")
    with st.sidebar.expander("À propos de l'application"):
        st.markdown("**Description de l'application :**")
        st.info("Cette application permet de suivre les livrables d'un projet. Vous pouvez saisir les données sur les livrables, les enregistrer dans une base de données MySQL et visualiser les données pour un mois spécifique ou l'évolution du pourcentage de livrables réalisés dans les délais au fil des mois.")

    st.sidebar.markdown("**Fonctionnalités de l'application:**")
    st.sidebar.warning("- Saisir les données sur les livrables : Nom du livrable, porteur, périodicité, échéance et date de réalisation.")
    st.sidebar.warning("- Enregistrer les données dans une base de données MySQL.")
    st.sidebar.warning("- Visualiser les données pour un mois spécifique : Affichage des livrables et pourcentage de livrables réalisés dans les délais.")
    st.sidebar.warning("- Visualiser l'évolution du pourcentage de livrables réalisés dans les délais au fil des mois.")

    # Sélection du prestataire
    prestataire = st.selectbox("Sélectionner le prestataire", ["PCCI", "PPED", "PPI", "HV", "OE", "1413", "GVC", "WAY2CALL", "KSERV", "FOUNDEVER", "POSITION STANDARD"])

    st.subheader(f"Saisie des données pour le prestataire {prestataire}")
    nom_livrable = st.text_input("Nom du livrable")
    porteur = st.text_input("Porteur du livrable")
    periodicite = st.selectbox("Périodicité", ["Quotidien", "Hebdomadaire", "Mensuel", "Trimestriel", "Annuel"])
    echeance = st.date_input("Échéance du livrable")
    date_realisation = st.date_input("Date de réalisation du livrable", datetime.today())

    # Bouton pour enregistrer les données
    if st.button("Enregistrer"):
        sauvegarder_donnees_prestataire(conn, prestataire, nom_livrable, porteur, periodicite, echeance, date_realisation)
        st.success("Données sauvegardées avec succès !")
    
        # Calcul du délai
        delai_depassee = date_realisation > echeance

        # Affichage du statut du délai
        if delai_depassee:
            st.error("Le livrable a été réalisé après l'échéance.")
        else:
            st.success("Le livrable a été réalisé dans les délais.") 


# Fonction pour enregistrer les données dans la base de données MySQL pour un prestataire donné
def sauvegarder_donnees_prestataire(conn, prestataire, nom_livrable, porteur, periodicite, echeance, date_realisation):
    cursor = conn.cursor()
    
    # Vérifier si la table pour le prestataire existe, sinon la créer
    table_name = f"livrables_{prestataire}"
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    if not result:
        # Créer la table si elle n'existe pas
        cursor.execute(f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, nom_livrable VARCHAR(255), porteur VARCHAR(255), periodicite VARCHAR(50), echeance DATE, date_realisation DATE)")
    
    # Modifier la requête SQL en fonction du prestataire
    sql = f"INSERT INTO {table_name} (nom_livrable, porteur, periodicite, echeance, date_realisation) VALUES (%s, %s, %s, %s, %s)"
    values = (nom_livrable, porteur, periodicite, echeance, date_realisation)
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()

# Clé unique pour le widget selectbox de l'année
annee_key = "annee_selectbox"

def visualiser_donnees_par_prestataire(conn):
    st.title("DASHBOARD OSF : Suivis et visualisation")
    with st.sidebar.expander("À propos de l'application"):
        st.markdown("**Description de l'application :**")
        st.info("Cette application permet de suivre les livrables d'un projet. Vous pouvez saisir les données sur les livrables, les enregistrer dans une base de données MySQL et visualiser les données pour un mois spécifique ou l'évolution du pourcentage de livrables réalisés dans les délais au fil des mois.")

    st.sidebar.markdown("**Fonctionnalités de l'application:**")
    st.sidebar.warning("- Saisir les données sur les livrables : Nom du livrable, porteur, périodicité, échéance et date de réalisation.")
    st.sidebar.warning("- Enregistrer les données dans une base de données MySQL.")
    st.sidebar.warning("- Visualiser les données pour un mois spécifique : Affichage des livrables et pourcentage de livrables réalisés dans les délais.")
    st.sidebar.warning("- Visualiser l'évolution du pourcentage de livrables réalisés dans les délais au fil des mois.")

    st.subheader("Visualisation des données sur les livrables par prestataire")
    
    # Sélection du prestataire
    prestataire_selectionne = st.selectbox("Sélectionner le prestataire", ["PCCI", "PPED", "PPI", "HV", "OE", "1413", "GVC", "WAY2CALL", "KSERV", "FOUNDEVER", "POSITION STANDARD"])
    
    # Construction du nom de la table en fonction du prestataire sélectionné
    table_name = f"livrables_{prestataire_selectionne}"
    
    # Récupération des données pour le prestataire sélectionné
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    donnees_prestataire = cursor.fetchall()
    cursor.close()
    
    # Vérification des données récupérées
    print("Données pour le prestataire sélectionné :", donnees_prestataire)
    
    # Affichage des données
    if not donnees_prestataire:
        st.warning("Aucune donnée disponible pour le prestataire sélectionné.")
    else:
        df = pd.DataFrame(donnees_prestataire, columns=['id', 'nom_livrable', 'porteur', 'periodicite', 'echeance', 'date_realisation'])
        st.write("Données pour le prestataire sélectionné :")
        st.write(df)
        
        # Exclure les périodicités quotidiennes
        df = df[df['periodicite'] != 'Quotidienne']

    
        
        # Sélection de l'année
        annee_selectionnee = st.selectbox("Sélectionner l'année à visualiser", range(2022, 2025))

        # Sélection du mois à visualiser
        mois_selectionne = st.selectbox("Sélectionner le mois à visualiser", ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'])

        # Conversion du mois en index (de 1 à 12)
        mois_index = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'].index(mois_selectionne) + 1

        # Filtrer les données pour le mois sélectionné
        df['echeance'] = pd.to_datetime(df['echeance'])

        df_mois = df[(df['echeance'].dt.year == annee_selectionnee) & (df['echeance'].dt.month == mois_index)]

        # Calcul du pourcentage de délai pour le mois sélectionné
        total_livrables = len(df_mois)
        livrables_dans_les_delais = len(df_mois[df_mois['date_realisation'] <= df_mois['echeance']])
        if total_livrables == 0:
            st.warning("Aucun livrable trouvé pour le mois sélectionné.")
        else:
            pourcentage_delai = (livrables_dans_les_delais / total_livrables) * 100
            st.write(f"Pourcentage de livrables réalisés dans les délais pour le mois sélectionné : {pourcentage_delai:.2f}%")

        # Sélection du porteur
        porteurs_disponibles = df_mois['porteur'].unique()  # Liste des porteurs disponibles dans le mois sélectionné
        porteur_selectionne = st.selectbox("Sélectionner le porteur", porteurs_disponibles)

        # Filtrer les données pour le porteur sélectionné
        df_porteur = df_mois[df_mois['porteur'] == porteur_selectionne]

        # Calcul du pourcentage de délai pour le porteur sélectionné
        total_livrables_porteur = len(df_porteur)
        livrables_dans_les_delais_porteur = len(df_porteur[df_porteur['date_realisation'] <= df_porteur['echeance']])
        if total_livrables_porteur == 0:
            st.warning("Aucun livrable trouvé pour le porteur sélectionné.")
        else:
            pourcentage_delai_porteur = (livrables_dans_les_delais_porteur / total_livrables_porteur) * 100
            st.write(f"Pourcentage de livrables réalisés dans les délais pour le porteur sélectionné : {pourcentage_delai_porteur:.2f}%")

def visualiser_evolution_delai_par_prestataire(conn):
    st.subheader("Évolution du pourcentage de livrables réalisés dans les délais par prestataire")
    
    # Sélection du prestataire avec une clé unique
    prestataire_selectionne = st.selectbox("Sélectionner le prestataire", ["PCCI", "PPED", "PPI", "HV", "OE", "1413", "GVC", "WAY2CALL", "KSERV", "FOUNDEVER", "POSITION STANDARD"], key="prestataire_selectbox")
    
    # Construction du nom de la table en fonction du prestataire sélectionné
    table_name = f"livrables_{prestataire_selectionne}"
    
    # Sélection de l'année avec une clé unique
    annee_selectionnee = st.selectbox("Sélectionner l'année à visualiser", range(2022, 2025), key="annee_selectbox")
    
    # Récupération des données pour chaque mois de l'année sélectionnée
    cursor = conn.cursor()
    pourcentages = []
    mois_labels = []
    for mois in range(1, 13):
        cursor.execute(f"SELECT * FROM {table_name} WHERE YEAR(echeance) = %s AND MONTH(echeance) = %s", (annee_selectionnee, mois))
        donnees = cursor.fetchall()
        df_mois = pd.DataFrame(donnees, columns=['id', 'nom_livrable', 'porteur', 'periodicite', 'echeance', 'date_realisation'])
        total = len(df_mois)
        dans_les_delais = len(df_mois[df_mois['date_realisation'] <= df_mois['echeance']])
        if total == 0:
            pourcentages.append(0)
        else:
            pourcentages.append((dans_les_delais / total) * 100)
        mois_labels.append(calendar.month_abbr[mois])  # Convertir le numéro du mois en abréviation du mois

    # Création de la courbe avec Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mois_labels, y=pourcentages, mode='lines+markers'))
    fig.update_layout(title=f"Évolution du pourcentage de livrables réalisés dans les délais pour l'année {annee_selectionnee} (Prestataire : {prestataire_selectionne})",
                      xaxis_title='Mois', yaxis_title='Pourcentage de livrables réalisés dans les délais')
    st.plotly_chart(fig)



# Choix de l'utilisateur : saisie des données ou visualisation des données
option = st.sidebar.selectbox("Choisir une option", ["Saisir des données", "Visualiser les données"])

# Afficher la partie correspondante en fonction du choix de l'utilisateur
if option == "Saisir des données":
    conn = etablir_connexion()
    saisie_donnees(conn)
    conn.close()
else:
    conn = etablir_connexion()
    visualiser_donnees_par_prestataire(conn)
    visualiser_evolution_delai_par_prestataire(conn)
    conn.close()
