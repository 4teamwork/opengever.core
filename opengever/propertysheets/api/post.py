from opengever.propertysheets.api.base import PropertySheetWriter
from opengever.propertysheets.exceptions import FieldValidationError
from opengever.propertysheets.exceptions import InvalidSchemaAssignment
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from zExceptions import BadRequest
from zope.interface import alsoProvides


class PropertySheetsPost(PropertySheetWriter):
    """
    Add new property sheets or replace existing ones.

    POST http://localhost:8080/fd/@propertysheets/question HTTP/1.1
    {
        "fields": [{"name": "foo", field_type": "text", "required": true}],
        "assignments": ["IDocumentMetadata.document_type.question"]
    }
    """

    sheet_id_required = True

    def reply(self):
        try:
            return self._reply()
        except Exception as exc:
            return self.serialize_exception(exc)

    def _reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        sheet_id = self.get_sheet_id()
        data = json_body(self.request)

        assignments = self.get_assignments(data)

        fields = self.get_fields(data)
        if not fields:
            raise BadRequest(u"Missing or invalid field definitions.")

        try:
            schema_definition = self.create_property_sheet(
                sheet_id, assignments, fields
            )
        except InvalidSchemaAssignment as exc:
            raise BadRequest(exc.message)

        self.request.response.setStatus(201)
        return self.serialize(schema_definition)
