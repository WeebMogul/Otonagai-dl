import requests
from bs4 import BeautifulSoup
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
import time

# from gunpla_info_scraper import Gunpla_Info
import asyncio
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
from rich.align import Align
from rich.prompt import Prompt

console = Console()
for i in range(0, 10):
    console.print(Panel("Hello World"))
