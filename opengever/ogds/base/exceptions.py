class ClientNotFound(Exception):
    """The client could not be found.
    """


class TransportationError(Exception):
    """A object could not be transported from or to another client.
    """
