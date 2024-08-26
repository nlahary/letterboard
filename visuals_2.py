import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from textwrap import wrap


def draw_studios_radar(df) -> plt.Figure:
    """ Draw a radar chart showing the favorite studios of films logged.
        Legend :
        - The size of the bars represents the average of the ratings given by the user for the movies from each studio.
        - The white dots represent the average rating of the average rating of the movies on letterbox from each studio.
        - The color gradient represents the number of movies the user has watched from each studio.
    """

    studios = df['studio'].value_counts().nlargest(10)
    studio_ratings = df.groupby('studio')['rating'].mean().loc[studios.index]
    studio_counts = df['studio'].value_counts().loc[studios.index]
    studio_avg_ratings = df.groupby(
        'studio')['average_rating'].mean().loc[studios.index]

    df_studios = pd.DataFrame(
        {'rating': studio_ratings, 'counts': studio_counts, 'avg_rating': studio_avg_ratings})

    MOVIES_N = df_studios['counts'].values

    COLORS = ["#DAF7A6", "#FFC300", "#FF5733", "#C70039", "#900C3F", "#581845"]
    # Create a colormap for the number of movies
    cmap = LinearSegmentedColormap.from_list(
        'custom', COLORS, N=len(df_studios))

    norm = mpl.colors.Normalize(vmin=MOVIES_N.min(), vmax=MOVIES_N.max())
    COLORS = cmap(norm(MOVIES_N))

    # Adjust the width of the bars to avoid overlap
    bar_width = 2 * np.pi / len(df_studios) * 0.8

    ANGLES = np.linspace(0, 2 * np.pi, len(df_studios),
                         endpoint=False).tolist()

    RATINGS = df_studios['rating'].tolist()
    AVG_RATINGS = df_studios['avg_rating'].tolist()
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    fig.patch.set_facecolor('#0E1117')
    ax.patch.set_facecolor('none')

    ax.set_theta_offset(1/2*np.pi / 2)
    ax.set_ylim(0, 5)

    # Color radial grids in white
    ax.grid(color='white')

    # Use the bar width in the ax.bar function
    bars = ax.bar(ANGLES, RATINGS, color=COLORS, linewidth=0, width=bar_width)
    ax.vlines(ANGLES, 0, 5, colors='white', ls=(
        0, (4, 4)), zorder=11, alpha=0.5)
    ax.scatter(ANGLES, AVG_RATINGS, color='white', s=100,
               zorder=10, alpha=0.8, edgecolors='black', linewidth=1)

    # Annotate bars with the number of movies
    # for bar, count in zip(bars, MOVIES_N):
    #     height = bar.get_height()
    #     ax.text(bar.get_x() + bar.get_width() / 2, height * 2/3, str(count),
    #             ha='center', va='center', color='black', fontsize=12,)

    # Hide the last circle
    ax.spines['polar'].set_visible(False)

    STUDIOS = ["\n".join(wrap(studio, 10, break_long_words=False))
               for studio in df_studios.index]

    ax.set_xticks(ANGLES)
    ax.set_xticklabels(STUDIOS, fontsize=10, fontweight='bold', color='white')

    # Ensure radial grids are white and visible
    ax.yaxis.grid(True, color='white', linestyle='-', linewidth=1)
    ax.xaxis.grid(False)

    ax.tick_params(axis='x', colors='white', labelsize=13)
    ax.tick_params(axis='y', colors='white', labelsize=15)

    XTICKS = ax.xaxis.get_major_ticks()
    for tick in XTICKS:
        tick.set_pad(30)

    plt.setp(ax.get_yticklabels(), color='white')

    # Color gradient legend to represent the number of movies
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))

    ax_inset = inset_axes(ax, width="50%", height="3%", loc='lower center',
                          bbox_to_anchor=(0, -0.3, 1, 1),
                          bbox_transform=ax.transAxes, borderpad=0)

    ax_inset.imshow(gradient, aspect='auto', cmap=cmap)
    ax_inset.set_xticks([])
    ax_inset.set_yticks([])
    ax_inset.set_frame_on(False)

    min_count = MOVIES_N.min()
    max_count = MOVIES_N.max()
    mid_count = (min_count + max_count) // 2

    # Position labels
    ax_inset.text(0, 1.5, str(min_count), color='white',
                  fontsize=13, ha='center', va='center', transform=ax_inset.transAxes)
    ax_inset.text(0.5, 1.5, str(mid_count), color='white', fontsize=13,
                  ha='center', va='center', transform=ax_inset.transAxes)
    ax_inset.text(1, 1.5, str(max_count), color='white', fontsize=13,
                  ha='center', va='center', transform=ax_inset.transAxes)

    # Title of the gradient legend
    ax_inset.text(0.5, -2, 'Number of Movies', color='white',
                  fontsize=15, ha='center', va='center', transform=ax_inset.transAxes, fontstyle='italic')

    title = "Your Favorite Studios"
    subtitle = """

    The size of the bars represents the average of your ratings for the movies from each studio.
    The white dots represent the average rating of the movies from each studio.
    The color gradient   represents the number of movies you have watched from each studio.

    Inspired by the work of [Tobias Stadler](https://tobias-stalder.netlify.app/dataviz/) & [Tomás Capretto](https://tomicapretto.com/)
    """

    return fig, title, subtitle


