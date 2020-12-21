from opengever.propertysheets.definition import PropertySheetSchemas
from plone.restapi.services import Service
from opengever.propertysheets.api.utils import get_property_sheet_schema


class PropertySheetsGet(Service):
    """GET http://localhost:8080/fd/@propertysheets"""

    def reply(self):
        response = []
        for schema_class in PropertySheetSchemas.list():
            response.append(get_property_sheet_schema(
                self.context, self.request, schema_class)
            )

        return response
