from zExceptions import BadRequest


class InvalidFieldType(Exception):
    pass


class InvalidFieldTypeDefinition(Exception):
    pass


class InvalidSchemaAssignment(Exception):
    pass


class BadCustomPropertiesFactoryConfiguration(Exception):
    pass


class SheetValidationError(BadRequest):
    pass


class FieldValidationError(BadRequest):
    pass


class AssignmentValidationError(BadRequest):
    pass


class AssignmentAlreadyInUse(BadRequest):
    pass
