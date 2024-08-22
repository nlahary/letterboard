from itertools import combinations
import pandas as pd
from arcplot import ArcDiagram


df = pd.read_csv("letterboxd.csv")


df = df[["film", "actors"]]
df['actors'] = df['actors'].apply(lambda x: eval(x)[:5])

# Créer une liste pour stocker les paires d'acteurs et le film en commun
actor_pairs_with_film = []

# Générer toutes les combinaisons de paires d'acteurs pour chaque film et les associer au film
for index, row in df.iterrows():
    film = row['film']
    actors = row['actors']
    pairs = list(combinations(actors, 2))
    for pair in pairs:
        actor_pairs_with_film.append((pair[0], pair[1], film))

# Créer un dataframe temporaire avec les paires d'acteurs et les films
df_pairs = pd.DataFrame(actor_pairs_with_film, columns=[
                        'Actor 1', 'Actor 2', 'Film'])

# Compter le nombre de films en commun pour chaque paire d'acteurs
df_weight = df_pairs.groupby(
    ['Actor 1', 'Actor 2']).size().reset_index(name='Weight')

# Joindre les informations sur le poids avec les films en commun
df_final = pd.merge(df_pairs, df_weight, on=['Actor 1', 'Actor 2'])

# Afficher le dataframe final
print(df_final.sort_values(by='Weight', ascending=False).head())

# Créer un diagramme d'arc avec les paires d'acteurs et les poids pour weight > 1

df_final = df_final[df_final['Weight'] > 1]

nodes = list(set(df_final['Actor 1']).union(set(df_final['Actor 2'])))

title = "Arc Diagram of Actor Pairs in Films"

arc = ArcDiagram(nodes, title)


for connection in df_final.itertuples():
    arc.connect(connection._1, connection._2)

arc.set_label_rotation_degree(90)

ACTORS_N = len(set(df_final['Actor 1']).union(set(df_final['Actor 2'])))
COLORS = ['#FF8000', '#00E054', '#40BCF4', "#272F36"]

# Generate a list of colors of length ACTORS_N using the COLORS list
COLORS_LIST = COLORS * (ACTORS_N // len(COLORS)) + \
    COLORS[:ACTORS_N % len(COLORS)]

arc.set_custom_colors(COLORS_LIST)

# cmap = 'inferno'
# arc.set_color_map(cmap)

arc.show_plot()
