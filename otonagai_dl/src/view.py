from rich.table import Table
from rich.style import Style
from readchar import key
from rich.panel import Panel
from rich.markdown import Markdown
from abc import ABC, abstractmethod
from rich.console import Console
from .warning_shots import (
    create_db_warning_panel,
    create_log_warning_panel,
)


def color_by_status(category):
    color_map = {
        "Planning": "#ffffff",
        "Acquired": "#e7b416",
        "Building": "#baffb9",
        "Completed": "#2dc937",
        "On Hold": "#db7b2b",
        "Dropped": "#cc3232",
    }

    return color_map.get(category, "white")


def table_scroll(size, rows, select, search_table_length):

    # check if th the len of the current rows is greater than the console height
    if len(rows) + 2 > size:

        # if the select variable contains a no. less than half the size, return a list of rows from 0 to the console height
        if select < (size / 2):
            rows = rows[:size]

        # if reach to the end of the search_table_length, then show from the end to the current console height and reset the select value
        elif select + (size / 2) > search_table_length:
            rows = rows[-size:]
            select -= search_table_length - size
        else:
            # if in the middle, show the inbetweens.
            rows = rows[select - (size // 2) : select + (size // 2)]
            select = size // 2

    return rows, select


# Interface for the table UI
class Table_View(ABC):

    # return a markdown panel of a warning
    @abstractmethod
    def warning_panel():
        pass

    # create the table UI
    @abstractmethod
    def create_table():
        pass


class Search_Table_View(Table_View):

    def __init__(self, gunpla_log):
        self.table = None
        self.selected = Style(color="blue", bgcolor="white", bold=True)
        self.gunpla_log = gunpla_log

    def warning_panel(self):
        return create_db_warning_panel()

    def create_table(self, console, gunpla_log, select, entered=False):
        self.table = Table(title="Database Table")
        self.table.add_column("Code", justify="center", no_wrap=True)
        self.table.add_column("Title")
        self.table.add_column(
            "Series",
        )
        self.table.add_column("Item Type", no_wrap=True)
        self.table.add_column(
            "Manufacturer",
        )
        self.table.add_column("Release Date", no_wrap=True)

        size = console.height - 12
        rows, select = table_scroll(
            size=size,
            rows=gunpla_log,
            select=select,
            search_table_length=len(gunpla_log),
        )

        for i, col in enumerate(rows):
            self.table.add_row(*col, style=self.selected if i == select else None)
            if i == select and entered == key.ENTER:
                return [col[0], col[1], col[3]]

        return self.table


class Log_Table_View(Table_View):

    def __init__(self, gunpla_log):
        self.table = None
        self.selected = Style(bgcolor="white", bold=True, color="black")
        self.gunpla_log = gunpla_log

    def warning_panel(self):
        return create_log_warning_panel()

    def create_table(self, console, gunpla_log, select, entered=False):
        self.table = Table(title="Log Table")

        # self.table.add_column("Log ID", justify="left", style="cyan")
        self.table.add_column(
            "Code",
            justify="center",
        )
        self.table.add_column(
            "Name",
            justify="center",
        )
        self.table.add_column(
            "Item Type",
            justify="center",
        )
        self.table.add_column(
            "Status",
            justify="left",
        )

        # display the list of items currently on the table
        size = console.height - 12
        rows, select = table_scroll(
            size=size,
            rows=gunpla_log,
            select=select,
            search_table_length=len(gunpla_log),
        )

        for i, col in enumerate(rows):
            color = color_by_status(col[4])
            if i == select and entered in [key.ENTER, key.DELETE]:
                self.table.add_row(col[1], col[2], col[3], col[4], style=self.selected)
                return [col[0], col[1], col[2], col[3], col[4]]
            elif i == select:
                self.table.add_row(col[1], col[2], col[3], col[4], style=self.selected)
            else:
                self.table.add_row(
                    f"[{color}]{col[1]}[/{color}]",
                    f"[{color}]{col[2]}[/{color}]",
                    f"[{color}]{col[3]}[/{color}]",
                    f"[{color}]{col[4]}[/{color}]",
                )

        return self.table
