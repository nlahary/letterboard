import streamlit as st
import pandas as pd

# Titre de l'application
st.title("Application Streamlit avec Menu, Chargement de CSV et Sélection de Colonne")

# Création du menu dans la barre latérale
menu = ["Page 1", "Page 2"]
choix = st.sidebar.selectbox("Navigation", menu)

# Initialise st.session_state pour stocker le DataFrame et le nom de colonne si ce n'est pas déjà fait
if 'dataframe' not in st.session_state:
    st.session_state.dataframe = None
if 'selected_column' not in st.session_state:
    st.session_state.selected_column = None

# Affichage du contenu en fonction du choix de l'utilisateur
if choix == "Page 1":
    st.header("Bienvenue sur la Page 1")
    st.write("Ceci est le contenu de la première page.")
    # Ajoutez ici plus de contenu spécifique à la Page 1

elif choix == "Page 2":
    st.header("Bienvenue sur la Page 2")
    st.write("Ceci est le contenu de la deuxième page.")

    # Bouton pour charger le fichier CSV
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")

    # Si un fichier est téléchargé, lire le fichier et le stocker dans st.session_state
    if uploaded_file is not None:
        st.session_state.dataframe = pd.read_csv(uploaded_file)
        # Réinitialise la colonne sélectionnée après le chargement d'un nouveau fichier
        st.session_state.selected_column = None
        st.success("Fichier CSV chargé avec succès!")

    # Afficher le DataFrame si il est chargé
    if st.session_state.dataframe is not None:
        st.write("Voici le DataFrame chargé:")
        st.dataframe(st.session_state.dataframe)

        # Sélecteur pour choisir une colonne
        st.session_state.selected_column = st.selectbox(
            "Sélectionnez une colonne à afficher",
            st.session_state.dataframe.columns
        )

        # Afficher les valeurs de la colonne sélectionnée
        if st.session_state.selected_column:
            st.write(f"Valeurs de la colonne '{
                     st.session_state.selected_column}':")
            st.text("\n".join(
                map(str, st.session_state.dataframe[st.session_state.selected_column].tolist())))

    else:
        st.write("Aucun fichier CSV n'est encore chargé.")
