class TransportationError(Exception):
    """A object could not be transported from or to another client.
    """


class MalformedOguid(Exception):
    """The Oguid is invalid and does not meet the required format of
    <admin_unit_id>:<int_id>.
    """


class InvalidOguidIntIdPart(Exception):
    """The int_id part of the oguid is invalid and does not exist.
    """
