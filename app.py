import streamlit as st
import pandas as pd
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report

from pycaret.regression import setup as setup_reg
from pycaret.regression import compare_models as compare_models_reg
from pycaret.regression import save_model as save_model_reg
from pycaret.regression import plot_model as plot_model_reg

from pycaret.classification import setup as setup_class
from pycaret.classification import compare_models as compare_models_class
from pycaret.classification import save_model as save_model_class
from pycaret.classification import plot_model as plot_model_class

@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    return data
    

def main():
    
    # Page title
    st.set_page_config(page_title='ML Model Building', page_icon='🤖')
    st.title('🤖 ML Model Building')
    with st.expander('About this app'):
        st.markdown('**What can this app do?**')
        st.info( "this app is for exploratory Data Analysis and building machine learning model for regression and classification tasks;\n")
        st.markdown('**How to use the app?**')
        st.warning("1. Load your dataset file (csv file);\n"
        "2. Click on *Profile Dataset* button in order to generate the pandas profiling of the dataset;\n" 
        "3. Choose your target columns;\n"
        "4. Choose the machine learning task (Regression or classifaction);\n"
        "5. Click on *Run Modelling* in order to start the training process.\n \n"
        "When the model is built, you can view the results like the pipeline model, residual plot, ROC curve, Confusion Matrix, Feature importance, etc;\n"
        "\n6. Download the pipeline model in your local computer."
                )
    
    
    st.sidebar.write(" Auteur : Francis Raymond Edouard Sagna")
    st.sidebar.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
    st.sidebar.title("Paramètres")
    
    file = st.sidebar.file_uploader("Upload your dataset in csv format", type=["csv"])
    
    # Chargement des données
    if file is not None:
        data = load_data(file)
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
        
        data = data.dropna(subset=[target])
        
        # Configuration et comparaison des modèles
        if st.sidebar.button("Lancer l'apprentissage"):
            st.write("Configuration des modèles ...")
            if task == "Regression":
                if st.button("Run modelling"):
                    exo_reg = setup_reg(data, target=target)
                    model_reg = compare_models_reg()
            
                    if model_reg:
                        save_model_reg(model_reg,"Best_reg_model")
                        st.success("Regression model built successfully")

                        # Results
                        st.write("Residuals")
                        plot_model_reg(model_reg, plot='residuals', save=True)
                        st.image("Residuals.png")

                        st.write("Feature importance")
                        plot_model_reg(model_reg, plot='feature', save=True)
                        st.image("Feature importance.png")

                        # Download the model
                        with open("best_reg_model.pkl", "rb") as f :
                            st.download_button("Download pipeline Model", f, file_name="best_reg_model.pkl")
                    else:
                        st.error("No regression model found. Please check your data and try again.")
            if task =="Classification" :
                if st.button("Run modelling"):
            
                    exo_class = setup_class(data, target = target)
                    model_class = compare_models_class()
                    save_model_class(model_class,"Best_class_model")
                    st.success("Classification model built successfully")
                    
                    # Results
                    col5, col6 = st.columns(2)
                    with col5 :
                        st.write("ROC curve")
                        plot_model_class(model_class, save=True)
                        st.image("AUC.png")
                        
                    with col6 :
                        st.write("Classification Report")
                        plot_model_class(model_class, plot="class_report", save=True)
                        st.image("Class Report.png")

                    col7, col8 = st.columns(2)
                    
                    with col7 :
                        st.write("Confusion Matrix")
                        plot_model_class(model_class, plot= "confusion matrix", save=True)
                        st.image("Confusion Matrix.png")
                    
                    with col8 :
                        st.write("Feature importance")
                        plot_model_class(model_class, plot= 'feature', save=True)
                        st.image("Feature importance.png")
                        
                    # Download the model
                    with open("best_class_model.pkl", "rb") as f :
                        st.download_button("Download model", f, file_name="best_class_model.pkl")
    else :
        st.warning('👈 Upload a CSV file')
        image = st.image('C:\\Users\\lenovo\\Downloads\\robot.jpg')
    
        # Charger et afficher la vidéo
        #video_path = "C:\\Users\\lenovo\\Downloads\\dystopian-midtown-stray-moewalls-com.mp4"
        #st.video(video_path, start_time=0)    
            
                    
if __name__== '__main__':
        main()