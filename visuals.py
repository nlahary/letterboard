from matplotlib import pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from textwrap import wrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize, hex2color
from textwrap import wrap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def draw_top3(df):

    total_films = df.shape[0]
    favorite_director = df['director'].mode().values[0]
    favorite_actor = df['actors'].explode().mode().values[0]

    if len(favorite_director) > 13:
        favorite_director = "\n"+favorite_director.replace(" ", "\n")

    if len(favorite_actor) > 13:
        favorite_actor = "\n"+favorite_actor.replace(" ", "\n")

    colors = ['#FF8000', '#00E054', '#40BCF4']

    fig, ax = plt.subplots()
    fig.patch.set_facecolor('#0E1117')
    ax.patch.set_facecolor('none')

    circles = [
        {'center': (1, 1), 'radius': 0.5, 'color': colors[0],
            'text': f'\n {total_films}',
            'subtext': 'Total Films Logged:',
            'text_font_size': 10},

        {'center': (1.9, 1), 'radius': 0.5, 'color': colors[1],
            'text': f'\n {favorite_director}',
            'subtext': 'Favorite Director:',
            'text_font_size': 10},
        {'center': (2.8, 1), 'radius': 0.5, 'color': colors[2],
            'text': f'\n {favorite_actor}',
            'subtext': 'Favorite Actor:',
            'text_font_size': 10}
    ]

    for circle in circles:
        ax.add_patch(patches.Circle(
            circle['center'], circle['radius'], color=circle['color'], alpha=0.5))

        ax.text(circle['center'][0], circle['center'][1], circle['text'],
                ha='center', va='center', color='white', weight='bold', fontsize=circle['text_font_size'])

        ax.text(circle['center'][0], circle['center'][1] + 0.1, circle['subtext'],
                ha='center', va='center', fontsize=8, color='white', style='oblique')

    ax.set_aspect('equal')

    plt.xlim(0.25, 3.5)
    plt.ylim(0, 2)
    plt.axis('off')

    return fig


def fav_countries(df):
    # Get the value counts of countries and select only the top 10
    top_countries = df['country'].value_counts(
    ).sort_values(ascending=True).tail(5)

    # Define the colors for the gradient
    colors = ['#FF8000', '#00E054', '#40BCF4', "#272F36"]

    # Create a color palette with a gradient
    # Since Plotly doesn't directly support gradient color palettes, we manually assign colors
    color_map = {country: colors[i % len(
        colors)] for i, country in enumerate(top_countries.index)}

    # Create the horizontal bar plot using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=top_countries.values,
        y=top_countries.index,
        orientation='h',
        marker=dict(
            color=[color_map[country]
                   for country in top_countries.index],
            # Thin black border around bars
            line=dict(color='black', width=1)
        ),
        text=[f'{value}' for value in top_countries.values],
        textposition='outside',
        width=0.5  # Keep bar width unchanged to avoid altering spacing
    ))

    # Update the layout to customize appearance and disable interactivity
    fig.update_layout(
        title="Distribution of Films by Country (Top 10)",
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(
            showline=False,
            showgrid=False,
            showticklabels=False
        ),
        yaxis=dict(
            showline=False,
            showgrid=False,
            showticklabels=True,
            # Increase the size of the y-axis tick labels
            tickfont=dict(size=14),
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        # Adjust margins for better spacing
        margin=dict(t=50, l=100, r=25, b=50),
        height=800,  # Increase the height of the figure
        width=1200,  # Increase the width of the figure

    )

    return remove_plotly_menus(fig)


def draw_log_timeline(df):
    colors = ['#FF8000', '#00E054', '#40BCF4', "#272F36"]
    df['log_date'] = pd.to_datetime(df['log_date'])
    df['year_month'] = df['log_date'].dt.to_period('M').astype(str)

    log_counts = df.groupby(
        ['year_month']).size().reset_index(name='counts')

    fig = go.Figure(data=[
        go.Bar(
            x=log_counts['year_month'],
            y=log_counts['counts'],
            marker=dict(
                color=log_counts['counts'], colorscale=colors)
        )
    ])

    fig.update_layout(
        title="Your Film Logs Over Time",
        xaxis_title="",
        yaxis_title="Number of Logs",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black'),
        xaxis_tickangle=-45,
        height=600,
        # width=900,
    )

    fig.update_traces(
        hoverinfo='none',  # Disable hoverinfo
        selector=dict(type='bar')
    )

    fig.update_layout(
        # Remove specific buttons from the toolbar
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True),
        modebar_remove=['zoom', 'pan', 'select',
                        'lasso', 'resetScale2d', 'resetViews'],
        clickmode='none',
        hovermode=False,
        dragmode=False,
    )

    return remove_plotly_menus(fig)


def fav_genres(df):
    colors = ['#FF8000', '#00E054', '#40BCF4', "#272F36"]
    # Get the value counts of genres and select only the top 10
    genres = df['genres'].explode().value_counts().nlargest(10)

    # Create the treemap figure using go.Treemap
    fig = go.Figure(go.Treemap(
        labels=genres.index,          # Genre names
        # Empty string as all items are root nodes
        parents=[""] * len(genres),
        values=genres.values,         # Corresponding values
        marker=dict(colors=genres.values,
                    colorscale=colors),  # Color settings
        textinfo="label+value"        # Display label and value on the treemap
    ))

    # Update the layout to customize appearance and disable the legend
    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        title_font_size=20,
        showlegend=False,  # Ensure the legend is disabled
        title="Your Most Watched Genres (Top 10)",
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        # Transparent plot background
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black')        # Font color for labels
    )

    return remove_plotly_menus(fig)


