from opengever.api.add import get_schema_validation_errors
from opengever.propertysheets.definition import isidentifier
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exceptions import InvalidSchemaAssignment
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.supermodel import model
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import provider
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


@provider(IContextSourceBinder)
def make_field_types_vocabulary(context):
    return SimpleVocabulary.fromValues(
        PropertySheetSchemaDefinition.FACTORIES.keys()
    )


class IFieldDefinition(model.Schema):

    name = schema.TextLine(required=True)
    field_type = schema.Choice(
        required=True, source=make_field_types_vocabulary
    )
    title = schema.TextLine(required=False)
    description = schema.TextLine(required=False)
    required = schema.Bool(required=False)
    values = schema.List(
        default=None,
        value_type=schema.TextLine(),
        required=False,
    )


@implementer(IPublishTraverse)
class PropertySheetsPost(Service):
    """
    Add new property sheets or replace existing ones.

    POST http://localhost:8080/fd/@propertysheets/question HTTP/1.1
    {
        "fields": [{"name": "foo", field_type": "text", "required": true}],
        "assignments": ["IDocumentMetadata.document_type.question"]
    }
    """
    def __init__(self, context, request):
        super(PropertySheetsPost, self).__init__(context, request)
        self.params = []
        self.storage = PropertySheetSchemaStorage()

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        if len(self.params) != 1:
            raise BadRequest(u"Missing parameter sheet_name.")
        sheet_name = self.params.pop()
        if not isidentifier(sheet_name):
            raise BadRequest(u"The name '{}' is invalid.".format(sheet_name))

        data = json_body(self.request)
        fields = data.get("fields")
        if not fields or not isinstance(fields, list):
            raise BadRequest(u"Missing or invalid field definitions.")

        errors = []
        for field_data in fields:
            field_errors = get_schema_validation_errors(
                self.context, field_data, IFieldDefinition
            )
            if field_errors:
                errors.extend(field_errors)

            # Require Manager role for any kind of dynamic defaults
            dynamic_defaults = PropertySheetSchemaDefinition.DYNAMIC_DEFAULT_PROPERTIES
            if any(p in field_data for p in dynamic_defaults):
                if not api.user.has_permission('cmf.ManagePortal'):
                    raise Unauthorized(
                        'Setting any dynamic defaults requires Manager role')

        if errors:
            raise BadRequest(errors)

        seen = set()
        duplicates = []
        for name in [each["name"] for each in fields]:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        if duplicates:
            raise BadRequest(
                u"Duplicate fields '{}'.".format("', '".join(duplicates))
            )

        assignments = data.get("assignments")
        if assignments is not None:
            assignments = tuple(assignments)

        try:
            schema_definition = self.create_property_sheet(
                sheet_name, assignments, fields
            )
        except InvalidSchemaAssignment as exc:
            raise BadRequest(exc.message)

        json_schema = schema_definition.get_json_schema()
        self.request.response.setStatus(201)
        self.content_type = "application/json+schema"
        return json_schema

    def create_property_sheet(self, sheet_name, assignments, fields):
        schema_definition = PropertySheetSchemaDefinition.create(
            sheet_name, assignments=assignments
        )
        for field_data in fields:
            name = field_data["name"]
            field_type = field_data["field_type"]
            title = field_data.get("title", name)
            description = field_data.get("description", u"")
            required = field_data.get("required", False)
            values = field_data.get("values")
            default = field_data.get("default")
            default_factory = field_data.get("default_factory")
            default_expression = field_data.get("default_expression")
            default_from_member = field_data.get("default_from_member")
            schema_definition.add_field(
                field_type, name, title, description, required, values,
                default, default_factory, default_expression,
                default_from_member
            )

        self.storage.save(schema_definition)
        return self.storage.get(sheet_name)
