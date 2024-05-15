import requests
from bs4 import BeautifulSoup
import asyncio
from ..logging import log_msg


async def extract_batch(page_based_url, start_page, end_page):

    # list of urls extracted from every page
    batch_url = []

    semaphore = asyncio.Semaphore(2)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    # start_page, end_page = _get_page_nos(page_based_url)

    async with semaphore:
        for page in range(start_page, end_page):

            html_response = requests.Session().get(
                f"{page_based_url}&Page={page}", headers=headers
            )
            log_msg(
                f"Extracting product info from '{page_based_url}&Page={page}' - Status Code : {html_response.status_code}"
            )
            soup = BeautifulSoup(html_response.text, "html.parser")

            products = soup.find_all("a", class_="item-img-wrapper", href=True)
            batch_url.extend(
                f'https://www.hlj.com{product["href"]}'.strip() for product in products
            )
            #     log_msg(
            #     f"Collected 'https://www.hlj.com{products["href"]}'".strip()
            # )

    # self.url_batch.extend(batch_url)
    return batch_url
