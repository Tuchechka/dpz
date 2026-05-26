import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Створює логер з форматом '[time] [level] [module] message'.
    Викликати в кожному модулі: log = get_logger(__name__)
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # вже налаштований

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(handler)
    return logger