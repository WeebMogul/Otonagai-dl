import sqlite3
from view import Gunpla_Table_View
from rich.console import Console

conn = sqlite3.connect("gunpla.db")
curs = conn.cursor()
console = Console()


def create_table():

    with conn:
        curs.execute(
            """
                     CREATE TABLE IF NOT EXISTS gunpla_log(
                         bandai_id text,
                         build_date date,
                         start_time date,
                         end_time date,
                         task text
                     )
                     """
        )


def search_gunpla(title, series, item_type):

    curs.execute(
        "SELECT bandai_id, title, series, item_type from gunpla where title like :title and series like :series and item_type like :item_type;",
        {
            "title": "%" + title + "%",
            "series": "%" + series + "%",
            "item_type": "%" + item_type + "%",
        },
    )
    result = curs.fetchall()

    console.print(Gunpla_Table_View(result).create_table())


search_gunpla("sazabi", "", "Master Grade")


# create_table()
