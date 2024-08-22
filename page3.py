import plotly.graph_objects as go
import pandas as pd
import numpy as np


def plot_sankey(df):
    df = df[["country", "primary_language"]]

    link_counts = df.groupby(
        ['country', 'primary_language']).size().reset_index(name='count')

    countries = link_counts['country'].unique()
    languages = link_counts['primary_language'].unique()

    # Créer un dictionnaire pour mapper les noms aux indices des noeuds
    node_mapping = {name: idx for idx, name in enumerate(
        list(countries) + list(languages))}

    # Créer les listes des indices source et cible pour les liens
    sources = [node_mapping[country] for country in link_counts['country']]
    targets = [node_mapping[language]
               for language in link_counts['primary_language']]
    values = link_counts['count']

    # Définir les couleurs pour chaque langue en format rgba
    language_colors = {
        language: color for language, color in zip(
            languages,
            [
                'rgba(0, 0, 255, 1)',  # blue
                'rgba(0, 128, 0, 1)',  # green
                'rgba(255, 0, 0, 1)',  # red
                'rgba(255, 165, 0, 1)',  # orange
                'rgba(128, 0, 128, 1)',  # purple
                'rgba(0, 255, 255, 1)',  # cyan
                'rgba(255, 0, 255, 1)',  # magenta
                'rgba(255, 255, 0, 1)'   # yellow
            ]
        )
    }

    # Créer une liste de couleurs pour les noeuds
    node_colors = ['grey' for _ in range(len(countries) + len(languages))]
    for language, idx in node_mapping.items():
        if language in language_colors:
            node_colors[idx] = language_colors[language]

    # Créer une liste de couleurs pour les liens avec une opacité de 0.4
    link_colors = []
    for target in targets:
        base_color = node_colors[target]
        rgba_color = base_color.replace(
            '1)', '0.4)')  # Changer l'opacité à 0.4
        link_colors.append(rgba_color)

    # Attribuer la couleur du lien avec le poids le plus grand à la source
    for country in countries:
        outgoing_indices = [i for i in range(
            len(sources)) if sources[i] == node_mapping[country]]
        if outgoing_indices:
            # Trouver l'indice du lien avec le poids maximum
            max_index = max(outgoing_indices, key=lambda i: values[i])
            # Utiliser la couleur de la target du lien avec le poids maximum pour la source
            node_colors[node_mapping[country]
                        ] = link_colors[max_index].replace('0.4)', '1)')

    # Créer le diagramme de Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,  # Augmenter l'espace entre les nœuds
            thickness=50,  # Augmenter l'épaisseur des nœuds
            line=dict(color='black', width=0.5),
            label=list(countries) + list(languages),
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])

    fig.update_layout(
        font_size=12,
        width=1200,
        height=800
    )

    return fig


if __name__ == "__main__":

    df = pd.read_csv('letterboxd.csv')
    fig = plot_sankey(df)
    fig.show()
