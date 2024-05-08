from rich.table import Table
from rich.style import Style
from datetime import datetime
from readchar import key
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown


def no_downloads():

    return Panel(
        Markdown(
            """
            
            There is an issue with the urls you have entered in the file. Some of the issues could be:
            
            - No urls entered.
            - You entered a text instead of a number with the page-related input.
            - The starting page number is more than the ending page number.
            
            Try again.
            """
        ),
        title_align="center",
    )


def table_scroll(size, gunpla_log, select):

    if len(gunpla_log) + 3 > size:
        if select < size / 2:
            gunpla_log = gunpla_log[:size]
        elif (select + size) / 2 > len(gunpla_log):
            gunpla_log = gunpla_log[-size:]
            select -= len(gunpla_log) - size
        else:
            gunpla_log = gunpla_log[select - size // 2 : select + size // 2]
            select -= select - size // 2

    return gunpla_log, select


class Gunpla_Table_View:

    def __init__(self):
        self.table = None
        self.selected = Style(color="blue", bgcolor="white", bold=True)

    def create_warning_panel(self, message):

        self.warning_panel = Panel(message, title_align="center")
        return self.warning_panel

    def create_gunpla_info_table(self, console, gunpla_log, select, entered=False):

        self.table = Table(title=f"Gunpla Collection {datetime.now().date()}")
        self.table.add_column("Code", justify="center", no_wrap=True)
        self.table.add_column("Title", no_wrap=False)
        self.table.add_column("Series", no_wrap=False)
        self.table.add_column("Item Type")
        self.table.add_column("Manufacturer")
        self.table.add_column("Release Date")

        size = console.height - 4

        gunpla_log, select = table_scroll(size, gunpla_log, select)

        for i, col in enumerate(gunpla_log):
            self.table.add_row(*col, style=self.selected if i == select else None)
            if i == select and entered == key.ENTER:
                return [col[0], col[1], col[3]]

        return self.table

    def create_gunpla_log_table(self, console, gunpla_log, select, entered=False):

        self.table = Table()

        self.table.add_column("Log ID", justify="left", no_wrap=True)
        self.table.add_column("Code", justify="center", no_wrap=True)
        self.table.add_column("Name", justify="center")
        self.table.add_column("Item Type", justify="center")
        self.table.add_column("Status", justify="left")

        size = console.height - 4

        gunpla_log, select = table_scroll(size, gunpla_log, select)

        for i, col in enumerate(gunpla_log):
            if i == select and (entered == key.ENTER or entered == key.DELETE):
                self.table.add_row(
                    str(col[0]), col[1], col[2], col[3], col[4], style=self.selected
                )
                return [col[0], col[1], col[2], col[3], col[4]]
            elif i == select:
                self.table.add_row(
                    str(col[0]), col[1], col[2], col[3], col[4], style=self.selected
                )
            else:
                self.table.add_row(str(col[0]), col[1], col[2], col[3], col[4])

        return self.table
