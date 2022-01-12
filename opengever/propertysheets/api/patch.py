from opengever.api.validation import get_validation_errors
from opengever.api.validation import scrub_json_payload
from opengever.propertysheets.api.error_rendering import render_error
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exceptions import InvalidSchemaAssignment
from opengever.propertysheets.metaschema import IFieldDefinition
from opengever.propertysheets.metaschema import IPropertySheetDefinition
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class PropertySheetsPatch(Service):
    """
    Modify an existing property sheet.

    PATCH http://localhost:8080/fd/@propertysheets/question HTTP/1.1
    {
        "fields": [{"name": "foo", field_type": "text", "required": true}],
    }
    """
    def __init__(self, context, request):
        super(PropertySheetsPatch, self).__init__(context, request)
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
        id_field = IPropertySheetDefinition['id']
        try:
            id_field.bind(sheet_name).validate(sheet_name)
        except Exception:
            raise BadRequest(u"The name '{}' is invalid.".format(sheet_name))

        data = json_body(self.request)
        fields = data.get("fields")

        if fields:
            errors = self.validate_fields(fields)
            if errors:
                msg = render_error(errors)
                raise BadRequest(msg)

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

        # Get existing sheet definition
        storage = PropertySheetSchemaStorage()
        schema_definition = storage.get(sheet_name)

        serializer = getMultiAdapter((schema_definition, self.request), ISerializeToJson)
        serialized_existing_definition = serializer()

        # Update it
        new_definition = serialized_existing_definition.copy()
        if fields is not None:
            new_definition.update({'fields': fields})

        if assignments is not None:
            new_definition.update({'assignments': assignments})

        # Delete old one
        storage.remove(sheet_name)

        try:
            schema_definition = self.create_property_sheet(
                sheet_name, new_definition['assignments'], new_definition['fields']
            )
        except InvalidSchemaAssignment as exc:
            raise BadRequest(exc.message)

        self.request.response.setStatus(200)
        serializer = getMultiAdapter((schema_definition, self.request), ISerializeToJson)
        return serializer()

    def validate_fields(self, fields):
        errors = []

        for field_data in fields:
            # Cast JSON strings to their appropriate Python types (unicode or
            # bytestring), depending on the schema field (ASCII or Text[Line])
            scrub_json_payload(field_data, IFieldDefinition)

            # Allowing unknown fields is necessary in order to allow managers
            # to set dynamic defaults like `default_factory`, which currently
            # aren't exposed in the meta schema.
            field_errors = get_validation_errors(
                field_data, IFieldDefinition, allow_unknown_fields=True)

            if field_errors:
                errors.extend(field_errors)

            # Require Manager role for any kind of dynamic defaults
            dynamic_defaults = PropertySheetSchemaDefinition.DYNAMIC_DEFAULT_PROPERTIES
            if any(p in field_data for p in dynamic_defaults):
                if not api.user.has_permission('cmf.ManagePortal'):
                    raise Unauthorized(
                        'Setting any dynamic defaults requires Manager role')
        return errors

    def create_property_sheet(self, sheet_name, assignments, fields):
        schema_definition = PropertySheetSchemaDefinition.create(
            sheet_name, assignments=assignments
        )
        for field_data in fields:
            name = field_data["name"]
            field_type = field_data["field_type"]
            title = field_data.get("title", name.decode('ascii'))
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
