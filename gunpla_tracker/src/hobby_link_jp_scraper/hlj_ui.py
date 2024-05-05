from rich.live import Live
from rich.table import Table
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)
from rich.layout import Layout
from rich import print
from rich.panel import Panel
import time
import asyncio


class HLJ_scraper_ui:

    def __init__(self):
        self.row_count = 0

    def create_layout(self, total_length):
        self.scrape_bar = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            TimeRemainingColumn(),
        )

        self.scrape_table = Table.grid(expand=True)
        self.download_progress_task = self.scrape_bar.add_task(
            "Scraping product info", total=total_length
        )

        self.scrape_layout = Layout(ratio=1, minimum_size=8)
        self.scrape_layout.split_column(
            Layout(name="left", ratio=1), Layout(name="right", ratio=6)
        )

    async def update_layout(self):
        self.scrape_layout["left"].update(self.loading_panel)
        self.scrape_layout["right"].update(self.table_panel)

    async def get_progress(self):

        self.loading_panel = Panel(
            self.scrape_bar, title="Downloads", border_style="green", padding=(1, 1)
        )

        self.table_panel = Panel(
            self.scrape_table, title="Contents", border_style="red", padding=(1, 1)
        )

        await self.update_layout()

        return self.scrape_layout

    async def update_bar(self):
        self.scrape_bar.update(self.download_progress_task, advance=1)

    async def update_table(self, message):

        self.row_count += 1
        if self.row_count % 20 == 0:
            self.scrape_table = Table.grid(expand=True)

        self.scrape_table.add_row(message)
        self.table_panel = Panel(
            self.scrape_table, title="Contents", border_style="red", padding=(1, 1)
        )


class HLJ_page_scraper_ui(HLJ_scraper_ui):

    def __init__(self, total_length):
        self.scrape_bar = Progress(
            TextColumn("[progress.description]{task.description}"),
            SpinnerColumn(),
        )

        self.download_progress_task = self.scrape_bar.add_task(
            "Scraping product info", total=total_length
        )

    def update_bar(self) -> None:
        self.scrape_bar.update(self.download_progress_task, advance=1)


async def do_shit(hlj_ui, num):
    await hlj_ui.update_bar()
    await hlj_ui.update_table(num, f"Adding {num} to table")
    await hlj_ui.update_layout()


async def main():

    hlj_ui = HLJ_scraper_ui()
    hlj_ui.create_layout(100)

    loading_bar = await hlj_ui.get_progress()

    with Live(loading_bar) as live:
        for num in range(1, 100):
            time.sleep(0.5)
            await do_shit(hlj_ui, num)
            live.update(loading_bar)


if __name__ == "__main__":
    asyncio.run(main())
