from rich.table import Table
from rich.style import Style
from datetime import datetime


class Gunpla_Table_View:

    def __init__(self):
        self.table = None

    def create_gunpla_info_table(self, gunpla_info, select):

        selected = Style(color="blue", bgcolor="white", bold=True)

        self.table = Table(title=f"Gunpla Collection {datetime.now().date()}")

        self.table.add_column("Code", justify="center", no_wrap=True)
        self.table.add_column("title", no_wrap=False)
        self.table.add_column("series", no_wrap=False)
        self.table.add_column("item_type")
        self.table.add_column("release_date")

        for i, col in enumerate(gunpla_info):
            if i == select:
                self.table.add_row(*col, style=selected)
            else:
                self.table.add_row(*col)

        return self.table

    def create_gunpla_log_table(self, gunpla_log):

        self.table = Table(title=f"Gunpla Log {datetime.now().date()}")

        self.table.add_column("bandai_id", justify="center", no_wrap=True)
        self.table.add_column("build date", justify="center")
        self.table.add_column("task", justify="left")

        for col in gunpla_log:
            self.table.add_row(col[0], col[1], col[2])

        return self.table
