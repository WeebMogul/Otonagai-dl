import requests
from bs4 import BeautifulSoup
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from gunpla_info_scraper import gunpla_db_connect
import time
from gunpla_db_model import Gunpla_Info
import asyncio
from rich import print
from rich.prompt import Prompt
from rich.panel import Panel
from rich.live import Live
import os

prog_bar = Progress(
    TextColumn("[progress.description]{task.description:}"),
    BarColumn(bar_width=None),
    MofNCompleteColumn(),
)

prog_panel = Panel(
    prog_bar, border_style="blue", expand=True, padding=(1, 1), height=None
)


async def scrape(url, start_page, end_page, gunpla_db):

    prog_bar.add_task("Extracting page links", total=int(end_page))
    gunpla_links = []

    with Live(prog_panel, auto_refresh=True, screen=True) as live:
        for i in range(int(start_page), int(end_page) + 1):

            r = requests.get(
                url + f"&Page={i}",
                headers=user_agent,
            )
            soup = BeautifulSoup(r.content, "lxml")

            for link in soup.find_all("a", class_="item-img-wrapper", href=True):
                gunpla_links.append("https://www.hlj.com" + link["href"])

            # print(prog_bar)
            time.sleep(5)
            prog_bar.update(0, advance=1)
            live.update(prog_panel, refresh=True)

        gunpla_info = Gunpla_Info(list(set(gunpla_links)), gunpla_db)
    await gunpla_info.scrape_info()


user_agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

if __name__ == "__main__":

    url = "https://www.hlj.com/search/?MacroType2=High+Grade+Kits&Page=1&MacroType2=High-Grade+Kits&GenreCode2=Gundam&MacroType2=Master+Grade+Kits&MacroType2=Master-Grade+Kits&MacroType2=Other+Gundam+Kits&MacroType2=SD+%26+BB+Grade+Kits&MacroType2=Real+Grade+Kits&MacroType2=Real-Grade+Kits&MacroType2=Perfect+Grade+Kits&MacroType2=Perfect-Grade+Kits&MacroType2=Gundam+Kits&MacroType2=Detailing+Kits%2FAccessories"
    data_location = os.path.join(os.getcwd(), "Gunpla-Tracker\Data\gunpla.db")

    gunpla_db = gunpla_db_connect(data_location)
    gunpla_db.create_database()

    start_page = Prompt.ask("Enter page to start")
    end_page = Prompt.ask("Enter page to end")

    asyncio.run(scrape(url, start_page, end_page, gunpla_db))
