from rich.table import Table
from rich.style import Style
from readchar import key
from rich.panel import Panel
from rich.markdown import Markdown
from abc import ABC, abstractmethod


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


# Interface for the table UI
class Table_View(ABC):

    # function to enable scrolling on the table
    @abstractmethod
    def _table_scroll():
        pass

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

    """
    Sounds silly, but I'm doing this one because :
    1. The snippet is really nice.
    2. Gotta give credit where it's due.
    3. Don't want to get yanked due to software licensing issues
    """
    # This code snippet is adapted from a discussion post in the [Project Name] GitHub repository
    # Original author: llimllib
    # License: MIT License
    # URL: https://github.com/Textualize/rich/discussions/1785

    # The full text of the MIT License can be found in the LICENSE file at the root of this project.
    def _table_scroll(self, size, rows, select):
        if len(rows) + 3 > size:
            if select < size / 2:
                rows = rows[:size]
            elif select + size / 2 > len(self.gunpla_log):
                rows = rows[-size:]
                select -= len(self.gunpla_log) - size
            else:
                rows = rows[select - size // 2 : select + size // 2]
                select -= select - size // 2

        return rows, select

    def warning_panel(self):
        return create_db_warning_panel()

    def create_table(self, console, gunpla_log, select, entered=False):
        self.table = Table(title="Database Table")
        self.table.add_column(
            "Code",
            justify="center",
        )
        self.table.add_column(
            "Title",
        )
        self.table.add_column(
            "Series",
        )
        self.table.add_column(
            "Item Type",
        )
        self.table.add_column(
            "Manufacturer",
        )
        self.table.add_column(
            "Release Date",
        )

        size = console.height - 6
        rows, select = self._table_scroll(size, gunpla_log, select)

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

    """
    Sounds silly, but I'm doing this one because :
    1. The snippet is really nice.
    2. Gotta give credit where it's due.
    3. Don't want to get yanked due to software licensing issues, since it's my first time doing this.
    """
    # This code snippet is adapted from a discussion post in the [Project Name] GitHub repository
    # Original author: llimllib
    # License: MIT License
    # URL: https://github.com/Textualize/rich/discussions/1785

    # The full text of the MIT License can be found in the LICENSE file at the root of this project.

    def _table_scroll(self, size, rows, select):
        if len(rows) + 6 > size:
            if select < size / 2:
                rows = rows[:size]
            elif select + size / 2 > len(self.gunpla_log):
                rows = rows[-size:]
                select -= len(self.gunpla_log) - size
            else:
                rows = rows[select - size // 2 : select + size // 2]
                select -= select - size // 2

        return rows, select

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

        size = console.height - 6
        rows, select = self._table_scroll(size, gunpla_log, select)

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
