from InquirerPy import inquirer
from rich.console import Console
from .navigate_manager import navigate_search_table, navigate_log_table
import sys
import os
from hobby_link_jp_scraper.hlj_ui import HLJ_scraper_ui
from hobby_link_jp_scraper.hlj_dl import HLJ_product_scraper
from .model import gunpla_log_db, gunpla_search_db, web_to_db
from .view import Gunpla_Table_View
import asyncio

url_file_path = rf".\Data\URLs.txt"


def create_url_file():
    with open(url_file_path, "w") as f:
        f.write("")


def use_edit_file():

    Console().clear()
    Console().print("Editing file")

    with open(url_file_path, "r") as f:
        existing_urls = f.read()

    result = inquirer.text(
        message="URLs:",
        multiline=True,
        long_instruction="Press escape and then enter to finish editing.",
        vi_mode=True,
        default=existing_urls,
    ).execute()

    with open(url_file_path, "wb") as f:
        f.write(result.encode())


def scrape_to_db(url_file_path):

    to_scrape_url = []
    inser = web_to_db()
    scraper_ui = HLJ_scraper_ui()

    with open(url_file_path, "rb") as f:
        for line in f.readlines():
            to_scrape_url.append(line.decode().strip())

    existing_url = inser.remove_any_duplicates(to_scrape_url)

    if len(existing_url) > 0:
        batcher = HLJ_product_scraper(existing_url, scraper_ui=scraper_ui)
        result = asyncio.run(batcher.start_process())
        inser.insert_to_table(result)
        print("Something worked")

    else:
        print("No links to download currently.")


def menu():

    search_db = gunpla_search_db()
    log_db = gunpla_log_db()
    if not os.path.exists("./Data/URLs.txt"):
        create_url_file()

    while True:

        Console().clear()
        menu_choice = inquirer.select(
            message="Welcome to the Gunpla Tracker. \nPlease select any option to proceed",
            choices=[
                "Add Gundam Kits to database",
                "Search Gundam Kits",
                "View and update Gunpla Log",
                "Open URL file",
                "Exit",
            ],
        ).execute()

        if menu_choice == "Search Gundam Kits":
            search_view = Gunpla_Table_View()
            navigate_search_table(search_db, search_view).navigate_table()
            continue

        if menu_choice == "View and update Gunpla Log":
            log_view = Gunpla_Table_View()
            navigate_log_table(log_db, log_view).navigate_table()
            continue

        if menu_choice == "Open URL file":
            use_edit_file()

        if menu_choice == "Exit":

            sys.exit()

        if menu_choice == "Add Gundam Kits to database":
            scrape_to_db(url_file_path)
            continue
