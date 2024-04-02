import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import os
import time
from tqdm import tqdm
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich import print
import random
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import httpx

# current working directory
current_dir = os.getcwd() + "\\"

# components for progress bar
progress_bar = Progress(
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)

user_agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}


async def fetch_url(client, url, limiter):
    async with limiter:
        try:
            resp = await client.get(
                url, headers=user_agent, follow_redirects=True, timeout=10
            )
            if resp.status_code == 404:
                return False
            else:
                print(resp.status_code)
                return resp.text

        except httpx.TimeoutException:
            print("Request timed out after 5 seconds. Retrying in 10 seconds")
            await asyncio.sleep(10)
            fetch_url(client, url, limiter)


def extract_text(element):

    if element is not None:
        return element.text.strip()


class gunpla_db:

    def create_database(self):

        if not os.path.isfile(rf"{current_dir}\gunpla.db"):

            conn = sqlite3.connect(rf"{current_dir}\gunpla.db")
            curs = conn.cursor()

            curs.execute(
                """
                    CREATE TABLE IF NOT EXISTS gunpla (
                        bandai_id text primary key not null,
                        title text,
                        price text,
                        url text,
                        jan_code text,
                        release_date date,
                        category text,
                        series text,
                        item_type text,
                        manufacturer text,
                        item_size_and_weight text
                    )
                    """
            )

    def add_to_database(self, gunpla_info):

        self.gunpla_info = gunpla_info
        conn = sqlite3.connect(rf"{current_dir}\gunpla.db")
        curs = conn.cursor()

        with conn:
            curs.execute(
                """ INSERT INTO gunpla VALUES(:bandai_id, :title, :price, :url, :jan_code, :release_date, :category, :series, :item_type, :manufacturer, :item_size_and_weight) """,
                {
                    "bandai_id": self.gunpla_info.get("Code"),
                    "title": self.gunpla_info.get("title", None),
                    "price": re.sub(
                        "\s+|Dh|AED",
                        " ",
                        self.gunpla_info.get("price", None),
                    )
                    .strip()
                    .split()[-1],
                    "url": self.gunpla_info["url"],
                    "jan_code": self.gunpla_info.get("JAN Code", None),
                    "release_date": self.gunpla_info.get("Release Date", None),
                    "category": self.gunpla_info.get("Category", None),
                    "series": self.gunpla_info.get("Series", None),
                    "item_type": self.gunpla_info.get("Item Type", None),
                    "manufacturer": self.gunpla_info.get("Manufacturer", None),
                    "item_size_and_weight": self.gunpla_info.get(
                        "Item Size/Weight", None
                    ),
                },
            )


class gunpla_scraper:

    async def scrape_data(self, url: str, rate_limit):
        gunpla_info = {}

        gunpla_database = gunpla_db()
        gunpla_database.create_database()

        try:
            # fetch and process data from batch of urls asynchronously
            async with httpx.AsyncClient() as client:

                # print(f"Adding {url} to database")

                # for all the urls, process and wait for requests in parallel
                html = await fetch_url(
                    client,
                    url.strip(),
                    rate_limit,
                )
                # print(url.strip())
                # await asyncio.sleep(4)
                # async with semaphore:
                if html == False:
                    gunpla_info = {
                        "Code": f"NA_{random.randint(10000,99999)}",
                        "url": url.strip(),
                    }
                    print(f"{gunpla_info['url']} not found in website")
                else:
                    # print(f'Adding {gunpla_info["title"]} to database')
                    soup = BeautifulSoup(html, "lxml")

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
                    product_detail_list = soup.find(
                        "div", class_="product-details"
                    ).find("ul")

                    # key and value pairs for product details
                    for i in product_detail_list.find_all("li"):

                        product_detail = i.text.split(":")

                        gunpla_info[product_detail[0]] = re.sub(
                            "\s+", " ", product_detail[1].strip()
                        )
                    print(f'Added {gunpla_info["title"]} to database')
                    # print(gunpla_info["url"])

                try:
                    gunpla_database.add_to_database(gunpla_info=gunpla_info)
                except sqlite3.IntegrityError:
                    print(f"{gunpla_info['title']} already exists in the dataset")
        except requests.HTTPError:
            print("Page not found. Skipping")
