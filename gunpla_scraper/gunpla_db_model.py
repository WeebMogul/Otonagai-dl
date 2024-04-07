import os
import random
import sqlite3
import asyncio, aiohttp
import time
from rich.live import Live
from rich.console import Console
from aiolimiter import AsyncLimiter
from ui import GunplaScraperUI
from rich.panel import Panel
import httpx
from bs4 import BeautifulSoup
from gunpla_info_scraper import gunpla_db_connect
import requests

# progress_bar = Progress(
#     TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
#     BarColumn(),
#     MofNCompleteColumn(),
#     TextColumn("•"),
#     TimeElapsedColumn(),
#     TextColumn("•"),
#     TimeRemainingColumn(),
# )

user_agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

import re

current_dir = os.getcwd() + "\\"


def extract_text(element):

    if element is not None:
        return element.text.strip()


async def fetch_url(client, url, limiter):
    async with limiter:
        try:
            resp = await client.get(
                url, headers=user_agent, follow_redirects=True, timeout=10
            )
            if resp.status_code == 404:
                print(f"{url} not found in website")
                return {
                    "Code": f"NA_{random.randint(10000,99999)}",
                    "url": url.strip(),
                }
            else:
                return resp.text

        except httpx.TimeoutException:
            print("Request timed out after 5 seconds. Retrying in 10 seconds")
            await asyncio.sleep(10)
            fetch_url(client, url, limiter)


loading_bar_size = 7
download_list_ratio = 2


class Gunpla_Info:

    def __init__(self, gunpla_urls: list, gunpla_conn: gunpla_db_connect):
        self.gunpla_urls = gunpla_urls
        self.gunpla_conn = gunpla_conn

    def find_remaining_link(self, gunpla_urls: list, gunpla_db_conn: gunpla_db_connect):

        url_links = gunpla_db_conn.get_remaining_links(gunpla_urls)
        url_clean = [link[0] for link in url_links]

        for link in gunpla_urls:
            if link.strip() in url_clean:
                gunpla_urls.remove(link)
            else:
                pass

        return gunpla_urls

    async def scrape_info(self):

        url_clean = self.find_remaining_link(self.gunpla_urls, self.gunpla_conn)

        rate_limit = AsyncLimiter(10, 10)

        for url in range(0, len(url_clean), 20):
            task_gunpla = [
                self.extract_data(
                    current_url.strip(),
                    rate_limit=rate_limit,
                )
                for current_url in self.gunpla_urls[url : url + 10]
            ]

            await asyncio.sleep(3)
            await asyncio.gather(*task_gunpla)

    async def extract_data(self, url: str, rate_limit: AsyncLimiter):
        try:
            # fetch and process data from batch of urls asynchronously
            async with httpx.AsyncClient() as client:

                # for all the urls, process and wait for requests in parallel
                html_response = await fetch_url(
                    client,
                    url.strip(),
                    rate_limit,
                )

                if html_response == False:
                    gunpla_info = html_response

                soup = BeautifulSoup(html_response, "lxml")

                gunpla_info = {}
                # title
                gunpla_info["title"] = extract_text(
                    soup.find("h2", class_="page-title")
                )
                # price
                gunpla_info["price"] = extract_text(
                    soup.find("p", class_="price product-margin")
                )
                # url
                gunpla_info["url"] = url.strip()

                # list of product details
                product_detail_list = soup.find("div", class_="product-details").find(
                    "ul"
                )

                # key and value pairs for product details
                for i in product_detail_list.find_all("li"):

                    product_detail = i.text.split(":")

                    if len(product_detail) > 2:
                        gunpla_info[product_detail[0]] = re.sub(
                            "\s+",
                            " ",
                            product_detail[1].strip()
                            + " : "
                            + product_detail[2].strip(),
                        )
                    else:
                        gunpla_info[product_detail[0]] = re.sub(
                            "\s+", " ", product_detail[1].strip()
                        )

                if self.gunpla_conn.add_to_database(gunpla_info=gunpla_info):
                    print(f"{gunpla_info['title']} is added to the database")
                else:
                    print(f"{gunpla_info['title']} already exists in the database")

        except requests.HTTPError:
            print("Page not found. Skipping")
