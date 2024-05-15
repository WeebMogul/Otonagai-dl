import logging
from rich.logging import RichHandler

FORMAT = (
    "%(asctime)s [%(levelname)s] [%(name)s] - %(message)s (%(filename)s:%(lineno)d)"
)
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        logging.FileHandler(
            "./Data/otonagai_log.log",
        ),
    ],
)


def log_msg(message):
    logging.info(message)
