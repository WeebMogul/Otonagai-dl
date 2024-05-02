from rich.table import Table
from rich.style import Style
from datetime import datetime
from readchar import key


class Gunpla_Table_View:

    def __init__(self):
        self.table = None
        self.selected = Style(color="blue", bgcolor="white", bold=True)

    def create_gunpla_info_table(self, gunpla_log, select, entered=False):

        self.table = Table(title=f"Gunpla Collection {datetime.now().date()}")

        self.table.add_column("Code", justify="center", no_wrap=True)
        self.table.add_column("Title", no_wrap=False)
        self.table.add_column("Series", no_wrap=False)
        self.table.add_column("Item Type")
        self.table.add_column("Release Date")

        for i, col in enumerate(gunpla_log):
            if i == select and entered == key.ENTER:
                self.table.add_row(*col, style=self.selected)
                return [col[0], col[1], col[3]]
            elif i == select:
                self.table.add_row(*col, style=self.selected)
            else:
                self.table.add_row(*col)

        return self.table

    def create_gunpla_log_table(self, gunpla_log, select, entered=False):

        self.table = Table(title=f"Gunpla Log {datetime.now().date()}")

        self.table.add_column("Log ID", justify="left", no_wrap=True)
        self.table.add_column("Code", justify="center", no_wrap=True)
        self.table.add_column("Name", justify="center")
        self.table.add_column("Item Type", justify="center")
        self.table.add_column("Status", justify="left")

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
