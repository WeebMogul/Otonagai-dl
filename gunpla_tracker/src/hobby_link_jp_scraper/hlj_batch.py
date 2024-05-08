import requests
from bs4 import BeautifulSoup
import re
import asyncio
import random
from .hlj_ui import HLJ_scraper_ui
from rich.live import Live
import time
from rich import print
from ..model import web_to_search_db
from rich.console import Console
from InquirerPy import inquirer


def _get_page_nos(url):

    print(f"\nThere is a link that contains multiple pages : {url}\n")
    start_page = int(input("Please enter the starting page: "))
    end_page = int(input("Please enter the ending page: "))

    # if start_page > end_page:
    #     print("The start page is more than the end page. Please try again")
    #     return None, None
    # elif ValueError:
    #     print("Please add a number for both starting and ending pages. Thank you")
    # else:
    return int(start_page), int(end_page)


# except ValueError:
#     print("Please add a number for both starting and ending pages. Thank you")


async def extract_batch(page_based_url, start_page, end_page):
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
            soup = BeautifulSoup(html_response.text, "html.parser")

            kits = soup.find_all("a", class_="item-img-wrapper", href=True)
            for kit in kits:
                batch_url.append(f'https://www.hlj.com{kit["href"]}'.strip())

    # self.url_batch.extend(batch_url)
    return batch_url
