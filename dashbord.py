import streamlit as st
import pandas as pd
from datetime import datetime
import mysql.connector
import matplotlib.pyplot as plt
import calendar
import plotly.graph_objects as go
# Import des bibliothèques nécessaires pour le modèle de machine learning
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score


st.sidebar.title("Francis Raymond Edouard Sagna")
#image_path = st.image('C:\\Users\\lenovo\\Downloads\\.jpeg')

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

    file = st.sidebar.file_uploader("Televerser votre fichier sous format csv", type=["csv"])
    
    
    st.subheader("Saisie des données sur les livrables")
    nom_livrable = st.text_input("Nom du livrable")
    porteur = st.text_input("Porteur du livrable")
    periodicite = st.selectbox("Périodicité", ["Quotidien", "Hebdomadaire", "Mensuel", "Trimestriel", "Annuel"])
    echeance = st.date_input("Échéance du livrable")
    date_realisation = st.date_input("Date de réalisation du livrable", datetime.today())
    
    # Bouton pour enregistrer les données
    if st.button("Enregistrer"):
        sauvegarder_donnees(conn, nom_livrable, porteur, periodicite, echeance, date_realisation)
        st.success("Données sauvegardées avec succès !")
    
    # Calcul du délai
    delai_depassee = date_realisation > echeance

    # Affichage du statut du délai
    if delai_depassee:
        st.error("Le livrable a été réalisé après l'échéance.")
    else:
        st.success("Le livrable a été réalisé dans les délais.")  

# Fonction pour enregistrer les données dans la base de données MySQL
def sauvegarder_donnees(conn, nom_livrable, porteur, periodicite, echeance, date_realisation):
    cursor = conn.cursor()
    sql = "INSERT INTO livrables (nom_livrable, porteur, periodicite, echeance, date_realisation) VALUES (%s, %s, %s, %s, %s)"
    values = (nom_livrable, porteur, periodicite, echeance, date_realisation)
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()

# Clé unique pour le widget selectbox de l'année
annee_key = "annee_selectbox"

# Fonction pour visualiser les données pour un mois spécifique
def visualiser_donnees(conn):
    with st.sidebar.expander("À propos de l'application"):
        
        st.markdown("**Description de l'application :**")
        st.info("Cette application permet de suivre les livrables d'un projet. Vous pouvez saisir les données sur les livrables, les enregistrer dans une base de données MySQL et visualiser les données pour un mois spécifique ou l'évolution du pourcentage de livrables réalisés dans les délais au fil des mois.")

    st.sidebar.markdown("**Fonctionnalités de l'application:**")
    st.sidebar.warning("- Saisir les données sur les livrables : Nom du livrable, porteur, périodicité, échéance et date de réalisation.")
    st.sidebar.warning("- Enregistrer les données dans une base de données MySQL.")
    st.sidebar.warning("- Visualiser les données pour un mois spécifique : Affichage des livrables et pourcentage de livrables réalisés dans les délais.")
    st.sidebar.warning("- Visualiser l'évolution du pourcentage de livrables réalisés dans les délais au fil des mois.")

    
    st.subheader("Visualisation des données pour un mois spécifique")
    
    annee_selectionnee = st.selectbox("Sélectionner l'année à visualiser", range(2022, 2025), key=annee_key)
    
    # Sélection du mois
    mois_selectionne = st.selectbox("Sélectionner le mois à visualiser", ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'])
    # Afficher le résultat de la conversion du nom du mois en numéro
    #mois_index = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'].index(mois_selectionne)
    #mois_numéro = list(range(1,13))[mois_index]
    #st.write(f"Le numéro du mois sélectionné est : {mois_numéro}")
    cursor = conn.cursor()
    mois_index = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'].index(mois_selectionne)
    cursor.execute("SELECT * FROM livrables WHERE YEAR(echeance) = %s AND MONTH(echeance) = %s", (annee_selectionnee, mois_index + 1))
    donnees_mois = cursor.fetchall()
    
    
    
    # Vérification des données récupérées
    print("Données pour le mois sélectionné :", donnees_mois)
    
    # Gestion des cas spéciaux
    if not donnees_mois:
        st.warning("Aucune donnée disponible pour le mois sélectionné.")
    else:
        df = pd.DataFrame(donnees_mois, columns=['id', 'nom_livrable', 'porteur', 'periodicite', 'echeance', 'date_realisation'])
        st.write("Données pour le mois sélectionné :")
        st.write(df)
        total_livrables = len(df)
        livrables_dans_les_delais = len(df[df['date_realisation'] <= df['echeance']])
        if total_livrables == 0:
            st.warning("Aucun livrable trouvé pour le mois sélectionné.")
        else:
            pourcentage_delai = (livrables_dans_les_delais / total_livrables) * 100
            st.write(f"Pourcentage de livrables réalisés dans les délais pour le mois sélectionné : {pourcentage_delai:.2f}%")
            
            # Ajouter la colonne 'pourcentage_delai' au DataFrame
            df['pourcentage_delai'] = pourcentage_delai
            # Convertir les colonnes en datetime si elles ne le sont pas déjà
            df['date_realisation'] = pd.to_datetime(df['date_realisation'])
            df['echeance'] = pd.to_datetime(df['echeance'])

            # Calcul de la différence en jours entre la date d'échéance et la date de réalisation
            df['delai'] = (df['date_realisation'] - df['echeance']).dt.days

            # Séparation des données en ensemble d'entraînement et ensemble de test (80% - 20%)
            X = df[['delai']]  # Caractéristique (différence de jours)
            y = df['pourcentage_delai']  # Variable cible (pourcentage de retard)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Entraînement du modèle de régression linéaire
            model = LinearRegression()
            model.fit(X_train, y_train)

            # Faire des prédictions sur l'ensemble de test
            predictions = model.predict(X_test)

            # Évaluation des performances du modèle
            mae = mean_absolute_error(y_test, predictions)
            r2 = r2_score(y_test, predictions)

            # Affichage des résultats
            st.write(f"Erreur absolue moyenne (MAE) : {mae:.2f}")
            st.write(f"Coefficient de détermination (R²) : {r2:.2f}")

# Fonction pour visualiser l'évolution du pourcentage de livrables réalisés dans les délais
def visualiser_evolution_delai(conn):
    st.subheader("Évolution du pourcentage de livrables réalisés dans les délais")
    
    # Sélection de l'année
    annee_selectionnee = st.selectbox("Sélectionner l'année à visualiser", range(2022, 2025))
    
    # Récupération des données pour chaque mois de l'année sélectionnée
    cursor = conn.cursor()
    pourcentages = []
    mois_labels = []
    for mois in range(1, 13):
        cursor.execute("SELECT * FROM livrables WHERE YEAR(echeance) = %s AND MONTH(echeance) = %s", (annee_selectionnee, mois))
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
    fig.update_layout(title=f"Évolution du pourcentage de livrables réalisés dans les délais pour l'année {annee_selectionnee}",
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
    visualiser_donnees(conn)
    visualiser_evolution_delai(conn)
    conn.close()