def draw_decades_radar(df) -> plt.Figure:
    """ Draw a radar chart showing the favorite decades of films logged. (Top 8)"""

    df["decade"] = df["date"] // 10 * 10

    decade_counts = df["decade"].value_counts().sort_index().nlargest(8)
    YEARS = decade_counts.index.tolist()
    MOVIES_N = decade_counts.values.tolist()

    ANGLES = np.linspace(0, 2 * np.pi, len(YEARS), endpoint=False).tolist()

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    for i in range(len(YEARS)):
        ax.plot([ANGLES[i], ANGLES[i]], [0, MOVIES_N[i]],
                color='orange', linewidth=2)
        ax.scatter(ANGLES[i], MOVIES_N[i],
                   color='orange', s=100)

    # Extra circle for the maximum number of movies watched during a decade
    max_movies_n = max(MOVIES_N)
    ax.plot(np.linspace(0, 2 * np.pi, 100),
            [max_movies_n] * 100, linestyle='--', color='#f4e60b', linewidth=1)
    ax.text(1, max_movies_n + 5,
            f'{max_movies_n}', color='#f4e60b',
            fontsize=10, ha='center')

    fig.patch.set_facecolor('#0E1117')
    ax.patch.set_facecolor('none')

    ax.set_ylim(0, max(MOVIES_N) + 15)

    ticks = np.quantile(MOVIES_N, np.linspace(0, 1, 5))
    # Round the ticks to the nearest decade. For example, 23 -> 20, 3 -> 0, 7 -> 10
    ticks = np.round(ticks, -1).astype(int)

    ax.set_yticks(ticks)
    ax.set_yticklabels(ticks, color='white', size=10)

    ax.set_xticklabels(YEARS, size=15, color='white')

    # Set the padding between the ticks and the decade labels
    XTICKS = ax.xaxis.get_major_ticks()
    for tick in XTICKS:
        tick.set_pad(15)

    title = "Your Favorite Decades"
    subtitle = " The radar chart below shows the number of movies you have watched per decade (Top 8).\n"

    return fig, title, subtitle


def draw_lang_sankey(df) -> go.Figure:
    """ Create a Sankey diagram showing the distribution of languages spoken in the movies 
        the user has watched by the country of origin of the movies. 
    """

    df = df[["country", "primary_language"]]

    link_counts = df.groupby(
        ['country', 'primary_language']).size().reset_index(name='count')

    countries = link_counts['country'].unique()
    languages = link_counts['primary_language'].unique()

    # Create a mapping of the nodes to their indices : {node_name: node_index}
    node_mapping = {name: idx for idx, name in enumerate(
        list(countries) + list(languages))}

    # Create a list of sources, targets, and values for the Sankey diagram
    sources = [node_mapping[country] for country in link_counts['country']]
    targets = [node_mapping[language]
               for language in link_counts['primary_language']]
    values = link_counts['count']

    language_colors = {
        language: color for language, color in zip(
            languages,
            [
                'rgba(0, 128, 0, 1)',    # green
                'rgba(255, 0, 0, 1)',    # red
                'rgba(255, 165, 0, 1)',  # orange
                'rgba(128, 0, 128, 1)',  # purple
                'rgba(0, 255, 255, 1)',  # cyan
                'rgba(255, 0, 255, 1)',  # magenta
                'rgba(255, 255, 0, 1)',  # yellow
                'rgba(128, 128, 128, 1)',  # gray
                'rgba(0, 100, 0, 1)',    # dark green
                'rgba(255, 20, 147, 1)',  # deep pink
                'rgba(75, 0, 130, 1)',   # indigo
                'rgba(255, 69, 0, 1)',   # orange red
                'rgba(139, 0, 139, 1)',  # dark magenta
                'rgba(255, 105, 180, 1)',  # hot pink
                'rgba(0, 255, 127, 1)',  # spring green
                'rgba(255, 140, 0, 1)',  # dark orange
                'rgba(85, 107, 47, 1)',  # dark olive green
                'rgba(255, 182, 193, 1)',  # light pink
                'rgba(46, 139, 87, 1)',  # sea green
                'rgba(255, 215, 0, 1)',  # gold
                'rgba(0, 206, 209, 1)',  # dark turquoise
                'rgba(147, 112, 219, 1)'  # medium purple
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
            pad=200,  # Augmenter l'espace entre les nœuds
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
        height=1200
    )

    title = "Does the country of the movies always make movies of the same language?"
    subtitle = """
    The Sankey diagram below shows the distribution of the languages spoken in the movies you have watched
    by the country of origin of the movies.
    The color of the links represents the language spoken in the movie.
    The width of the links represents the number of movies using that language.
    """
    return fig, title, subtitle


if __name__ == "__main__":

    df = pd.read_csv('letterboxd.csv')
    fig = draw_lang_sankey(df)
    fig.show()
