import sqlite3
from rich.console import Console
from rich.table import Table
import os

conn = sqlite3.connect(f"{os.getcwd()}/gunpla.db")
curs = conn.cursor()

collections = curs.execute(
    "SELECT bandai_id,title, series, item_type from gunpla where title like (?);",
    ("%" + "gundam barbatos" + "%",),
)

console = Console()


class Gunpla_Table_View:

    def __init__(self, gunpla_info):
        self.gunpla_info = gunpla_info

    def create_table(self):

        self.table = Table(title="Gunpla Collection")

        self.table.add_column("bandai_id", justify="center")
        self.table.add_column("title")
        self.table.add_column("series")
        self.table.add_column("item_type")

        for col in self.gunpla_info:
            self.table.add_row(col[0], col[1], col[2], col[3])

        return self.table
