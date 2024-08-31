import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
import multiprocessing

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"


async def scrape_page(session, page_num):
    url = BASE_URL.format(page_num)
    async with session.get(url) as response:
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        results = []
        for book in books:
            title = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            results.append((title, price))
        return results


async def scrape_pages(start_page, end_page):
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_page(session, i)
                 for i in range(start_page, end_page + 1)]
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]


def process_worker(start_page, end_page, results_queue):
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(scrape_pages(start_page, end_page))
    for result in results:
        results_queue.put(result)


if __name__ == "__main__":
    start_time = time.time()

    manager = multiprocessing.Manager()
    results_queue = manager.Queue()

    processes = []
    num_processes = 4
    pages_per_process = 5

    for i in range(num_processes):
        start_page = i * pages_per_process + 1
        end_page = start_page + pages_per_process - 1
        p = multiprocessing.Process(target=process_worker, args=(
            start_page, end_page, results_queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    end_time = time.time()

    print(f"Scraped {len(results)} books in {
          end_time - start_time:.2f} seconds")
    print("Sample of results:")
    for title, price in results[:5]:
        print(f"Title: {title}, Price: {price}")
