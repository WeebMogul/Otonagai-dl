from rich.console import Console
from InquirerPy import inquirer
from abc import ABC, abstractmethod
from readchar import readkey, key
from InquirerPy import inquirer
from rich.live import Live
import time
import logging
import os
from rich.panel import Panel

console = Console()


def basic_or_advanced_search(model):

    search_flag = None
    if len(model.view_table()) > 1:
        if inquirer.confirm(
            "Do you want to proceed with advanced search or regular search"
        ).execute():
            search_result = model.advanced_view_table()
            search_flag = "Advanced"
        else:
            search_result = model.view_table()
            search_flag = "Basic"
    else:
        search_result = []

    return search_result, search_flag


# Interface for the navigation classes for db and log
class Navigation(ABC):

    @abstractmethod
    def navigate_table(self):
        pass

    @abstractmethod
    def no_data_warning(self):
        pass


class search_table_navigation(Navigation):

    def __init__(self, model, view, console):

        self.model = model
        self.view = view
        self.console = console

    # If data is not available in database, return Markdown notif.
    def no_data_warning(self, search_result):
        if len(search_result) < 1:
            self.console.print(self.view.warning_panel())
            time.sleep(5)
            return None

    def navigate_table(self):
        selected = 0
        # choice for advanced or full db table
        search_result, flag = basic_or_advanced_search(self.model)

        # check if data is available in the db
        if flag is None:
            self.no_data_warning(search_result)

        # clear the console
        self.console.clear()

        with Live(
            self.view.create_table(self.console, search_result, selected),
            auto_refresh=False,
            screen=True,
        ) as live:

            while True:

                if len(search_result) < 1:
                    break

                # read keyboard input
                ch = readkey()

                # selected entry on the table
                selected_gunpla = self.view.create_table(
                    self.console, search_result, selected, ch
                )

                if ch == key.UP:
                    selected = max(0, selected - 1)
                elif ch == key.DOWN:
                    selected = min(len(search_result) - 1, selected + 1)
                if ch == key.ENTER:
                    live.stop()

                    if inquirer.confirm(
                        f"Do you want to add {selected_gunpla[1]} to the log ?"
                    ).execute():
                        # live.stop()
                        self.model.insert_to_table(
                            selected_gunpla[0],
                            selected_gunpla[1],
                            selected_gunpla[2],
                        )

                    # stop and then restart the function
                    if flag == "Basic":
                        os.system("cls" if os.name == "nt" else "clear")
                        live.start(refresh="True")
                    else:
                        break

                elif ch == key.ESC:
                    if inquirer.confirm(
                        "\n\n Do you want to go back to the main menu ?"
                    ).execute():
                        break
                    else:
                        os.system("cls" if os.name == "nt" else "clear")
                        live.start(refresh=True)

                live.update(
                    self.view.create_table(
                        self.console,
                        self.model.view_table(),
                        selected,
                    ),
                    refresh=True,
                )


class log_table_navigation:

    def __init__(self, model, view, console):

        self.model = model
        self.view = view
        self.console = console

    def no_data_warning(self, log_result):
        if len(log_result) < 1:
            self.console.print(self.view.warning_panel())
            time.sleep(5)
            return None

    def navigate_table(self):
        selected = 0

        log_result = self.model.view_table()
        self.no_data_warning(log_result)

        self.console.clear()
        with Live(
            self.view.create_table(
                self.console,
                log_result,
                selected,
            ),
            auto_refresh=False,
        ) as live:

            while True:

                if len(log_result) < 1:
                    break
                ch = readkey()

                selected_log = self.view.create_table(
                    self.console, log_result, selected, ch
                )

                if ch == key.UP:
                    selected = max(0, selected - 1)
                elif ch == key.DOWN:
                    selected = min(len(log_result) - 1, selected + 1)

                # Update the status of the product build
                elif ch == key.ENTER:
                    live.stop()
                    self.model.update_table(selected_log[0])

                    os.system("cls" if os.name == "nt" else "clear")
                    live.start(refresh=True)

                # delete the product from the log
                elif ch == key.DELETE:
                    live.stop()
                    self.model.delete_from_table(selected_log[0])

                    # update the table with the new changes
                    log_result = self.model.view_table()
                    selected_log = self.view.create_table(
                        self.console, log_result, selected, ch
                    )
                    selected = 0

                    os.system("cls" if os.name == "nt" else "clear")
                    live.start(refresh=True)

                elif ch == key.ESC:
                    if inquirer.confirm(
                        "\n\n Do you want to go back to the main menu ?"
                    ).execute():
                        break
                    else:
                        os.system("cls" if os.name == "nt" else "clear")
                        live.start(refresh=True)

                live.update(
                    self.view.create_table(
                        self.console,
                        self.model.view_table(),
                        selected,
                    ),
                    refresh=True,
                )
