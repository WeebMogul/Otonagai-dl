import requests
from bs4 import BeautifulSoup
import re
import os
from rich import print
import random
import asyncio
import aiohttp
import sqlite3
from aiolimiter import AsyncLimiter
import httpx
from rich import print
from rich.panel import Panel

# current working directory

# components for progress bar
user_agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}


def clean_price(price):

    if price is not None:
        return (
            re.sub(
                "\s+|Dh|AED",
                " ",
                price,
            )
            .strip()
            .split()[-1]
        )

    else:
        return None


class gunpla_db_connect:

    def __init__(self, location):
        self.conn_gunpla = sqlite3.connect(location)
        self.curs_gunpla = self.conn_gunpla.cursor()

    def create_database(self):

        with self.conn_gunpla:
            self.curs_gunpla.execute(
                """
                        CREATE TABLE IF NOT EXISTS gunpla (
                            bandai_id text primary key not null,
                            title text,
                            price float,
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

    def add_to_database(
        self,
        gunpla_info,
    ):

        try:
            with self.conn_gunpla:
                self.curs_gunpla.execute(
                    """ INSERT INTO gunpla VALUES(:bandai_id, :title, :price, :url, :jan_code, :release_date, :category, :series, :item_type, :manufacturer, :item_size_and_weight) """,
                    {
                        "bandai_id": gunpla_info.get("Code"),
                        "title": gunpla_info.get("title", None),
                        "price": clean_price(gunpla_info.get("price", None)),
                        "url": gunpla_info["url"],
                        "jan_code": gunpla_info.get("JAN Code", None),
                        "release_date": gunpla_info.get("Release Date", None),
                        "category": gunpla_info.get("Category", None),
                        "series": gunpla_info.get("Series", None),
                        "item_type": gunpla_info.get("Item Type", None),
                        "manufacturer": gunpla_info.get("Manufacturer", None),
                        "item_size_and_weight": gunpla_info.get(
                            "Item Size/Weight", None
                        ),
                    },
                )
                return True
        except sqlite3.IntegrityError:
            # layout_table.add_row(
            return False

    def get_remaining_links(
        self,
        gunpla_urls: list,
    ):
        # with
        url_links = self.curs_gunpla.execute("select url from gunpla").fetchall()
        url_clean = list(link[0] for link in url_links)
        gunpla_urls = list(link for link in gunpla_urls)

        for link in gunpla_urls:
            if link in url_clean:
                gunpla_urls.remove(link)

        print(len(gunpla_urls))

        return gunpla_urls


# from rich import print

# if __name__ == "__main__":
#     db_link = os.path.join(os.getcwd(), "Gunpla-Tracker\Data\gunpla.db")
#     txt_link = os.path.join(
#         os.getcwd(), "Gunpla-Tracker\gunpla_scraper\gundam_links.txt"
#     )

#     with open(txt_link, "r+") as read:
#         # get all the urls in the text file
#         new_links = []
#         gunpla_set = list(read.readlines())
#         for i in gunpla_set:
#             new_links.append(i.split("https"))

#         # new_links = list("https" + i for i in gunpla_list)
#         new_total = set("https" + new_link for new_link in new_links[0])
#         print(new_total)

#     gunpla_conn = gunpla_db_connect(db_link)
#     gunpla_conn.get_remaining_links(new_total)
