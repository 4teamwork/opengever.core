class ValidationError(Exception):
    pass


class MissingGUID(ValidationError):
    pass


class DuplicateGUID(ValidationError):
    pass


class MissingParent(ValidationError):
    pass
