import streamlit as st
import pandas as pd
from pycaret.regression import setup, compare_models, save_model, plot_model

# Fonction pour charger les données
@st.cache
def load_data(file):
    data = pd.read_csv(file)
    return data

def main():
    st.title("Auto Machine Learning")

    # Sidebar
    st.sidebar.title("Paramètres")
    uploaded_file = st.sidebar.file_uploader("Uploader un fichier CSV", type=["csv"])

    # Chargement des données
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        st.write("Aperçu des données :")
        st.write(data.head())

        # Génération du profil des données
        if st.sidebar.button("Profiler les données"):
            st.write("Génération du profil des données ...")
            profile = data.profile_report()
            st_profile_report(profile)

        # Sélection de la variable cible et du type de tâche
        target = st.sidebar.selectbox("Sélectionner la variable cible", data.columns)
        task = st.sidebar.selectbox("Sélectionner la tâche ML", ["Régression", "Classification"])

        # Configuration et comparaison des modèles
        if st.sidebar.button("Lancer l'apprentissage"):
            st.write("Configuration des modèles ...")
            if task == "Régression":
                exo_reg = setup(data, target=target)
                model_reg = compare_models()
                save_model(model_reg, "Best_reg_model")
                st.success("Modèle de régression construit avec succès")

                # Affichage des résultats
                st.write("Graphique des résidus :")
                plot_model(model_reg, plot='residuals')
                st.write("Importance des variables :")
                plot_model(model_reg, plot='feature')

            elif task == "Classification":
                exo_class = setup(data, target=target)
                model_class = compare_models()
                save_model(model_class, "Best_class_model")
                st.success("Modèle de classification construit avec succès")

                # Affichage des résultats
                st.write("Courbe ROC :")
                plot_model(model_class)
                st.write("Rapport de classification :")
                plot_model(model_class, plot="class_report")

    else:
        st.warning("Veuillez uploader un fichier CSV pour commencer.")

if __name__ == '__main__':
    main()
