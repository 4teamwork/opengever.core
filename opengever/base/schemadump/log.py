from logging import Formatter
from logging import StreamHandler
import logging


def setup_logging(name):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    log.propagate = False
    handler = StreamHandler()
    handler.setFormatter(Formatter(''))
    handler.setLevel(logging.INFO)
    log.addHandler(handler)
    return log
