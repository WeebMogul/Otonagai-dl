from InquirerPy import inquirer
from rich.console import Console
from .controller import navigate_search_table, navigate_log_table
import sys
import os
from .hobby_link_jp_scraper.hlj_ui import HLJ_scraper_ui
from .hobby_link_jp_scraper.hlj_dl import HLJ_product_scraper
from .model import gunpla_log_db, gunpla_search_db, web_to_db
from .view import Gunpla_Table_View
import asyncio
import os

URL_FILE_PATH = rf".\Data\URLs.txt"


def create_data_contents():

    if not os.path.exists(rf".\Data"):
        os.mkdir(rf".\Data")

    if not os.path.exists(URL_FILE_PATH):
        with open(URL_FILE_PATH, "w") as f:
            f.write("")


def use_edit_file():

    Console().clear()
    Console().print("Editing file")

    with open(URL_FILE_PATH, "r") as f:
        existing_urls = f.read()

    result = inquirer.text(
        message="URLs:",
        multiline=True,
        long_instruction="Press escape and then enter to finish editing.",
        vi_mode=True,
        default=existing_urls,
    ).execute()

    with open(URL_FILE_PATH, "wb") as f:
        f.write(result.encode())


def scrape_to_db(URL_FILE_PATH):

    to_scrape_url = []
    inser = web_to_db()
    scraper_ui = HLJ_scraper_ui()

    with open(URL_FILE_PATH, "rb") as f:
        for line in f.readlines():
            to_scrape_url.append(line.decode().strip())

    batcher = HLJ_product_scraper(to_scrape_url, scraper_ui=scraper_ui, web_to_db=inser)
    result = asyncio.run(batcher.start_process())
    if len(result) < 1:
        return None
    else:
        inser.insert_to_table(result)


def menu():

    create_data_contents()

    search_db = gunpla_search_db()
    log_db = gunpla_log_db()

    while True:

        os.system("cls")
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
            os.system("cls")
            search_view = Gunpla_Table_View()
            navigate_search_table(search_db, search_view).navigate_table()

        # if menu_choice == "Advanced search Gundam Kits":
        #     os.system("cls")
        #     search_view = Gunpla_Table_View()
        #     navigate_search_table(search_db, search_view).navigate_table()

        if menu_choice == "View and update Gunpla Log":
            os.system("cls")
            log_view = Gunpla_Table_View()
            navigate_log_table(log_db, log_view).navigate_table()

        if menu_choice == "Open URL file":
            os.system("cls")
            use_edit_file()

        if menu_choice == "Exit":

            sys.exit()

        if menu_choice == "Add Gundam Kits to database":
            os.system("cls")
            scrape_to_db(URL_FILE_PATH)
