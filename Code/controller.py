import sqlite3
from view import Gunpla_Table_View
from rich.console import Console
from InquirerPy import inquirer
import re
from abc import ABC, abstractmethod
from curses import wrapper
from readchar import readkey, key
from InquirerPy import inquirer
from datetime import datetime

db_location = r"D:\GitHub\Python-Programming-Projects\Gunpla_Tracker_Database\Gunpla-Tracker\Data\gunpla.db"

console = Console()

conn = sqlite3.connect(db_location)
# conn.create_function(
#     "regexp",
#     2,
# )
curs = conn.cursor()


def regexp(y, x, search=re.search):
    return 1 if search(y, x) else 0


def create_table():
    with conn:
        curs.execute(
            """
                     CREATE TABLE IF NOT EXISTS gunpla_log(
                         bandai_id text,
                         build_date date,
                         title text,
                         item_type date,
                         status text
                     )
                     """
        )


def search_gunpla(title: str = "", series: str = "", item_type: str = ""):
    curs.execute(
        "SELECT bandai_id, title, series, item_type, release_date from gunpla where title like :title and series like :series "
        "and item_type like :item_type order by release_date desc limit 10;",
        {
            "title": "%" + title + "%",
            "series": "%" + series + "%",
            "item_type": "%" + item_type + "%",
        },
    )
    result = curs.fetchall()
    return result


def show_gunpla_info(result, select):
    console.print(Gunpla_Table_View().create_gunpla_info_table(result, select))


def add_gunpla_task(bandai_id, task):

    with conn:
        curs.execute(
            "INSERT into gunpla_log bandai_id :bandai_id, build_date :build_date, title :title, item_type :item_type, status :status",
            {
                "bandai_id": bandai_id,
                "task": task,
                "build date": datetime.now().date,
            },
        )


def change_position(old_position: int, new_position: int, commit=True):
    with conn:
        curs.execute(
            "UPDATE gunpla_log set task_id = :new_position where task_id = :old_position",
            {"old_position": old_position, "new_position": new_position},
        )
        if commit:
            conn.commit()


def update_gunpla_task(bandai_id: str, task=None):
    with conn:
        if task is not None:
            curs.execute(
                "UPDATE gunpla_log set task = :task where bandai_id = :bandai_id",
                {"task": "%" + task + "%", "bandai_id": "%" + bandai_id + "%"},
            )
        else:
            print(Exception("Task is not added. Please update with correct Task"))


def delete_gunpla_task(task_id: str):
    with conn:
        if task_id is not None:
            curs.execute(
                "DELETE from gunpla_log where task_id = :task_id", {"task_id": task_id}
            )

        for pos in range(task_id + 1, 100):
            change_position(task_id, task_id - 1)


def navigate_gunpla(console, selected=0):
    console.clear()
    result = search_gunpla("Aerial", "")
    show_gunpla_info(result, selected)


def main():

    conn = sqlite3.connect(db_location)
    conn.create_function("regexp", 2, regexp)
    curs = conn.cursor()

    console = Console()

    selected = 0
    navigate_gunpla(console)

    while True:
        ch = readkey()
        if ch == key.UP:
            selected = max(0, selected - 1)
        if ch == key.DOWN:
            selected = min(100, selected + 1)
        if ch == key.ENTER:
            inquirer.confirm("Do you want to add to the database ?").execute()
            inquirer.select(
                "Please confirm state of task",
                ["Planning", "Acquired", "Building", "Completed", "On Hold", "Dropped"],
            ).execute()
            break
        navigate_gunpla(console, selected)


# create_table()


if __name__ == "__main__":
    main()
