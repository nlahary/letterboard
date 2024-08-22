import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Fonction pour calculer la couleur moyenne des liens partant d'une source


def plot_sankey(df):
    def average_color(colors):
        rgb_colors = []
        for c in colors:
            if c.startswith('rgba'):
                rgba = c.replace('rgba(', '').replace(')', '').split(',')
                rgb = tuple(map(int, rgba[:3]))  # Convertir en tuple (R, G, B)
                rgb_colors.append(rgb)

        if not rgb_colors:
            return 'grey'

        # Calculer la couleur moyenne
        avg_color = tuple(np.mean(rgb_colors, axis=0).astype(int))
        return f'rgba({avg_color[0]}, {avg_color[1]}, {avg_color[2]}, 1)'

    df = df[["country", "primary_language"]]

    link_counts = df.groupby(['country', 'primary_language']
                             ).size().reset_index(name='count')

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

    # Calculer les couleurs moyennes pour les pays en fonction des couleurs des cibles (targets) auxquelles ils sont liés
    for country in countries:
        outgoing_targets = [targets[i] for i in range(
            len(sources)) if sources[i] == node_mapping[country]]
        outgoing_colors = [node_colors[target] for target in outgoing_targets]
        if outgoing_colors:
            node_colors[node_mapping[country]] = average_color(outgoing_colors)

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
        title_text="Sankey Diagram of Countries to Languages",
        font_size=12,
        width=1200,
        height=800
    )

    return fig
