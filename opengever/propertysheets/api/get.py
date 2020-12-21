from opengever.propertysheets.definition import PropertySheetSchemas
from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.services import Service
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import iter_fields


class PropertySheetsGet(Service):

    def reply(self):
        response = []
        for schema_class in PropertySheetSchemas.list(self.context):
            fieldsets = get_fieldsets(self.context, self.request, schema_class)
            properties = get_jsonschema_properties(self.context, self.request, fieldsets)

            required = []
            for field in iter_fields(fieldsets):
                name = field.field.getName()
                # Determine required fields
                if field.field.required:
                    required.append(name)

            schema_info = {
                "id": schema_class.getName(),
                "properties": IJsonCompatible(properties),
                "required": required,
                "fieldsets": get_fieldset_infos(fieldsets),
            }

            response.append(schema_info)

        return response
