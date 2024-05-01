import sqlite3
from .view import Gunpla_Table_View
from rich.console import Console
from InquirerPy import inquirer
import re
from abc import ABC, abstractmethod
from curses import wrapper
from readchar import readkey, key
from InquirerPy import inquirer
from datetime import datetime
from .model import gunpla_log_db, gunpla_search_db
from rich.live import Live
import time
import sys

console = Console()


class Navigation(ABC):

    @abstractmethod
    def navigate_table(self):
        pass


class navigate_search_table(Navigation):

    def __init__(self, model, view):

        self.model = model
        self.view = view

    def navigate_table(self):
        selected = 0

        console.clear()
        search_result = self.model.view_table()

        if not search_result:
            print("Gundam kit does not exist. Returning to search bar")
            time.sleep(3)
            self.navigate_table()

        gunpla_search_table = self.view.create_gunpla_info_table(
            search_result,
            selected,
        )

        with Live(gunpla_search_table, auto_refresh=False) as live:
            # console.clear()
            while True:
                ch = readkey()
                if ch == key.UP:
                    selected = max(0, selected - 1)
                if ch == key.DOWN:
                    selected = min(len(search_result) - 1, selected + 1)
                if ch == key.ENTER:
                    live.stop()
                    self.selected_gunpla = self.view.create_gunpla_info_table(
                        search_result, selected, ch
                    )
                    if self.model.insert_to_table(
                        self.selected_gunpla[0],
                        self.selected_gunpla[1],
                        self.selected_gunpla[2],
                    ):
                        self.navigate_table()
                    else:
                        break

                # if ch == key.ESC:
                #     live.stop()
                #     if inquirer.confirm(
                #         "Do you want to go back to the main menu ?"
                #     ).execute():
                #         return True
                #     else:
                #         self.navigate_table()

                live.update(
                    self.view.create_gunpla_info_table(search_result, selected, ch),
                    refresh=True,
                )


class navigate_log_table:

    def __init__(self, model, view):

        self.model = model
        self.view = view

    def do_something_if_enter(self, log_id):
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
        with self.conn:
            self.curs.execute(
                "UPDATE gunpla_log set status = :status where log_id = :log_id",
                {
                    "status": log_state,
                    "log_id": log_id,
                },
            )

        return True

    def navigate_table(self):
        selected = 0

        console.clear()
        result = self.model.view_table()
        gunpla_log_table = self.view.create_gunpla_log_table(
            result,
            selected,
        )
        with Live(gunpla_log_table, auto_refresh=False) as live:
            #  console.clear()
            while True:
                ch = readkey()
                selected_gunpla = self.view.create_gunpla_log_table(
                    result, selected, ch
                )

                if ch == key.UP:
                    selected = max(0, selected - 1)
                if ch == key.DOWN:
                    selected = min(len(result) - 1, selected + 1)
                if ch == key.ENTER:
                    live.stop()
                    self.model.update_table(selected_gunpla[0])
                    self.navigate_table()
                if ch == key.DELETE:
                    live.stop()
                    self.model.delete_from_table(selected_gunpla[0])
                    self.navigate_table()
                if ch == key.ESC:
                    exit_request = inquirer.confirm(
                        "Do you want to go back to the main menu ?"
                    ).execute()
                    if exit_request:
                        live.stop()
                        break

                live.update(
                    self.view.create_gunpla_log_table(result, selected),
                    refresh=True,
                )
