from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class PropertySheetsGet(Service):
    """
    Return a list of all registered sheets or the schema for a single sheet.

    A list of all sheets can be obtained with no additional path segments:

    GET http://localhost:8080/fd/@propertysheets HTTP/1.1

    The schema for a single sheet can be obtained by using the name of the
    sheet in the request path:

    GET http://localhost:8080/fd/@propertysheets/<sheet-name> HTTP/1.1
    """

    def __init__(self, context, request):
        super(PropertySheetsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        if not self.params:
            return self.reply_list_all_sheets()

        elif len(self.params) == 1:
            return self.reply_for_sheet()

        raise BadRequest(u"Must supply either zero or one parameters.")

    def reply_list_all_sheets(self):
        storage = PropertySheetSchemaStorage()

        base_url = "{}/@propertysheets".format(self.context.absolute_url())
        result = {"@id": base_url, "items": []}
        for schema_definition in storage.list():
            sheet_definition = {
                "@id": "{}/{}".format(base_url, schema_definition.name)
            }
            result["items"].append(sheet_definition)
        return result

    def reply_for_sheet(self):
        sheet_name = self.params.pop()
        storage = PropertySheetSchemaStorage()

        schema_definition = storage.get(sheet_name)
        if schema_definition is None:
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": u"Sheet '{}' not found.".format(sheet_name),
            }

        json_schema = schema_definition.get_json_schema()
        self.content_type = "application/json+schema"
        return json_schema
