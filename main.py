from rich.console import Console
import sqlite3
from Code import menu


if __name__ == "__main__":
    # start_args()
    db_location = r"D:\GitHub\Python-Programming-Projects\Gunpla_Tracker_Database\gunpla_tracker\Data\gunpla.db"
    conn = sqlite3.connect(db_location)
    curs = conn.cursor()

    menu.menu(curs, conn)
