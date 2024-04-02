import os
import random
import sqlite3
import asyncio, aiohttp
import time
from gunpla_database_model import gunpla_db, gunpla_scraper
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from aiolimiter import AsyncLimiter

progress_bar = Progress(
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)
current_dir = os.getcwd() + "\\"


def find_remaining_link():

    db_path = f"{os.getcwd()}/gunpla.db"
    if not os.path.exists(db_path):
        return []
    else:
        conn = sqlite3.connect(f"{os.getcwd()}/gunpla.db")
        curs = conn.cursor()

        url_links = curs.execute("select url from gunpla")
        url_clean = [link[0] for link in url_links]

        return url_clean


async def main():

    gunpla_scrape = gunpla_scraper()
    tasks = []

    with open(rf"{current_dir + 'gunpla_scraper'}\gundam_links.txt", "r") as read:
        # get all the urls in the text file
        gunpla_link = list(set(read.readlines()))

        # objects for scraper and database setup

        url_clean = find_remaining_link()
        for link in gunpla_link:
            if link.strip() in url_clean:
                gunpla_link.remove(link)
            else:
                pass

        rate_limit = AsyncLimiter(3, 10)

        with progress_bar as p:

            task = p.add_task(
                "[progress.percentage]{task.percentage:>3.0f}%",
                total=len(gunpla_link),
            )

            for url in range(0, len(gunpla_link), 3):
                task_gunpla = [
                    gunpla_scrape.scrape_data(
                        current_url.strip(), rate_limit=rate_limit
                    )
                    for current_url in gunpla_link[url : url + 3]
                ]
                # task.appen
                p.update(task, advance=3)
                await asyncio.sleep(5)
                await asyncio.gather(*task_gunpla)


if __name__ == "__main__":

    current = time.perf_counter()
    asyncio.run(main())
    next = time.perf_counter()

    print(f"Time taken in minutes : {((next - current))/60}")
    print(f"Time taken in hours : {((next - current))/3600}")
