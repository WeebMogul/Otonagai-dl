from datetime import datetime
import os

import rich.box
from rich.console import Console
from rich.style import Style
from rich.table import Table
from readchar import readkey, key

SELECTED = Style(color="blue", bgcolor="white", bold=True)


def print_table(console, table, rows=[], selected=0):
    for i, row in enumerate(rows):
        if i == selected:
            table.add_row(*row, style=SELECTED)
        else:
            table.add_row(*row)

    console.print(table)


def make_table(headers):
    table = Table(box=rich.box.MINIMAL)
    for i in range(len(headers)):
        table.add_column(headers[i])

    return table


UP = "\x1b[A"
DOWN = "\x1b[B"
ENTER = "\r"

selected = 0
console = Console()


def format_ts(ts):
    return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")


# get the first 5 items from os.listdir to show in the table
headers = ["filename", "size (bytes)", "modified"]
items = [
    (fname, str(stat.st_size), format_ts(stat.st_mtime))
    for fname, stat in [(f, os.stat(f)) for f in os.listdir()[:5]]
]

console.clear()
print_table(console, make_table(headers), items, selected)

while True:
    ch = readkey()
    if ch == key.UP:
        selected = max(0, selected - 1)
    if ch == key.DOWN:
        selected = min(len(items) - 1, selected + 1)
    if ch == key.ENTER:
        print("you selected: ", items[selected])
        break
    console.clear()
    print_table(console, make_table(headers), items, selected)
