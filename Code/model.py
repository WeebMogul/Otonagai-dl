from datetime import datetime
import string
import sqlite3


class gunpla_log:

    def __init__(
            self,
            bandai_id: string,
            build_date: datetime,
            task_id: string,
            task: string,
    ):
        self.bandai_id = bandai_id
        self.build_date = datetime.strptime(build_date, "%d/%m/%Y").date()
        self.task = task
        self.task_id = task_id
        self.multiple_build = False

    def __repr__(self):
        return f"{self.bandai_id} , {self.build_date} , {self.task}"


if __name__ == "__main__":
    g1 = gunpla_log("123124", "05/04/2024", "TSK_01", "Planned",)
    g2 = gunpla_log("123124", "05/04/2024", "TSK_02", "Acquired", )
    g3 = gunpla_log("123124", "05/04/2024", "TSK_03", "Building", )
    g4 = gunpla_log("123124", "05/04/2024", "TSK_04", "Completed", )

    print(g2)
