import sqlite3
from abc import ABC, abstractmethod
from InquirerPy import inquirer
import time

DB_PATH = "Data/gunpla.db"


def collect_options(choice_dict):

    category_dict = {}
    for category in choice_dict:
        if category[0] not in category_dict:
            category_dict[str(category[0])] = None

    category_dict["All"] = None
    return category_dict


def advanced_search(categories, item_types, series):
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

    return search_title, search_category, search_item_type, search_series


class web_to_search_db:

    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()

    def remove_any_duplicates(self, new_url):

        self.cursor.execute("select URL from gunpla")
        existing_url = set(link[0].strip() for link in self.cursor.fetchall())
        new_url = set(new_url)

        return list(new_url - existing_url)

    def insert_to_table(self, products):

        for product in products:

            try:
                self.cursor.execute(
                    "INSERT INTO gunpla (Title, URL, Code, `JAN Code`, `Release Date`, Category, Series, `Item Type`, Manufacturer, `Item Size/Weight`) VALUES (?,?,?,?,?,?,?,?,?,?)",
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
            except sqlite3.IntegrityError:
                print(
                    "Products are already downloaded. Please add new ones in the url file."
                )
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
            "CREATE TABLE IF NOT EXISTS gunpla (Title text, URL text, Code text not null primary key, `JAN Code` text, `Release Date` date, Category text, Series text, `Item Type` text, `Manufacturer` text, `Item Size/Weight` text)"
        )

    def advanced_view_table(self):
        search_category = collect_options(
            self.cursor.execute("select Category from gunpla")
        )
        item_type_category = collect_options(
            self.cursor.execute("select `Item Type` from gunpla")
        )
        series_category = collect_options(
            self.cursor.execute("select Series from gunpla")
        )
        title, category, item_type, series = advanced_search(
            search_category, item_type_category, series_category
        )

        with self.connection:
            self.cursor.execute(
                "SELECT Code, Title, Series, `Item Type`, `Release Date` from gunpla where Title like ? and Category like ? and `Item Type` like ? and Series like ? order by `Release Date` desc;",
                (
                    f"%{title}%",
                    f"%{category if category != 'All' else ''}%",
                    f"%{item_type if item_type != 'All' else ''}%",
                    f"%{series if series != 'All' else ''}%",
                ),
            )

            self.result = self.cursor.fetchall()

            return self.result

    def view_table(self):

        with self.connection:
            self.cursor.execute(
                "SELECT Code, Title, Series, `Item Type`, `Release Date` from gunpla order by `Release Date` desc;",
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

        with self.connection:

            self.cursor.execute("select count(*) from gunpla_log")
            count_log = self.cursor.fetchone()[0]
            log_id = count_log + 1

            self.cursor.execute(
                "INSERT into gunpla_log (`Log ID`, Code, Title, `Item Type`, Series) VALUES (?,?,?,?,?)",
                (
                    log_id,
                    Code,
                    Title,
                    item_type,
                    log_state,
                ),
            )
            print(f"{Title} ({Code}) has been added to the log.")


class gunpla_log_db:

    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS gunpla_log (`Log ID` integer, Code text, Title text, `Item Type` text, `Series` text)"
        )

    def view_table(self):
        with self.connection:
            self.cursor.execute("select * from gunpla_log")
            log_result = self.cursor.fetchall()
            return log_result

    def change_position(self, old_position, new_position):
        with self.connection:
            self.cursor.execute(
                "UPDATE gunpla_log set `Log ID` = ? where `Log ID` = ?",
                (new_position, old_position),
            )

    def update_table(self, log_id):
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
        with self.connection:
            self.cursor.execute(
                "UPDATE gunpla_log set Series = ? where `Log ID` = ?",
                (
                    log_state,
                    log_id,
                ),
            )

        return True

    def delete_from_table(self, log_id):
        if inquirer.confirm("Do you want to delete this entry ?").execute():
            with self.connection:
                self.cursor.execute("select count(*) from gunpla_log")
                count = self.cursor.fetchone()[0]

                if log_id is not None:
                    self.cursor.execute(
                        "DELETE from gunpla_log where `Log ID` = ?",
                        (log_id,),
                    )

                    for pos in range(log_id, count + 1):
                        self.change_position(pos, pos - 1)

        return True
