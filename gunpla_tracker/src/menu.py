from InquirerPy import inquirer
from .controller import search_table_navigation, log_table_navigation
import sys
import os
from .hobby_link_jp_scraper.hlj_dl import HLJ_product_scraper
from .hobby_link_jp_scraper.hlj_ui import HLJ_scraper_ui
from .model import gunpla_log_db, gunpla_search_db, web_to_search_db
from .view import Gunpla_Table_View
from .utils import (
    create_data_contents,
    use_edit_file,
    extract_from_page_links,
    filter_urls,
    add_to_search_db,
    extract_urls_from_file,
    add_page_nos,
)
import os
from rich.console import Console
import time


def menu():

    create_data_contents()
    search_db = gunpla_search_db()
    log_db = gunpla_log_db()
    console = Console()

    while True:

        console.clear()
        menu_choice = inquirer.select(
            message="Welcome to the Gunpla Tracker. \nPlease select any option to proceed",
            choices=[
                "Extract Merch info",
                "Merchandise Database",
                "Merchandise Log",
                "URLs to download",
                "Exit",
            ],
        ).execute()

        if menu_choice == "Merchandise Database":
            console.clear()
            search_view = Gunpla_Table_View()
            search_table_navigation(
                console=console, model=search_db, view=search_view
            ).navigate_table()

        if menu_choice == "Merchandise Log":
            console.clear()
            log_view = Gunpla_Table_View()
            log_table_navigation(
                model=log_db, view=log_view, console=console
            ).navigate_table()

        if menu_choice == "URLs to download":
            console.clear()
            use_edit_file(console, inquirer)

        if menu_choice == "Exit":

            sys.exit()

        if menu_choice == "Extract Merch info":
            console.clear()

            text_urls = extract_urls_from_file()
            page_urls, non_page_urls = filter_urls(text_urls)

            for url in page_urls:

                print(f"Please add the pages to extract the products from {url}\n")
                start_page = input("Please enter the starting page : ")
                end_page = input("Please enter the ending page : ")
                start_page, end_page = add_page_nos(start_page, end_page)

                if start_page is not None and end_page is not None:
                    non_page_urls.extend(
                        extract_from_page_links(
                            url, start_page=start_page, end_page=end_page
                        )
                    )

            add_to_search_db(
                extracted_urls=non_page_urls,
                scraper_ui=HLJ_scraper_ui(),
                search_db_conn=web_to_search_db(),
            )
