import os
from rich.console import Console
import asyncio
import time
from .warning_shots import no_downloads
from .hobby_link_jp_scraper.hlj_batch import extract_batch
from .hobby_link_jp_scraper.hlj_dl import HLJ_product_scraper
import asyncio
from .log_system import log_msg


# logging.basicConfig(level=logging.INFO)

URL_FILE_PATH = rf"./Data/URLs.txt"
DATA_FOLDER_PATH = rf"./Data"
DB_PATH = "./Data/otonagai.db"


# Create Data folder to store db file
def create_data_contents():
    if not os.path.exists(DATA_FOLDER_PATH):
        os.mkdir(DATA_FOLDER_PATH)

        with open(URL_FILE_PATH, "w") as f_url:
            f_url.write("")

        with open(DB_PATH, "w") as f_db:
            f_db.write("")


# extract the urls from the text file
def extract_urls_from_file():
    text_file_urls = []
    with open(URL_FILE_PATH, "rb") as f:
        text_file_urls.extend(line.decode().strip() for line in f.readlines())

    return text_file_urls


# check if the start page number is bigger than the end page
def start_bigger_than_end(func):
    def wrapper_function(start_page, end_page):
        try:
            start_page = int(start_page)
            end_page = int(end_page)
            if start_page > end_page:
                print("\n Starting page is bigger than ending page. Try again")
        except ValueError:
            # print("Please add numbers next time")
            return func(None, None)
        return func(start_page, end_page)

    return wrapper_function


@start_bigger_than_end
def add_page_nos(start_page, end_page):
    return start_page, end_page


# create a UI interface to add the URLs
def use_edit_file(inquirer):

    with open(URL_FILE_PATH, "r") as f:
        present_urls = f.read()

    url_collection = inquirer.text(
        message="URLs to be extracted:",
        multiline=True,
        vi_mode=True,
        default=present_urls,
    ).execute()

    with open(URL_FILE_PATH, "wb") as f:
        f.write(url_collection.encode())


# only retrieve the urls that are from HobbylinkJapan
def filter_urls(urls):

    # remove any links not related to hobby link japan
    hobbylink_urls = list(filter(lambda x: "hlj.com" in x, urls))

    # separate links into page and non-page urls
    page_urls = list(filter(lambda x: "search" in x, hobbylink_urls))
    non_page_urls = list(filter(lambda x: "search" not in x, hobbylink_urls))

    return page_urls, non_page_urls


# start extracting the product URLs from the pages
def extract_from_page_links(page_urls, start_page, end_page):

    extracted_urls = []
    extracted_urls.extend(
        asyncio.run(extract_batch(page_urls, start_page=start_page, end_page=end_page))
    )

    return extracted_urls


# scrape and add the product info to the search database
def add_to_search_db(extracted_urls, scraper_ui, search_db_conn):
    batcher = HLJ_product_scraper(
        extracted_urls, scraper_ui=scraper_ui, web_to_search_db=search_db_conn
    )
    batch_result = asyncio.run(batcher.start_process())
    if len(batch_result) < 1:
        log_msg("No new downloads found")
        Console().print(no_downloads())
        time.sleep(5)
    else:
        search_db_conn.insert_to_table(batch_result)
