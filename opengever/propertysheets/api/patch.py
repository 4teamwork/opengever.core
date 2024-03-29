from opengever.propertysheets.api.base import PropertySheetWriter
from opengever.propertysheets.definition import PropertySheetSchemaDefinition as PSDefinition
from opengever.propertysheets.exceptions import InvalidSchemaAssignment
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from zExceptions import BadRequest
from zope.interface import alsoProvides


class PropertySheetsPatch(PropertySheetWriter):
    """
    Modify an existing property sheet.

    PATCH semantics only apply to the topmost level (assignments and fields) -
    if either of those keys is omitted, it will be preserved as-is.

    Omitting a field from the list of fields however will delete it. The field
    list as a whole therefore needs to be modified by the caller, and always
    be sent in its entirety.

    Syntax:

    PATCH /@propertysheets/question HTTP/1.1
    {
        "fields": [{"name": "foo", field_type": "text", "required": true}],
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

        sheet_definition = self.locate_sheet()
        sheet_id = sheet_definition.name
        data = json_body(self.request)

        if 'id' in data and data['id'] != sheet_id:
            raise BadRequest("The 'id' of an existing sheet must not be changed.")

        assignments = self.get_assignments(data, sheet_definition)

        existing_dynamic_defaults = self.get_existing_dynamic_defaults(
            sheet_definition)

        fields = self.get_fields(data, existing_dynamic_defaults)

        # Get existing sheet definition
        serialized_existing_definition = self.serialize(sheet_definition)

        # Update it
        new_definition_data = serialized_existing_definition.copy()
        if fields is not None:
            new_definition_data.update({'fields': fields})

        if assignments is not None:
            new_definition_data.update({'assignments': assignments})

        # Delete old one
        self.storage.remove(sheet_id)

        # Recreate the updated one
        try:
            new_definition = self.create_property_sheet(
                sheet_id,
                new_definition_data['assignments'],
                new_definition_data['fields'],
            )
        except InvalidSchemaAssignment as exc:
            raise BadRequest(exc.message)

        self.request.response.setStatus(200)
        return self.serialize(new_definition)

    def get_existing_dynamic_defaults(self, sheet_definition):
        sheet = self.serialize(sheet_definition)
        dynamic_default_types = PSDefinition.DYNAMIC_DEFAULT_PROPERTIES
        existing_dynamic_defaults = []

        for field in sheet.get('fields', []):
            for dynamic_default_type in dynamic_default_types:
                if field.get(dynamic_default_type) is not None:
                    existing = (
                        field['name'],
                        dynamic_default_type,
                        field.get(dynamic_default_type),
                    )
                    existing_dynamic_defaults.append(existing)

        return existing_dynamic_defaults
