from jsonschema import Draft4Validator
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.testing import FunctionalTestCase


class TestPropertySheetJSONSchema(FunctionalTestCase):

    maxDiff = None

    def test_validate_simple_property_sheet_schema_definition(self):
        definition = PropertySheetSchemaDefinition.create(
            "schema", assignments=[u"IDocumentMetadata.document_type.question"]
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
                u"assignments": [u"IDocumentMetadata.document_type.question"],
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
                            [u"bl\xe4h".encode("unicode_escape"), u"bl\xe4h"],
                            [u"bl\xfcb".encode("unicode_escape"), u"bl\xfcb"]
                        ],
                        u"description": u"",
                        u"enum": [
                            u"bl\xe4h".encode("unicode_escape"),
                            u"bl\xfcb".encode("unicode_escape")
                        ],
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
            "schema", assignments=[u"IDocumentMetadata.document_type.question"]
        )
        definition.add_field("bool", u"yesorno", u"y/n", u"", False)
        choices = [u"bl\xe4h", u"blub"]
        definition.add_field(
            "choice", u"chooseone", u"choose", u"", False, values=choices
        )
        definition.add_field(
            "choice", u"choice_with_default", u"Choice with default",
            u"", True,
            values=[u'de', u'fr', u'en'],
            default=u'fr',
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

        expected = {
            'assignments': [
                u'IDocumentMetadata.document_type.question',
            ],
            'fieldsets': [
                {
                    'behavior': 'plone',
                    'fields': [
                       u'yesorno',
                       u'chooseone',
                       u'choice_with_default',
                       u'num',
                       u'blabla',
                       u'bla',
                    ],
                    'id': 'default',
                    'title': 'Default',
                }
            ],
            'properties': {
                u'bla': {
                    u'description': u'Say something short.',
                    u'factory': u'Text line (String)',
                    u'title': u'Textline',
                    u'type': u'string',
                },
                u'blabla': {
                    u'description': u'Say something long.',
                    u'factory': u'Text',
                    u'title': u'Text',
                    u'type': u'string',
                    u'widget': u'textarea',
                },
                u'choice_with_default': {
                    u'choices': [
                        [u'de', u'de'],
                        [u'fr', u'fr'],
                        [u'en', u'en'],
                    ],
                    u'default': u'fr',
                    u'description': u'',
                    u'enum': [
                        u'de',
                        u'fr',
                        u'en',
                    ],
                    u'enumNames': [
                        u'de',
                        u'fr',
                        u'en',
                    ],
                    u'factory': u'Choice',
                    u'title': u'Choice with default',
                    u'type': u'string',
                },
                u'chooseone': {
                    u'choices': [
                        [u'bl\\xe4h', u'bl\xe4h'],
                        [u'blub', u'blub'],
                    ],
                    u'description': u'',
                    u'enum': [
                        u'bl\\xe4h',
                        u'blub',
                    ],
                    u'enumNames': [
                        u'bl\xe4h',
                        u'blub',
                    ],
                    u'factory': u'Choice',
                    u'title': u'choose',
                    u'type': u'string',
                },
                u'num': {
                    u'description': u'Put a number.',
                    u'factory': u'Integer',
                    u'title': u'A number',
                    u'type': u'integer',
                },
                u'yesorno': {
                    u'description': u'',
                    u'factory': u'Yes/No',
                    u'title': u'y/n',
                    u'type': u'boolean',
                },
            },
            'required': [
                u'choice_with_default',
                u'num',
                u'blabla',
                u'bla',
            ],
            'title': 'schema',
            'type': 'object',
        }     

        self.assertEqual(expected, json_schema)
