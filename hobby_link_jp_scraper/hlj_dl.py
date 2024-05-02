import requests
from bs4 import BeautifulSoup
import re
import pprint
import asyncio
import random
from .hlj_ui import HLJ_scraper_ui
from rich.live import Live
import time
from rich import print

# from file_handles import Export_to_file
from rich.console import Console
import httpx
from InquirerPy import inquirer

lock = asyncio.Lock()


def extract_text(element):

    return element.text.strip() if element is not None else None


# get the start and end pages to scrape from
def get_start_and_end_page(url):

    print(f"\nThere is a link that contains multiple pages : {url}\n")
    start_page = input("Please enter the starting page: ")
    end_page = input("Please enter the ending page: ")

    return int(start_page), int(end_page)


class HLJ_product_scraper:

    def __init__(self, url: list[str], scraper_ui: HLJ_scraper_ui):
        self.url_batch = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        self.semaphore = asyncio.Semaphore(2)
        self.hlj_ui = scraper_ui

    async def start_process(self):
        scraped_products = []

        # clear console contents
        Console().clear()

        # If the link contains multiple items, extract separate links from the list of pages specified
        for search_link in self.url_batch:
            if "search" in search_link:

                start_page, end_page = get_start_and_end_page(search_link)
                await self._extract_batch(search_link, start_page, end_page)

        # remove the urls with the word 'search'
        self.url_batch = [url for url in self.url_batch if "search" not in url]

        # create the layout and loading bar to show
        self.hlj_ui.create_layout(len(self.url_batch))
        self.loading_bar = await self.hlj_ui.get_progress()

        # start and update the program live
        with Live(self.loading_bar, refresh_per_second=2) as live:

            for link in self.url_batch:
                scraped_products.append(
                    asyncio.create_task(self._get_product_info(link))
                )

            scraped_results = [
                await product_info
                for product_info in asyncio.as_completed(scraped_products)
            ]

            live.update(self.loading_bar)

        return scraped_results

    async def _get_product_info(self, url):
        async with self.semaphore:
            html_response = requests.Session().get(url.strip(), headers=self.headers)

            # check if the url response isn't giving a 404 error
            if html_response.status_code != 404:

                soup = BeautifulSoup(html_response.text, "lxml")
                hlj_product_info = {
                    "Title": extract_text(soup.find("h2", class_="page-title")),
                    "URL": url.strip(),
                }

                # get list of product details
                product_detail_list = soup.find("div", class_="product-details").find(
                    "ul"
                )

                # key and value pairs for product details section
                for i in product_detail_list.find_all("li"):

                    product_detail = i.text.split(":")

                    if len(product_detail) > 2:
                        hlj_product_info[product_detail[0]] = re.sub(
                            "\s+",
                            " ",
                            f"{product_detail[1].strip()} : {product_detail[2].strip()}",
                        )
                    else:
                        hlj_product_info[product_detail[0]] = re.sub(
                            "\s+", " ", product_detail[1].strip()
                        )

                # Item size and weight may not be available with some products, so return None if it happens
                if "Item Size/Weight" not in hlj_product_info:
                    hlj_product_info["Item Size/Weight"] = None
            else:
                # If the link returns a 404 error, return an empty dict for the product with random code and url
                hlj_product_info = {
                    "url": url.strip(),
                    "Code": f"NA_{random.randint(1000,9999)}",
                }
            await self.hlj_ui.update_bar()
            await self.hlj_ui.update_table(message=f"Finished {url.strip()}")
            await self.hlj_ui.update_layout()

        return hlj_product_info

    async def _extract_batch(self, page_based_url, start_page=1, end_page=2):
        batch_url = []

        async with self.semaphore:
            for page in range(start_page, end_page):

                html_response = requests.Session().get(
                    f"{page_based_url}&Page={page}", headers=self.headers
                )
                soup = BeautifulSoup(html_response.text, "lxml")

                kits = soup.find_all("a", class_="item-img-wrapper", href=True)
                for kit in kits:
                    batch_url.append(f'https://www.hlj.com{kit["href"]}')

        self.url_batch.extend(batch_url)


# if __name__ == "__main__":

#     single_url = [
#         "https://www.hlj.com/1-144-scale-30mm-eexm-s03h-forestieri-03-banh663016",
#         "https://www.hlj.com/search/?Page=1&GenreCode2=Gundam&MacroType2=Master+Grade+Kits&MacroType2=Master-Grade+Kits",
#     ]

#     scraper_ui = HLJ_scraper_ui()

#     batcher = HLJ_product_scraper(single_url, scraper_ui)
#     result = asyncio.run(batcher.start_process())
