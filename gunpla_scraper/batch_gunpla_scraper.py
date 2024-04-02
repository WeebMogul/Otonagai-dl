import requests
from bs4 import BeautifulSoup
import re
import time
import click
import sys
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

progress_bar = Progress(
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)


# @click.command()
# @click.argument("url", default=sys.stdin)
# @click.option("--start_page", type=click.INT)
# @click.option("--end_page", type=click.INT)
def scrape(url, start_page, end_page):
    print("\nDownloading links :")
    with progress_bar as p:
        for i in p.track(range(start_page, end_page + 1)):
            r = requests.get(
                url + f"&Page={i}",
                headers=user_agent,
            )
            soup = BeautifulSoup(r.content, "lxml")

            for link in soup.find_all("a", class_="item-img-wrapper", href=True):
                gunpla_links.append("https://www.hlj.com" + link["href"])

            if i % 10 != 0:
                time.sleep(7)
            else:
                time.sleep(30)

    with open("gundam_links.txt", "w") as file_write:
        file_write.writelines(gunpla_link + "\n" for gunpla_link in gunpla_links)


user_agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

gunpla_links = []

if __name__ == "__main__":
    url = "https://www.hlj.com/search/?MacroType2=High+Grade+Kits&Page=1&MacroType2=High-Grade+Kits&GenreCode2=Gundam&MacroType2=Master+Grade+Kits&MacroType2=Master-Grade+Kits&MacroType2=Other+Gundam+Kits&MacroType2=SD+%26+BB+Grade+Kits&MacroType2=Real+Grade+Kits&MacroType2=Real-Grade+Kits&MacroType2=Perfect+Grade+Kits&MacroType2=Perfect-Grade+Kits&MacroType2=Gundam+Kits&MacroType2=Detailing+Kits%2FAccessories"
    start_page = 1
    end_page = 154

    scrape(url, start_page, end_page)
