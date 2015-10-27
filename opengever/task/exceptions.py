class TaskException(Exception):
    """Base exception class for custom task exceptions."""


class TaskRemoteRequestError(TaskException):
    pass
