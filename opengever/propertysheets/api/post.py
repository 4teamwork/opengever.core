from opengever.propertysheets.api.utils import get_property_sheet_schema
from opengever.propertysheets.definition import PropertySheetSchemas
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.schemaeditor import fields
from plone.schemaeditor.utils import IEditableSchema
from plone.supermodel import model
from zExceptions import BadRequest
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


# some hardcoded factories for the POC
factories = {
    'text': fields.TextFactory,
    'int': fields.IntFactory,
    'bool': fields.BoolFactory,
}


@implementer(IPublishTraverse)
class PropertySheetsPost(Service):
    """
    Stores new property sheets or replaces existing ones.

    Sample request:

    POST http://localhost:8080/fd/@propertysheets/qux

    {"fields": {"foo": {"type": "text", "required": true}}}

    See plone.schemaeditor.browser.schema.add_field.FieldAddForm
    """

    def __init__(self, context, request):
        super(PropertySheetsPost, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        if len(self.params) != 1:
            raise BadRequest("Missing parameter sheet_name")

        data = json_body(self.request)

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        sheet_name = self.params.pop()

        class SchemaClass(model.Schema):
            pass

        schema = IEditableSchema(SchemaClass)

        for field_name, data in data['fields'].items():
            factory = factories[data['type']]

            title = data.get('title', field_name)
            required = data.get('required', False)

            properties = {
                "title": title,
                "__name__": field_name,
                "description": u"",
                "required": required,
            }

            field = factory(**properties)
            schema.addField(field)

        PropertySheetSchemas.save(sheet_name, SchemaClass)

        self.request.response.setStatus(201)
        return get_property_sheet_schema(
            self.context, self.request, PropertySheetSchemas.get(sheet_name)
        )
