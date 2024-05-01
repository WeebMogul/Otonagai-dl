from InquirerPy import inquirer
from rich.console import Console
from .navigate_manager import navigate_search_table, navigate_log_table
import sys
import os
import time
from hobby_link_jp_scraper.hlj_dl import HLJ_product_scraper
from .model import gunpla_log_db, gunpla_search_db
from .view import Gunpla_Table_View

# from hobby_link_jp_scraper.file_handles import Export_to_file
import asyncio

url_file_path = rf".\Data\URLs.txt"


def use_edit_file():

    Console().clear()
    Console().print("Editing file")

    with open(url_file_path, "w") as f:
        f.write("")

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

    with open(url_file_path, "rb") as f:
        for line in f.readlines():
            to_scrape_url.append(line.decode())

    batcher = HLJ_product_scraper(to_scrape_url)
    result = asyncio.run(batcher.start_process())

    # extractor = Export_to_file(result)
    # extractor.to_json(rf"{os.getcwd()}\Data\scrapped_data.json")


def menu(curs, conn):

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
            search_db = gunpla_search_db()
            search_view = Gunpla_Table_View()
            search_table = navigate_search_table(
                search_db, search_view
            ).navigate_table()
            if search_table:
                menu(curs, conn)

        if menu_choice == "View and update Gunpla Log":
            log_db = gunpla_log_db()
            log_view = Gunpla_Table_View()
            log_table = navigate_log_table(log_db, log_view).navigate_table()
            if log_table:
                menu(curs, conn)
            # print(log_table)

        if menu_choice == "Open URL file":
            use_edit_file()

        if menu_choice == "Exit":
            Console().clear()
            sys.exit()

        if menu_choice == "Add Gundam Kits to database":
            # search_table = navigate_search_table(curs, conn).navigate_table()
            # if search_table:
            #     menu(curs, conn)
            # print(search_table)
            scrape_to_db(url_file_path)
            time.sleep(2000)
