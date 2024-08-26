import matplotlib.patches as patches
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt


def draw_top3(df: pd.DataFrame) -> plt.Figure:
    """ Draw a pie chart showing the favorite director, actor, and total films logged."""

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


def draw_top_countries(df: pd.DataFrame) -> go.Figure:
    """ Draw a horizontal bar chart showing the top 5 countries with the most films logged."""

    top_countries = df['country'].value_counts(
    ).sort_values(ascending=True).tail(5)

    colors = ['#FF8000', '#00E054', '#40BCF4', "#272F36"]

    # Create a color palette with a gradient
    # Since Plotly doesn't directly support gradient color palettes, we manually assign colors
    color_map = {country: colors[i % len(
        colors)] for i, country in enumerate(top_countries.index)}

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
            tickfont=dict(size=14),
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        # Adjust margins for better spacing
        margin=dict(t=50, l=100, r=25, b=50),
        height=800,
        width=1200,

    )

    return remove_plotly_menus(fig)


def draw_log_timeline(df: pd.DataFrame) -> go.Figure:
    """ Draw a bar chart showing the number of films logged over time since the user started logging."""

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


def draw_top_genres(df: pd.DataFrame) -> go.Figure:
    """ Draw a treemap showing the top 10 genres of films logged."""

    colors = ['#FF8000', '#00E054', '#40BCF4', "#272F36"]
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


def draw_rating_dist(df: pd.DataFrame) -> go.Figure:
    """ Draw a bar chart showing the distribution of film ratings."""

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


def draw_top_actors(df: pd.DataFrame) -> go.Figure:
    """ Draw a treemap showing the top 10 actors of films logged."""

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


def remove_plotly_menus(fig: go.Figure) -> go.Figure:
    """ Remove the plotly menus ( toolbar, hover, click, drag...) from a figure. """

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
