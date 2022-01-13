from opengever.propertysheets.api.base import PropertySheetLocator


class PropertySheetsGet(PropertySheetLocator):
    """
    Return a list of all registered sheets or the schema for a single sheet.

    A list of all sheets can be obtained with no additional path segments:

    GET http://localhost:8080/fd/@propertysheets HTTP/1.1

    The schema for a single sheet can be obtained by using the name of the
    sheet in the request path:

    GET http://localhost:8080/fd/@propertysheets/<sheet-name> HTTP/1.1
    """

    sheet_id_required = False

    def reply(self):
        sheet_definition = self.locate_sheet()

        if sheet_definition is not None:
            # Get sheet by id
            return self.serialize(sheet_definition)
        else:
            # List all sheets
            return self.list()

    def list(self):
        base_url = "{}/@propertysheets".format(self.context.absolute_url())
        result = {"@id": base_url, "items": []}
        for schema_definition in self.storage.list():
            sheet_definition = {
                "@id": "{}/{}".format(base_url, schema_definition.name),
                "@type": "virtual.propertysheet",
                "id": schema_definition.name,
            }
            result["items"].append(sheet_definition)
        return result
