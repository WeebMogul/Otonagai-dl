import logging
from rich.logging import RichHandler

FORMAT = (
    "%(asctime)s [%(levelname)s] [%(name)s] - %(message)s (%(filename)s:%(lineno)d)"
)
logging.basicConfig(
    level="DEBUG",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        logging.FileHandler(
            "./foo.log",
        ),
        RichHandler(rich_tracebacks=True, show_path=True, console=None),
    ],
)


# log = logging.getLogger("Rich")
def log_msg(message):
    logging.debug(message)
