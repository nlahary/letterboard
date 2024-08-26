from selectolax.parser import HTMLParser
import httpx
import asyncio
import pandas as pd
from time import time
from concurrent.futures import ThreadPoolExecutor
import backoff
import streamlit as st

from visuals_2 import *
from visuals import *


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
                    st.success("Data fetched successfully!")
                    if df.empty:
                        st.error(
                            f"No data found for user '{username}'. Please check the username and try again.")
                        return
                except AttributeError as e:
                    if "PoolTimeoutError" in str(e):
                        st.error("The request timed out. Please try again.")
                        return

                if df.empty:
                    st.error(
                        f"No data found for user '{username}'. Please check the username and try again.")
                    return
                tab_level1, tab_level2, tab_level3 = st.tabs(
                    ["Level.1", "Level.2", "Level.3"])

                with tab_level1:
                    try:
                        fig = draw_top3(df)
                        st.pyplot(fig)

                        fig = draw_top_countries(df)
                        st.plotly_chart(fig)

                        fig = draw_log_timeline(df)
                        st.plotly_chart(fig)

                        fig = draw_top_genres(df)
                        st.plotly_chart(fig)

                        fig = draw_rating_dist(df)
                        st.plotly_chart(fig)

                        fig = draw_top_actors(df)
                        st.plotly_chart(fig)

                    except UnboundLocalError:
                        st.error(
                            f"Timeout error. Please try again or check your internet connection.")
                        return

                with tab_level2:

                    fig, title, subtitle = draw_studios_radar(df)
                    st.markdown(f"""
                    # {title}
                    {subtitle}
                    """)
                    st.pyplot(fig)

                    fig, title, subtitle = draw_decades_radar(df)
                    st.markdown(f"""
                    # {title}
                    {subtitle}
                    """)
                    st.pyplot(fig)

                    fig, title, subtitle = draw_lang_sankey(df)
                    st.markdown(f"""
                    # {title}
                    {subtitle}
                    """)
                    st.plotly_chart(fig)

                with tab_level3:

                    if 'filter_by' not in st.session_state:
                        st.session_state['filter_by'] = "Country"

                    # Create select boxes without refreshing the page
                    filter_by = st.selectbox(
                        "Filter by:", ["Country", "Language",
                                       "Genre", "Director", "Actor", "Studio"],
                        index=["Country", "Language", "Genre", "Director", "Actor", "Studio"].index(
                            st.session_state['filter_by']),
                        key='filter_by_select'
                    )

                    apply_filters = st.button("Apply Filters")

                    if apply_filters or st.session_state['filter_by'] != filter_by:
                        st.session_state['filter_by'] = filter_by

                        # Filtering logic
                        if filter_by == "Country":
                            top_10 = df["country"].value_counts().head(10)
                        elif filter_by == "Language":
                            top_10 = df["primary_language"].value_counts().head(
                                10)
                        elif filter_by == "Genre":
                            top_10 = df["genres"].explode(
                            ).value_counts().head(10)
                        elif filter_by == "Director":
                            top_10 = df["director"].value_counts().head(10)
                        elif filter_by == "Actor":
                            top_10 = df["actors"].explode(
                            ).value_counts().head(10)
                        elif filter_by == "Studio":
                            top_10 = df["studio"].value_counts().head(10)

                        st.write(top_10)
                    else:
                        # Default display when the app is first loaded or not interacting with the button
                        if st.session_state['filter_by'] == "Country":
                            top_10 = df["country"].value_counts().head(10)
                        elif st.session_state['filter_by'] == "Language":
                            top_10 = df["primary_language"].value_counts().head(
                                10)
                        elif st.session_state['filter_by'] == "Genre":
                            top_10 = df["genres"].explode(
                            ).value_counts().head(10)
                        elif st.session_state['filter_by'] == "Director":
                            top_10 = df["director"].value_counts().head(10)
                        elif st.session_state['filter_by'] == "Actor":
                            top_10 = df["actors"].explode(
                            ).value_counts().head(10)
                        elif st.session_state['filter_by'] == "Studio":
                            top_10 = df["studio"].value_counts().head(10)

                        st.write(top_10)

        else:
            st.error("Please enter a username.")


if __name__ == "__main__":
    run_app()
