from zope.schema import ValidationError
from zope.schema.interfaces import InvalidURI


class UnknownField(ValidationError):
    """Encountered an unexpected, extra field that's not part of the schema.
    """


class InvalidBase64DataURI(InvalidURI):
    """The given URI is not a valid data URI using Base64 encoding.
    """
