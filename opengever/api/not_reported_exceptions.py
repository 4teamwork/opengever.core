from zExceptions import BadRequest as _BadRequest


class NotReportedException(Exception):
    """An exception that is not reported in sentry
    """


class BadRequest(_BadRequest, NotReportedException):
    """BadRequest that is not reported in sentry.

    This class needs to be named BadRequest so that ZPublisher's HTTPResponse
    will set the status code to 400, and so that the API will return BadRequest
    as error type.
    """