def draw_rating_hist(df):
    df['rating'] = df['rating'].astype(float) / 2

    # Define the bins and labels
    bins = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5]
    bin_labels = ["0.5", "1", "1.5", "2",
                  "2.5", "3", "3.5", "4", "4.5", "5"]

    # Compute the histogram
    hist, _ = np.histogram(df['rating'], bins=bins)

    # Create the bar plot
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=bin_labels,
        y=hist,
        marker=dict(color='#FF8000'),
        text=[f'{count}' for count in hist],
        textposition='outside'
    ))

    # Update layout for better appearance
    fig.update_layout(
        xaxis=dict(
            showline=False,
            showgrid=False,
            showticklabels=True,
            ticks='outside',
            tickmode='array',
            tickvals=[0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
            ticktext=["0.5", "1", "1.5", "2",
                      "2.5", "3", "3.5", "4", "4.5", "5"],
            tickfont=dict(
                family="Arial",
                size=14,
                color="white"
            ),
            tickangle=0,
            automargin=True,

        ),
        yaxis=dict(
            showline=False,
            showgrid=True,
            showticklabels=True,
            ticks='outside'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, l=50, r=50, b=50),
        height=600,
        width=900,
        title='Distribution of Film Ratings',
        title_font_size=20
    )
    return remove_plotly_menus(fig)


def fav_actors(df):
    colors = ['#FF8000', '#00E054', '#40BCF4', "#272F36"]
    actors = df['actors'].explode().value_counts().nlargest(10)

    # Create the treemap figure using go.Treemap
    fig = go.Figure(go.Treemap(
        labels=actors.index,          # Actor names
        # Empty string as all items are root nodes
        parents=[""] * len(actors),
        values=actors.values,         # Corresponding values
        marker=dict(colors=actors.values,
                    colorscale=colors),  # Color settings
        textinfo="label+value"        # Display label and value on the treemap
    ))

    # Update the layout to customize appearance and disable the legend
    fig.update_layout(
        clickmode='none',
        hovermode=False,
        dragmode=False,
        margin=dict(t=50, l=25, r=25, b=25),
        title_font_size=20,
        showlegend=False,  # Ensure the legend is disabled
        title="Your Most Watched Actors (Top 10)",
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        # Transparent plot background
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black')        # Font color for labels
    )

    return fig


def fav_studios(df):
    # Get the value counts of studios and select the top 3
    top_studios = df['studio'].value_counts().nlargest(10)

    # Define colors for the donut chart
    colors = ['#FF8000', '#00E054', '#40BCF4']

    # Create the donut chart
    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=top_studios.index,
        values=top_studios.values,
        hole=0.4,  # Make it a donut chart
        marker=dict(
            colors=colors
        ),
        textinfo='label',
        # Change font size based on string length
        textfont=dict(
            size=[20 if len(label) <= 10 else
                  15 if len(label) <= 15 else 10
                  for label in top_studios.index],


            color='black'),
    ))

    # Update layout for better appearance
    fig.update_layout(
        title='Your 10 Favorite Studios',
        title_font_size=20,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=600,
        width=900,
        margin=dict(t=50, l=50, r=50, b=50),
        legend=dict(
            x=0.8,
            y=0.5,
            title='Studios',
            # Correctly specified as an integer
            title_font=dict(size=13),
        ),
    )

    return remove_plotly_menus(fig)


def radar_plot(df):
    studios = df['studio'].value_counts().nlargest(10)
    studio_ratings = df.groupby('studio')['rating'].mean().loc[studios.index]
    studio_counts = df['studio'].value_counts().loc[studios.index]
    studio_avg_ratings = df.groupby(
        'studio')['average_rating'].mean().loc[studios.index]

    df_studios = pd.DataFrame(
        {'rating': studio_ratings, 'counts': studio_counts, 'avg_rating': studio_avg_ratings})

    MOVIES_N = df_studios['counts'].values

    # Create a colormap for the number of movies
    cmap = LinearSegmentedColormap.from_list(
        'custom', [hex2color('#FF8000'), hex2color('#00E054')])

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
    ax.scatter(ANGLES, AVG_RATINGS, color='white', s=100, zorder=10)

    # Annotate bars with the number of movies
    for bar, count in zip(bars, MOVIES_N):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height * 2/3, str(count),
                ha='center', va='center', color='black', fontsize=12,)

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

    return fig


def draw_radar_decades(df):

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

    return fig


def remove_plotly_menus(fig):

    return fig.update_layout(
        # Supprimer des boutons spécifiques de la barre d'outils
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True),
        modebar_remove=['zoom', 'pan', 'select', 'lasso', 'resetScale2d',
                        'resetViews', 'toggleSpikelines', 'autoScale2d'],

        clickmode='none',
        hovermode=False,
        dragmode=False,
        showlegend=False
    )
