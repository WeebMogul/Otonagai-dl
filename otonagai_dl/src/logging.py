import logging


FORMAT = (
    "%(asctime)s [%(levelname)s] [%(name)s] - %(message)s (%(filename)s:%(lineno)d)"
)
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        logging.FileHandler("./otonagai_dl.log", mode="a"),
    ],
)


def log_msg(message):

    logging.info(message)
