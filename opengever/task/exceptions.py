class TaskException(Exception):
    """Base exception class for custom task exceptions."""


class CannotAcceptTaskException(TaskException):
    pass
