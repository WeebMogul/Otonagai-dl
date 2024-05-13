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
            soup = BeautifulSoup(html_response.text, "html.parser")

            products = soup.find_all("a", class_="item-img-wrapper", href=True)
            for products in products:
                batch_url.append(f'https://www.hlj.com{products["href"]}'.strip())

    # self.url_batch.extend(batch_url)
    return batch_url
