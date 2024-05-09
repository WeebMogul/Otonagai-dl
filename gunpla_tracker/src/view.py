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

            There seems to be an issue with the urls you have provided.
            
            Here are some reasons:

            - No urls entered.
            - You entered a text instead of a number with the page-related input.
            - The starting page number is more than the ending page number.
            - The product associated with the url is already in the database.
            - The hobbylinkjapan link you entered is not available on the website.

            Try again.
            """
        ),
        title_align="center",
    )


def create_db_warning_panel():

    return Panel(
        Markdown(
            """
            There is no merchandise info added to the database. Please follow the instructions :
            
            - Go to the HobbyLinkJapan website (https://www.hlj.com)
            - Get the link to any of your favourite product or the search result containing multiple pages
            - Choose the "Open URLs" option and paste the links you copied.
            - Close and save the file.
            - Choose the option "Add Merchandise to the database". Follow the onscreen instructions.
            - Now, go the the database.                    
            """
        ),
        title_align="center",
    )


def create_log_warning_panel():

    return Panel(
        Markdown(
            """
            No merch has been added to your log. Please follow the instructions :
            
            - Go to the database
            - Choose any one of the merch in the database
            - Enter 'y' to add to your log.
            - Choose the status of what you're going to do with the merch, to the log.
            - Exit the database.
            - Now, go the the log and check if it is in.                    
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
        self.warning_panel = None

    def database_warning_panel(self):

        self.warning_panel = create_db_warning_panel()
        return self.warning_panel

    def log_warning_panel(self):
        self.warning_panel = create_log_warning_panel()
        return self.warning_panel

    def create_gunpla_info_table(self, console, gunpla_log, select, entered=False):

        self.table = Table()
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
