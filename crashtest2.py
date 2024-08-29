import streamlit as st
from bson import json_util, BSON  # PyMongo's BSON encoding and decoding functions
import json

bson_data = BSON.encode({
    "nom": "ChatGPT",
    "type": "Assistant IA",
    "caractéristiques": {
        "langues": ["Français", "Anglais", "Espagnol"],
        "modèle": "GPT-4",
        "version": 1.0
    },
    "actif": True
})


def main():
    st.title("Application Streamlit pour lire et modifier des fichiers BSON")

    # Lire les données BSON
    bson_dict = BSON.decode(bson_data)

    # Afficher le contenu BSON sous forme de texte
    st.header("Contenu BSON original")
    bson_pretty = json.dumps(bson_dict, indent=4, ensure_ascii=False)
    st.code(bson_pretty, language='json')

    # Permettre la modification des données BSON
    st.header("Modifier le BSON")
    modified_bson_str = st.text_area(
        "Éditez le BSON ici :", bson_pretty, height=300)

    if st.button("Sauvegarder les modifications"):
        try:
            # Convertir la chaîne modifiée en dictionnaire Python
            modified_bson_dict = json.loads(modified_bson_str)

            # Convertir en BSON et sauvegarder (simulé ici par une simple variable)
            modified_bson_data = BSON.encode(modified_bson_dict)

            # Afficher la confirmation
            st.success("Modifications sauvegardées avec succès !")

            # Afficher le contenu BSON modifié
            st.header("Contenu BSON modifié")
            st.code(json.dumps(modified_bson_dict, indent=4,
                    ensure_ascii=False), language='json')

        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde : {e}")


if __name__ == "__main__":
    main()
