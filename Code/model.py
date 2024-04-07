from datetime import datetime
import string
import sqlite3


def create_table():

    conn = sqlite3.connect("gunpla_log.db")
    curs = conn.cursor()

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


create_table()


class gunpla_log:

    def __init__(
        self,
        bandai_id: string,
        build_date: datetime,
        start_time: datetime,
        end_time: datetime,
        task: string,
    ):
        self.bandai_id = bandai_id
        self.build_date = datetime.strptime(build_date, "%d/%m/%Y").date()
        self.start_time = datetime.strptime(start_time, "%H:%M:%S")
        self.end_time = datetime.strptime(end_time, "%H:%M:%S")
        self.task = task


gun_log = gunpla_log("123124", "05/04/2024", "12:21:00", "22:21:00", "asdfadsf")
print(gun_log)
