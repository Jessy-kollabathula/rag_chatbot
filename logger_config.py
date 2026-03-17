import logging
import os

# create logs folder if not exists
os.makedirs("logs", exist_ok=True)

def get_logger(name, log_file):

    logger = logging.getLogger(name)

    if not logger.handlers:

        handler = logging.FileHandler(log_file)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        handler.setFormatter(formatter)

        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    return logger