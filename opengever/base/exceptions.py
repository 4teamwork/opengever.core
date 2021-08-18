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


class UnsupportedTypeForRemoteURL(Exception):
    """The Oguid does not refer to one of the types that get_remote_url() is
    supported for.
    """


class NonRemoteOguid(Exception):
    """An attempt was made to use get_remote_url() on a Oguid for an object
    that is located on the current AdminUnit.
    """


class IncorrectConfigurationError(Exception):
    """Exception raised when Gever is not configured correctly
    """


class ReferenceNumberCannotBeFreed(Exception):
    """Exception raised when trying to free a reference number
    that is still in use.
    """
