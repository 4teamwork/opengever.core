from opengever.propertysheets import _
from zExceptions import BadRequest
from zope.schema.interfaces import ValidationError


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


class DuplicateField(ValidationError):
    __doc__ = _("""Duplicate field with this name""")
