import streamlit as st
from bson import json_util, decode_all, encode
import json

# Exemple de données BSON brutes codées en dur (sous forme de bytes)

bson_data = encode({
    "nom": "ChatGPT",
    "type": "Assistant IA",
    "caractéristiques": {
        "langues": ["Français", "Anglais", "Espagnol"],
        "modèle": "GPT-4",
        "version": 1.0
    },
    "actif": True
})


def main(bson_data=bson_data):
    st.title("Application Streamlit pour lire et modifier des fichiers BSON")

    # Lire les données BSON
    bson_dict = decode_all(bson_data)[0]

    # Utiliser une variable d'état pour suivre le mode (vue ou édition)
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    if st.session_state.edit_mode:
        # Mode édition
        st.header("Modifier le BSON")
        bson_pretty = json.dumps(bson_dict, indent=4, ensure_ascii=False)
        modified_bson_str = st.text_area(
            "Éditez le BSON ici :", bson_pretty, height=300)

        if st.button("Sauvegarder"):
            try:
                # Convertir la chaîne modifiée en dictionnaire Python
                modified_bson_dict = json.loads(modified_bson_str)

                # Convertir en BSON et sauvegarder (simulé ici par une simple variable)
                bson_data = encode(modified_bson_dict)

                # Mise à jour de l'état pour sortir du mode édition
                st.session_state.edit_mode = False

                # Afficher la confirmation
                st.success("Modifications sauvegardées avec succès !")
                st.rerun()
                # Rafraîchir la page pour afficher les données mises à jour
            except Exception as e:
                st.error(f"Erreur lors de la sauvegarde : {e}")

    else:
        # Mode vue
        st.header("Contenu BSON")
        bson_pretty = json.dumps(bson_dict, indent=4, ensure_ascii=False)
        st.code(bson_pretty, language='json')

        if st.button("Modifier"):
            # Passer en mode édition
            st.session_state.edit_mode = True
            st.rerun()


if __name__ == "__main__":
    main(bson_data=bson_data)
