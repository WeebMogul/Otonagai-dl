import os
import random
import sqlite3
import asyncio, aiohttp
import time
from rich.live import Live
from rich.console import Console
from aiolimiter import AsyncLimiter
from rich.panel import Panel
import httpx
from bs4 import BeautifulSoup
from gunpla_db_schema import gunpla_db_connect
from ui import GunplaScraperUI
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

gunpla_ui = GunplaScraperUI()

user_agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

import re

current_dir = os.getcwd() + "\\" + "Gunpla-Tracker" + "\\"


def extract_text(element):

    if element is not None:
        return element.text.strip()
    else:
        return None


async def fetch_url(client, url, limiter, table):
    async with limiter:
        try:
            resp = await client.get(
                url, headers=user_agent, follow_redirects=True, timeout=10
            )
            print(resp.status_code)
            if resp.status_code == 404:
                table.add_row(f"[red]{url} not found in website. [/red]")
                return {
                    "Code": f"NA_{random.randint(10000,99999)}",
                    "url": url.strip(),
                }
            else:
                return resp.text

        except httpx.TimeoutException:
            print("Request timed out after 5 seconds. Retrying in 10 seconds")
            await asyncio.sleep(10)
            fetch_url(client, url, limiter, table)


loading_bar_size = 7
download_list_ratio = 2
gunpla_ui = GunplaScraperUI()


class Gunpla_Info:

    def __init__(self, gunpla_urls: list, gunpla_conn: gunpla_db_connect):
        self.gunpla_urls = gunpla_urls
        self.gunpla_conn = gunpla_conn

    def _find_remaining_link(
        self, gunpla_urls: list, gunpla_db_conn: gunpla_db_connect
    ):

        url_links = gunpla_db_conn.get_remaining_links(gunpla_urls)
        return url_links

    async def scrape_info(self):

        url_clean = self._find_remaining_link(self.gunpla_urls, self.gunpla_conn)

        rate_limit = AsyncLimiter(10, 10)
        with Live(
            gunpla_ui.progress_layout,
            auto_refresh=False,
            screen=True,
        ) as live:
            profile_bar, panel = await gunpla_ui.gunpla_profile_panel(
                total_stock=len(url_clean)
            )
            table, table_panel = await gunpla_ui.create_table()

            # live.update(gunpla_ui.progress_layout, refresh=True)
            for url in range(0, len(url_clean), 10):

                if url % 20 == 0:
                    table, table_panel = await gunpla_ui.create_table()
                task_gunpla = [
                    self.extract_data(
                        current_url.strip(),
                        rate_limit=rate_limit,
                        table_data=table,
                    )
                    for current_url in url_clean[url : url + 10]
                ]
                await asyncio.sleep(3)
                await asyncio.gather(*task_gunpla)

                gunpla_ui.loading_bar.update(profile_bar, advance=10, refresh=True)
                gunpla_ui.update_panels(panel, table_panel)
                live.update(gunpla_ui.progress_layout, refresh=True)

    async def extract_data(self, url: str, rate_limit: AsyncLimiter, table_data):
        try:
            # fetch and process data from batch of urls asynchronously
            async with httpx.AsyncClient() as client:

                # for all the urls, process and wait for requests in parallel
                html_response = await fetch_url(
                    client, url, rate_limit, table=table_data
                )

                if not isinstance(html_response, dict):
                    soup = BeautifulSoup(html_response, "html.parser")

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
                    product_detail_list = soup.find(
                        "div", class_="product-details"
                    ).find("ul")

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
                        table_data.add_row(
                            f"[green]{gunpla_info['title']}[/green] is added to the database"
                        )
                else:
                    gunpla_info = html_response
        except requests.HTTPError:
            print("Page not found. Skipping")


from rich import print


async def main():
    with open(rf"{current_dir + 'gunpla_scraper'}\gundam_links.txt", "r") as read:
        # get all the urls in the text file
        new_links = []
        gunpla_set = list(read.readlines())

        gunpla_conn = gunpla_db_connect(
            os.path.join(os.getcwd(), "Gunpla-Tracker\Data\gunpla.db")
        )

        gunpla_link = list(link.strip("\n") for link in gunpla_set)

        # gunpla_conn.get_remaining_links(gunpla_link)
        gunpla_info = Gunpla_Info(gunpla_link, gunpla_conn)
        await gunpla_info.scrape_info()


if __name__ == "__main__":

    asyncio.run(main())
