import logging


class BaseTransport(object):
    """Base class for Transports that sets up proper logging.
    """

    def __init__(self, disposition, request, parent_logger):
        self.disposition = disposition
        self.request = request
        self.parent_logger = parent_logger

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.INFO)
        self.log.parent = parent_logger
