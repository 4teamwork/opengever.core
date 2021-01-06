from jsonschema import Draft4Validator
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.testing import FunctionalTestCase


class TestPropertySheetJSONSchema(FunctionalTestCase):

    maxDiff = None

    def test_validate_simple_property_sheet_schema_definition(self):
        definition = PropertySheetSchemaDefinition.create(
            "schema", assignments=[u"foo.bar"]
        )
        definition.add_field("bool", u"yesorno", u"y/n", u"", False)
        choices = [u"bl\xe4h", u"bl\xfcb"]
        definition.add_field(
            "choice", u"choose", u"Usw\xe4hle", u"", True, values=choices
        )

        json_schema = definition.get_json_schema()
        Draft4Validator.check_schema(json_schema)

        self.assertEqual(
            {
                u"assignments": [u"foo.bar"],
                u"fieldsets": [
                    {
                        u"behavior": u"plone",
                        u"fields": [u"yesorno", u"choose"],
                        u"id": u"default",
                        u"title": u"Default",
                    }
                ],
                u"properties": {
                    u"choose": {
                        u"choices": [
                            [u"blaeh", u"bl\xe4h"],
                            [u"blueb", u"bl\xfcb"]
                        ],
                        u"description": u"",
                        u"enum": [u"blaeh", u"blueb"],
                        u"enumNames": [u"bl\xe4h", u"bl\xfcb"],
                        u"factory": u"Choice",
                        u"title": u"Usw\xe4hle",
                        u"type": u"string",
                    },
                    u"yesorno": {
                        u"description": u"",
                        u"factory": u"Yes/No",
                        u"title": u"y/n",
                        u"type": u"boolean",
                    },
                },
                u"required": [u"choose"],
                u"title": u"schema",
                u"type": u"object",
            },
            json_schema
        )

    def test_validate_complex_sheet_schema_with_all_supported_fields(self):
        definition = PropertySheetSchemaDefinition.create(
            "schema", assignments=[u"foo.bar"]
        )
        definition.add_field("bool", u"yesorno", u"y/n", u"", False)
        choices = [u"bl\xe4h", u"blub"]
        definition.add_field(
            "choice", u"chooseone", u"choose", u"", False, values=choices
        )
        definition.add_field(
            "int", u"num", u"A number", u"Put a number.", True
        )
        definition.add_field(
            "text", u"blabla", u"Text", u"Say something long.", True
        )
        definition.add_field(
            "textline", u"bla", u"Textline", u"Say something short.", True
        )

        json_schema = definition.get_json_schema()
        Draft4Validator.check_schema(json_schema)
