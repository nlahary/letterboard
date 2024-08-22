from selectolax.parser import HTMLParser
import httpx
import asyncio
import pandas as pd
from time import time
from concurrent.futures import ThreadPoolExecutor
import backoff
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib.patches as patches

from page3 import plot_sankey
from visuals import draw_radar_decades, draw_top3, fav_countries, draw_log_timeline, fav_genres, draw_rating_hist, fav_actors, fav_studios, radar_plot
# from page2 import


def get_total_pages(username: str) -> int:
    url = f"https://letterboxd.com/{username}/films/diary/"

    response = httpx.get(url, verify=False)
    response.raise_for_status()

    parser = HTMLParser(response.text)
    pages = parser.css("li.paginate-page")

    if pages:
        max_pages = int(pages[-1].text())
        return max_pages

    return 1


@backoff.on_exception(backoff.expo, (httpx.HTTPStatusError, httpx.RequestError), max_tries=5, jitter=None)
async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    """ Fetch a single page of the diary asynchronously """
    response = await client.get(url, timeout=10.0, )
    response.raise_for_status()
    return response.text


def parse_content(content: str) -> pd.DataFrame:
    """ Parse the content of the diary page and return a DataFrame """
    parser = HTMLParser(content)

    films = parser.css("a[rel='nofollow']")

    films_names = [film.attrs["data-film-name"] for film in films]
    films_ratings = [film.attrs["data-rating"] for film in films]
    films_years = [int(film.attrs["data-film-year"]) if film.attrs["data-film-year"] else pd.NA
                   for film in films]

    films_liked = [film.attrs["data-liked"] for film in films]
    films_log_date = [film.attrs["data-viewing-date"] for film in films]
    films_urls = [
        film.attrs["data-film-poster"].replace("image-150/", "") for film in films]

    return pd.DataFrame(
        {"film": films_names, "rating": films_ratings, "date": films_years,
            "liked": films_liked, "log_date": films_log_date, "url": films_urls}
    )


async def fetch_film_details(client: httpx.AsyncClient, film_url: str, executor: ThreadPoolExecutor) -> dict:
    """ Fetch the details of a single film asynchronously """
    full_url = f"https://letterboxd.com{film_url}"
    content = await fetch_page(client, full_url)

    # Parse the film details in a separate thread
    loop = asyncio.get_event_loop()
    details = await loop.run_in_executor(executor, parse_film_details, content)

    return details


def parse_film_details(content: str) -> dict:
    """ Parse the film details from the film page """
    parser = HTMLParser(content)

    country = parser.css_first("a[href*='/films/country/']").text(
    ) if parser.css_first("a[href*='/films/country/']") else None
    studio = parser.css_first(
        "a[href*='/studio/']").text() if parser.css_first("a[href*='/studio/']") else None
    primary_language = parser.css_first("a[href*='/films/language/']").text(
    ) if parser.css_first("a[href*='/films/language/']") else None

    genres = parser.css(
        "a[href*='/films/genre/']") if parser.css("a[href*='/films/genre/']") else None
    genres = [genre.text() for genre in genres] if genres else []

    director = parser.css_first(
        "a[href*='/director/']").text() if parser.css_first("a[href*='/director/']") else None

    actors = parser.css("a[href*='/actor/']") if parser.css(
        "a[href*='/actor/']") else None
    actors = [actor.text() for actor in actors] if actors else []

    running_time = parser.css_first("p[class*='text-link']").text() if parser.css_first(
        "p[class*='text-link']") else None
    running_time = [char for char in running_time.split()[0]
                    if char.isdigit()] if running_time else None
    running_time = int("".join(map(str, running_time))
                       ) if running_time else None

    # get "content" attribute value from meta tag whose name is "twitter:data2"
    average_rating = parser.css_first(
        "meta[name='twitter:data2']").attrs["content"] if parser.css_first("meta[name='twitter:data2']") else None
    average_rating = float(average_rating.split(
        " ")[0]) if average_rating else None
    return {
        "country": country,
        "studio": studio,
        "primary_language": primary_language,
        "genres": genres,
        "director": director,
        "actors": actors,
        "running_time": running_time,
        "average_rating": average_rating
    }


