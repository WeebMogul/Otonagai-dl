import sqlite3
from abc import ABC, abstractmethod
from InquirerPy import inquirer
import time
import os
from .logging import log_msg

DB_PATH = "Data/gunpla.db"
status_priority = """
            CASE 
            WHEN status = "Planning" THEN 1
            WHEN status = "Acquired" THEN 2
            WHEN status = "Building" THEN 3
            WHEN status = "Completed" THEN 4
            WHEN status = "On Hold" THEN 5
            WHEN status = "Dropped" THEN 6
            END ASC
"""


def collect_options_from_db(choice_dict):

    category_dict = {}
    for category in choice_dict:
        if category[0] not in category_dict:
            category_dict[str(category[0])] = None

    category_dict["All"] = None
    return category_dict


def advanced_search(categories, item_types, series, manufacturer):
    search_title = inquirer.text("Which product you want to search ?").execute()

    search_category = inquirer.text(
        message="Which category ?",
        completer=categories,
    ).execute()

    search_item_type = inquirer.text(
        message="Which item type ?",
        completer=item_types,
    ).execute()

    search_series = inquirer.text(
        message="From which series ?",
        completer=series,
    ).execute()

    search_manufacturer = inquirer.text(
        message="From which manufacturer ?",
        completer=manufacturer,
    ).execute()

    return (
        search_title,
        search_category,
        search_item_type,
        search_series,
        search_manufacturer,
    )


class web_to_search_db:

    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()

    def remove_any_duplicates(self, new_url):

        self.cursor.execute("select url from gunpla")
        existing_url = {link[0].strip() for link in self.cursor.fetchall()}
        new_url = set(new_url)

        return list(new_url - existing_url)

    def insert_to_table(self, products):

        for product in products:
            log_msg(f"Inserting info for {product['URL']}")

            try:
                self.cursor.execute(
                    "INSERT INTO gunpla (title, url, code, jan_code, release_date, category, series, item_type, manufacturer, item_size_and_weight) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        product["Title"],
                        product["URL"],
                        product["Code"],
                        product["JAN Code"],
                        product["Release Date"],
                        product["Category"],
                        product["Series"],
                        product["Item Type"],
                        product["Manufacturer"],
                        product["Item Size/Weight"],
                    ),
                )
                log_msg(f"Inserting {product['Title']}")
            except sqlite3.IntegrityError:
                log_msg(f'{product["URL"]} already exists in the database')
                break
            except KeyError:
                break
        time.sleep(3)
        self.connection.commit()


class gunpla_search_db:

    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS gunpla (title text, URL text, code text not null primary key, jan_code text, release_date date, category text, series text, item_type text, manufacturer text, item_size_and_weight text)"
        )

    def advanced_view_table(self):
        search_category = collect_options_from_db(
            self.cursor.execute("select category from gunpla")
        )
        item_type_category = collect_options_from_db(
            self.cursor.execute("select item_type from gunpla")
        )
        series_category = collect_options_from_db(
            self.cursor.execute("select series from gunpla")
        )

        manufacturer_category = collect_options_from_db(
            self.cursor.execute("select manufacturer from gunpla")
        )

        title, category, item_type, series, manufacturer = advanced_search(
            search_category, item_type_category, series_category, manufacturer_category
        )

        with self.connection:
            self.cursor.execute(
                "SELECT code, title, series, item_type, manufacturer , release_date from gunpla where title like ? and category like ? and item_type like ? and series like ?  and manufacturer like ? order by release_date desc;",
                (
                    f"%{title}%",
                    f"%{category if category != 'All' else ''}%",
                    f"%{item_type if item_type != 'All' else ''}%",
                    f"%{series if series != 'All' else ''}%",
                    f"%{manufacturer if manufacturer != 'All' else ''}%",
                ),
            )

            self.result = self.cursor.fetchall()

            return self.result

    def view_table(self):

        with self.connection:
            self.cursor.execute(
                "SELECT code, title, series, item_type, manufacturer , release_date from gunpla order by release_date desc;",
            )

            self.result = self.cursor.fetchall()

            return self.result

    def insert_to_table(self, Code, Title, item_type):
        log_state = inquirer.select(
            "Please confirm state of task",
            [
                "Planning",
                "Acquired",
                "Building",
                "Completed",
                "On Hold",
                "Dropped",
            ],
        ).execute()
        # log_msg(f"Adding {Title} to log with current status {log_state}")

        with self.connection:

            self.cursor.execute("select count(*) from gunpla_log")
            count_log = self.cursor.fetchone()[0]
            log_id = count_log + 1

            self.cursor.execute(
                "INSERT into gunpla_log (log_id, code, title, item_type, status) VALUES (?,?,?,?,?)",
                (
                    log_id,
                    Code,
                    Title,
                    item_type,
                    log_state,
                ),
            )
            log_msg(f"Adding {Title} to log with current status {log_state}")


class gunpla_log_db:

    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS gunpla_log (log_id integer, code text, title text, item_type text, status text)"
        )

    def view_table(self):
        with self.connection:
            self.cursor.execute(f"select * from gunpla_log order by {status_priority}")
            # log_result = self.cursor.fetchall()
            return self.cursor.fetchall()

    def change_position(self, old_position, new_position):
        with self.connection:
            self.cursor.execute(
                "UPDATE gunpla_log set log_id = ? where log_id = ?",
                (new_position, old_position),
            )

    def update_table(self, log_id, name):
        log_state = inquirer.select(
            message=f'Please confirm state of task for the product : "{name}"',
            choices=[
                "Planning",
                "Acquired",
                "Building",
                "Completed",
                "On Hold",
                "Dropped",
            ],
        ).execute()

        with self.connection:
            self.cursor.execute(
                "UPDATE gunpla_log set status = ? where log_id = ?",
                (
                    log_state,
                    log_id,
                ),
            )
        log_msg(f"Changing status for {name} to new status {log_state}")
        return True

    def delete_from_table(self, log_id, name):
        if inquirer.confirm(
            f'Do you want to delete "{name}" from this entry ?'
        ).execute():
            with self.connection:
                self.cursor.execute("select count(*) from gunpla_log")
                count = self.cursor.fetchone()[0]

                if log_id is not None:
                    self.cursor.execute(
                        "DELETE from gunpla_log where log_id = ?",
                        (log_id,),
                    )

                    for pos in range(log_id, count + 1):
                        self.change_position(pos, pos - 1)
                    log_msg(f"Deleted {name} from the log")

        return True
