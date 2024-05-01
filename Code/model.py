import sqlite3
from abc import ABC, abstractmethod
from InquirerPy import inquirer

DB_PATH = "./Data/gunpla.db"


class gunpla_db(ABC):
    @abstractmethod
    def view_table(self):
        pass

    @abstractmethod
    def insert_to_table(self):
        pass

    @abstractmethod
    def delete_from_table(self):
        pass


class gunpla_search_db(gunpla_db):

    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS gunpla (Title text, URL text, Code text, `JAN Code` text, `Release Date` date, Category text, Series text, `Item Type` text, `Manufacturer` text, `Item Size/Weight` text)"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS gunpla_log (`Log ID` text, Code text, Title text, `Item Type` text, `Series` text)"
        )

    def delete_from_table(self):
        return super().delete_from_table()

    def view_table(self):

        search_title = inquirer.text("Which Gundam you want to search for ?").execute()
        search_item_type = inquirer.text(
            "Which grade to search for ?",
            completer={
                "High Grade Kits": None,
                "Master Grade Kits": None,
                "Real Grade Kits": None,
                "Perfect Grade Kits": None,
                "Other Gundam Kits": None,
            },
        ).execute()

        with self.connection:
            self.cursor.execute(
                "SELECT bandai_id, title, series, item_type, release_date from gunpla where title like :title and series like :series "
                "and item_type like :item_type order by release_date desc limit 20;",
                {
                    "title": "%" + search_title + "%",
                    "series": "%" + "" + "%",
                    "item_type": "%" + search_item_type + "%",
                },
            )

            self.result = self.cursor.fetchall()

            if len(self.result) < 1:
                return False
            return self.result

    def insert_to_table(self, bandai_id, title, item_type):
        if inquirer.confirm("Do you want to add to the database ?").execute():
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
                log_id = count_log + 1 if count_log else 1

                self.cursor.execute(
                    "INSERT into gunpla_log VALUES (:log_id, :bandai_id, :title, :item_type, :status)",
                    {
                        "log_id": log_id,
                        "bandai_id": bandai_id,
                        "title": title,
                        "item_type": item_type,
                        "status": log_state,
                    },
                )
                print(f"{title} ({bandai_id}) has been added to the database.")
        else:
            return False

        return True


class gunpla_log_db(gunpla_db):

    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS gunpla (Title text, URL text, Code text, `JAN Code` text, `Release Date` date, Category text, Series text, `Item Type` text, `Manufacturer` text, `Item Size/Weight` text)"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS gunpla_log (`Log ID` text, Code text, Title text, `Item Type` text, `Series` text)"
        )

    def view_table(self):
        with self.connection:
            self.cursor.execute("select * from gunpla_log")
            log_result = self.cursor.fetchall()
            return log_result

    def change_position(self, old_position, new_position):
        with self.connection:
            self.cursor.execute(
                "UPDATE gunpla_log set log_id = :new_position where log_id = :old_position",
                {"old_position": old_position, "new_position": new_position},
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
                "UPDATE gunpla_log set status = :status where log_id = :log_id",
                {
                    "status": log_state,
                    "log_id": log_id,
                },
            )

        return True

    def delete_from_table(self, log_id):
        if inquirer.confirm("Do you want to delete this entry ?").execute():
            with self.connection:

                self.cursor.execute("select count(*) from gunpla_log")
                count = self.cursor.fetchone()[0]

                if log_id is not None:
                    self.cursor.execute(
                        "DELETE from gunpla_log where log_id = :log_id",
                        {"log_id": log_id},
                    )

            for pos in range(1, count):
                self.change_position(pos, count + 1)

        return True

    def insert_to_table(self):
        return super().insert_to_table()


gunpla_search = gunpla_log_db()
gunpla_search.view_table()
