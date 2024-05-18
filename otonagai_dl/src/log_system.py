import logging

LOG_FILE_PATH = "./otonagai_dl.log"

FORMAT = (
    "%(asctime)s [%(levelname)s] [%(name)s] - %(message)s (%(filename)s:%(lineno)d)"
)
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode="a"),
    ],
)


def log_msg(message):

    logging.info(message)
