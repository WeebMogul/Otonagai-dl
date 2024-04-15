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
from rich.live import Live

db_location = r"D:\GitHub\Python-Programming-Projects\Gunpla_Tracker_Database\Gunpla-Tracker\Data\gunpla.db"

console = Console()

conn = sqlite3.connect(db_location)
curs = conn.cursor()


def regexp(y, x, search=re.search):
    return 1 if search(y, x) else 0


def create_table():
    with conn:
        curs.execute(
            """
                     CREATE TABLE IF NOT EXISTS gunpla_log(
                         bandai_id text,
                         title text,
                         item_type date,
                         status text
                     )
                     """
        )


def search_gunpla(title: str = "", series: str = "", item_type: str = ""):

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

    curs.execute(
        "SELECT bandai_id, title, series, item_type, release_date from gunpla where title like :title and series like :series "
        "and item_type like :item_type order by release_date desc limit 10;",
        {
            "title": "%" + search_title + "%",
            "series": "%" + series + "%",
            "item_type": "%" + search_item_type + "%",
        },
    )
    result = curs.fetchall()
    return result


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
            change_position(pos, task_id - 1)


def add_gunpla_log_status(bandai_id: str, title: str, item_type: str):

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
    if inquirer.confirm("Do you want to add to the database ?").execute():
        with conn:
            curs.execute(
                "INSERT into gunpla_log VALUES (:bandai_id, :title, :item_type, :status)",
                {
                    "bandai_id": bandai_id,
                    "title": title,
                    "item_type": item_type,
                    "status": log_state,
                },
            )
            print(f"{title}({bandai_id}) has been added to the database.")

    return_add = inquirer.confirm("Do you want to return to the search bar ?").execute()

    return return_add


def navigate_gunpla(result, selected=0, enter=False):
    # result = search_gunpla()
    return Gunpla_Table_View().create_gunpla_info_table(result, selected, enter)


def main():

    selected = 0
    console.clear()
    result = search_gunpla()

    with Live(navigate_gunpla(result), auto_refresh=False) as live:
        #  console.clear()
        while True:
            ch = readkey()
            if ch == key.UP:
                selected = max(0, selected - 1)
            if ch == key.DOWN:
                selected = min(100, selected + 1)
            if ch == key.ENTER:
                live.stop()
                selected_gunpla = navigate_gunpla(result, selected, ch)
                add_gunpla_log_status(
                    selected_gunpla[0], selected_gunpla[1], selected_gunpla[2]
                )
                # add_gunpla_log_status()
                # if add_gunpla_log_status():
                #     print(navigate_gunpla(result, selected, ch))
                #     main()
                # elif return_menu:
                # main()
                break
            live.update(navigate_gunpla(result, selected, ch), refresh=True)


# create_table()


if __name__ == "__main__":
    create_table()
    main()
