from zope.schema import ValidationError
from zope.schema.interfaces import InvalidURI


class ActionAlreadyExists(Exception):
    """A webaction with the given unique_name already exists.
    """


class UnknownField(ValidationError):
    """Encountered an unexpected, extra field that's not part of the schema.
    """


class InvalidBase64DataURI(InvalidURI):
    """The given URI is not a valid data URI using Base64 encoding.
    """


class ForbiddenTargetUrlParam(ValidationError):
    """The target url contains an invalid query parameter, e.g. a query
    parameter which is already appended to the target url by default.
    """


class UnsupportedTargetUrlPlaceholder(ValidationError):
    """The target url contains unsupported placeholders in the querystring.
    """