async def fetch_data(client: httpx.AsyncClient, username: str, page: int, executor: ThreadPoolExecutor) -> pd.DataFrame:
    """ Fetch the data for a single page of the diary """
    url = f"https://letterboxd.com/{username}/films/diary/page/{page}/"
    content = await fetch_page(client, url)

    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(executor, parse_content, content)

    # Fetch film details for each film on the page
    film_details_tasks = [
        fetch_film_details(client, film_url, executor)
        for film_url in df["url"]
    ]
    details_list = await asyncio.gather(*film_details_tasks, return_exceptions=True)

    details_df = pd.DataFrame(details_list)
    combined_df = pd.concat([df, details_df], axis=1)
    return combined_df.dropna()


async def main(username: str, total_pages: int) -> pd.DataFrame:
    async with httpx.AsyncClient() as client:
        with ThreadPoolExecutor() as executor:
            tasks = [fetch_data(client, username, page, executor)
                     for page in range(1, total_pages + 1)]
            results = await asyncio.gather(*tasks)

    return pd.concat(results, ignore_index=True)


def run_app():

    st.title("Letterboard : Your Letterboxd Diary Analysis",)

    st.markdown(
        """
        Welcome to Letterboard! This app allows you to analyze your Letterboxd diary and discover interesting insights about your film-watching habits.
        Enter your Letterboxd username below and click the 'Fetch Diary' button to get started.

        Inspired by the work of Favour O. ([Link to GitHub](https://github.com/afoshiok/Letterboard))

        Made by [Nathanaël L.]
        """
    )

    username = st.text_input("Enter your Letterboxd username:").strip()

    if st.button("Fetch Diary"):
        if username:
            try:
                total_pages = get_total_pages(username)
            except httpx.HTTPStatusError as e:
                st.error(
                    f"User '{username}' not found. Please check the username and try again.")
                return

            with st.spinner("Fetching data..."):
                try:
                    df = asyncio.run(main(username, total_pages))

                except AttributeError as e:
                    if "PoolTimeoutError" in str(e):
                        st.error("The request timed out. Please try again.")
                        return

                tab_level1, tab_level2 = st.tabs(
                    ["Level.1", "Level.2"])

                with tab_level1:
                    try:
                        fig = draw_top3(df)
                        st.pyplot(fig)

                        fig = fav_countries(df)
                        st.plotly_chart(fig)

                        fig = draw_log_timeline(df)
                        st.plotly_chart(fig)

                        fig = fav_genres(df)
                        st.plotly_chart(fig)

                        fig = draw_rating_hist(df)
                        st.plotly_chart(fig)

                        fig = fav_actors(df)
                        st.plotly_chart(fig)
                    except UnboundLocalError:
                        st.error(
                            f"Timeout error. Please try again or check your internet connection.")
                        return

                with tab_level2:
                    fig = radar_plot(df)

                    title = "Your Favorite Studios"
                    subtitle = """

                    The size of the bars represents the average of your ratings for the movies from each studio.
                    The white dots represent the average rating of the movies from each studio.
                    The color gradient   represents the number of movies you have watched from each studio.

                    Inspired by the work of [Tobias Stadler](https://tobias-stalder.netlify.app/dataviz/) & [Tomás Capretto](https://tomicapretto.com/)
                    """

                    st.markdown(f"""
                    # {title}
                    {subtitle}
                    """)

                    st.pyplot(fig)

                    title = "Your Favorite Decades"
                    subtitle = " The radar chart below shows the number of movies you have watched per decade (Top 8).\n"

                    st.markdown(f"""
                    # {title}
                    {subtitle}
                    """)

                    fig = draw_radar_decades(df)
                    st.pyplot(fig)

                    title = "Does the country of the movies always make movies of the same language?"
                    subtitle = """
                    The Sankey diagram below shows the distribution of the languages of the movies you have watched by country.
                    """

                    st.markdown(f"""
                    # {title}
                    {subtitle}
                    """)

                    fig = plot_sankey(df)
                    st.plotly_chart(fig)
        else:
            st.error("Please enter a username.")


if __name__ == "__main__":
    run_app()
