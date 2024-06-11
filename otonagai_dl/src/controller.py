from rich.console import Console
from InquirerPy import inquirer
from abc import ABC, abstractmethod
from readchar import readkey, key
from InquirerPy import inquirer
from rich.live import Live
import time
import os
from .log_system import log_msg

console = Console()


def force_restart(live: Live):
    os.system("cls" if os.name == "nt" else "clear")
    live.start(refresh=True)


def basic_or_advanced_search(model):

    search_flag = None
    if len(model.view_table()) >= 1:
        search_flag = inquirer.select(
            "Do you want to proceed with advanced search or regular search",
            choices=["Advanced", "Basic"],
        ).execute()

        if search_flag == "Advanced":
            search_result = model.advanced_view_table()
        elif search_flag == "Basic":
            search_result = model.view_table()
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
        os.system("cls" if os.name == "nt" else "clear")

        with Live(
            self.view.create_table(self.console, search_result, selected),
            auto_refresh=False,
            screen=True,
        ) as live:

            while len(search_result) >= 1:

                # read keyboard input
                typed_key = readkey()
                # log_msg(f"Key typed : {ch}")

                # selected entry on the table
                selected_gunpla = self.view.create_table(
                    self.console, search_result, selected, typed_key
                )

                match typed_key:
                    case key.UP:
                        selected = max(0, selected - 1)
                    case key.DOWN:
                        selected = min(len(search_result) - 1, selected + 1)
                    case key.ENTER:
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
                            force_restart(live)
                        elif flag == "Advanced":
                            break

                    case key.CTRL_D:

                        live.stop()
                        if inquirer.confirm(
                            "Do you want to go back to the main menu ?"
                        ).execute():
                            break

                        force_restart(live)
                live.update(
                    self.view.create_table(
                        self.console,
                        search_result,
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

        os.system("cls" if os.name == "nt" else "clear")
        with Live(
            self.view.create_table(
                self.console,
                log_result,
                selected,
            ),
            auto_refresh=False,
            screen=True,
        ) as live:

            while len(log_result) >= 1:

                typed_key = readkey()

                selected_log = self.view.create_table(
                    self.console, log_result, selected, typed_key
                )

                match typed_key:
                    case key.UP:
                        selected = max(0, selected - 1)
                    case key.DOWN:
                        selected = min(len(log_result) - 1, selected + 1)
                    case key.ENTER:
                        live.stop()
                        self.model.update_table(selected_log[0], selected_log[2])
                        force_restart(live)
                    case key.DELETE:
                        live.stop()
                        self.model.delete_from_table(selected_log[0], selected_log[2])

                        # update the table with the new changes
                        log_result = self.model.view_table()
                        selected_log = self.view.create_table(
                            self.console, log_result, selected, typed_key
                        )
                        selected = 0
                        force_restart(live)
                    case key.CTRL_D:
                        live.stop()
                        if inquirer.confirm(
                            "Do you want to go back to the main menu ?"
                        ).execute():
                            break
                        force_restart(live)

                live.update(
                    self.view.create_table(
                        self.console,
                        self.model.view_table(),
                        selected,
                    ),
                    refresh=True,
                )
