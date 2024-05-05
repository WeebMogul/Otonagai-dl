import sqlite3
from .view import Gunpla_Table_View
from rich.console import Console
from InquirerPy import inquirer
import re
from abc import ABC, abstractmethod
from readchar import readkey, key
from InquirerPy import inquirer
from datetime import datetime
from .model import gunpla_log_db, gunpla_search_db
from rich.live import Live
import time
import sys
import os

console = Console()


class Navigation(ABC):

    @abstractmethod
    def navigate_table(self):
        pass

    @abstractmethod
    def _create_warning_panel():
        pass


class navigate_search_table(Navigation):

    def _create_warning_panel(self, search_result):
        if len(search_result) < 1:
            console.print(
                self.view.create_warning_panel(
                    "There is no data available. Please add new links to the database"
                )
            )
            time.sleep(5)
            return None

    def __init__(self, model, view):

        self.model = model
        self.view = view

    def navigate_table(self):
        selected = 0

        search_result = self.model.view_table()

        self._create_warning_panel(search_result)

        with Live(
            self.view.create_gunpla_info_table(console, search_result, selected),
            auto_refresh=False,
        ) as live:

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

                    if inquirer.confirm("Do you want to add to the log ?").execute():
                        self.model.insert_to_table(
                            search_result[selected][0],
                            search_result[selected][1],
                            search_result[selected][2],
                        )

                    else:
                        break

                    live.start(refresh=True)

                if ch == key.ESC:
                    if inquirer.confirm(
                        "\n\n Do you want to go back to the main menu ?"
                    ).execute():

                        break
                    else:

                        os.system("cls")
                        live.start(refresh=True)

                live.update(
                    self.view.create_gunpla_info_table(
                        console, search_result, selected
                    ),
                    refresh=True,
                )


class navigate_log_table:

    def __init__(self, model, view):

        self.model = model
        self.view = view

    def _create_warning_panel(self, log_result):
        if len(log_result) < 1:
            console.print(
                self.view.create_warning_panel(
                    "There is no merchandise in the log. Add the products to the database and then change it."
                )
            )
            time.sleep(5)
            return None

    def navigate_table(self):
        selected = 0

        log_result = self.model.view_table()
        self._create_warning_panel(log_result)

        console.clear()
        with Live(
            self.view.create_gunpla_log_table(
                console,
                log_result,
                selected,
            ),
            auto_refresh=False,
        ) as live:

            while True:

                if len(log_result) < 1:
                    break
                ch = readkey()

                selected_gunpla = self.view.create_gunpla_log_table(
                    console, log_result, selected, ch
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
                        console, log_result, selected, ch
                    )

                    console.clear()
                    live.start()
                    live.refresh()

                if ch == key.DELETE:
                    live.stop()
                    self.model.delete_from_table(selected_gunpla[0])

                    log_result = self.model.view_table()
                    selected_gunpla = self.view.create_gunpla_log_table(
                        console, log_result, selected, ch
                    )

                    console.clear()
                    live.start()
                    live.refresh()

                if ch == key.ESC:
                    if inquirer.confirm(
                        "\n\n Do you want to go back to the main menu ?"
                    ).execute():
                        break
                    else:
                        os.system("cls")
                        live.start(refresh=True)

                live.update(
                    self.view.create_gunpla_log_table(console, log_result, selected),
                    refresh=True,
                )
