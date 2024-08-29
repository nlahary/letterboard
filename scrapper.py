from concurrent.futures import ThreadPoolExecutor
from selectolax.parser import HTMLParser
from time import time
import pandas as pd
import backoff
import httpx
import asyncio


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
