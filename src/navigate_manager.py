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
        gunpla_search_table = self.view.create_gunpla_info_table(
            search_result, selected
        )
        with Live(gunpla_search_table, auto_refresh=False) as live:

            while True:

                if len(search_result) < 1:
                    break
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
                    if inquirer.confirm("Do you want to add to the log ?").execute():
                        self.model.insert_to_table(
                            self.selected_gunpla[0],
                            self.selected_gunpla[1],
                            self.selected_gunpla[2],
                        )
                        console.clear()
                        live.start()

                if (
                    ch == key.ESC
                    and inquirer.confirm(
                        "\n\n Do you want to go back to the main menu ?"
                    ).execute()
                ):
                    break
                live.update(
                    self.view.create_gunpla_info_table(search_result, selected),
                    refresh=True,
                )


class navigate_log_table:

    def __init__(self, model, view):

        self.model = model
        self.view = view

    def navigate_table(self):
        selected = 0

        console.clear()
        log_result = self.model.view_table()
        gunpla_log_table = self.view.create_gunpla_log_table(
            log_result,
            selected,
        )
        with Live(gunpla_log_table, auto_refresh=False) as live:

            while True:
                ch = readkey()

                selected_gunpla = self.view.create_gunpla_log_table(
                    log_result, selected, ch
                )

                if ch == key.UP:
                    selected = max(0, selected - 1)
                if ch == key.DOWN:
                    selected = min(len(log_result) - 1, selected + 1)
                if ch == key.ENTER:
                    live.stop()
                    self.model.update_table(selected_gunpla[0])

                    log_result = self.model.view_table()
                    selected_gunpla = self.view.create_gunpla_log_table(
                        log_result, selected, ch
                    )

                    console.clear()
                    live.start()
                    live.refresh()

                if ch == key.DELETE:
                    live.stop()
                    self.model.delete_from_table(selected_gunpla[0])

                    log_result = self.model.view_table()
                    selected_gunpla = self.view.create_gunpla_log_table(
                        log_result, selected, ch
                    )

                    console.clear()
                    live.start()
                    live.refresh()

                if (
                    ch == key.ESC
                    and inquirer.confirm(
                        "\n\n Do you want to go back to the main menu ?"
                    ).execute()
                ):
                    break

                live.update(
                    self.view.create_gunpla_log_table(log_result, selected),
                    refresh=True,
                )
