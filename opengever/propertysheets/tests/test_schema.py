from jsonschema import Draft4Validator
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exportimport import dottedname
from opengever.propertysheets.testing import dummy_default_factory_fr
from opengever.testing import FunctionalTestCase
from plone import api


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
        member = api.user.get_current()
        member.setProperties({'location': 'Switzerland'})

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
            "choice", u"choice_with_default_factory", u"Choice with default factory",
            u"", True,
            values=[u'de', u'fr', u'en'],
            default_factory=dottedname(dummy_default_factory_fr),
        )
        definition.add_field(
            "choice", u"choice_with_default_expression", u"Choice with default expression",
            u"", True,
            values=[u'de', u'fr', u'en'],
            default_expression='portal/language',
        )
        definition.add_field(
            "choice", u"choice_with_default_from_member", u"Choice with default from Member",
            u"", True,
            values=[u'CH', u'DE', u'US'],
            default_from_member={
                'property': 'location',
                'mapping': {
                    'Switzerland': 'CH',
                    'Germany': 'DE',
                    'United States': 'US',
                }
            },
        )
        definition.add_field(
            "choice", u"choice_with_unicode", u"Choice with Unicode",
            u"", True,
            values=[u'Deutsch', u'Fran\xe7ais'],
            default=u'Fran\xe7ais',
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
                       u'choice_with_default_factory',
                       u'choice_with_default_expression',
                       u'choice_with_default_from_member',
                       u'choice_with_unicode',
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
                u'choice_with_default_expression': {
                    u'choices': [
                        [u'de', u'de'],
                        [u'fr', u'fr'],
                        [u'en', u'en'],
                    ],
                    u'default': u'en',
                    u'default_expression': u'portal/language',
                    u'default_factory': None,
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
                    u'title': u'Choice with default expression',
                    u'type': u'string',
                },
                u'choice_with_default_factory': {
                    u'choices': [
                        [u'de', u'de'],
                        [u'fr', u'fr'],
                        [u'en', u'en'],
                    ],
                    u'default': u'fr',
                    u'default_factory': u'opengever.propertysheets.testing.dummy_default_factory_fr',
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
                    u'title': u'Choice with default factory',
                    u'type': u'string',
                },
                u'choice_with_default_from_member': {
                    u'choices': [
                        [u'CH', u'CH'],
                        [u'DE', u'DE'],
                        [u'US', u'US'],
                    ],
                    u'default': u'CH',
                    u'default_from_member': {
                        u'mapping': {
                            u'Germany': u'DE',
                            u'Switzerland': u'CH',
                            u'United States': u'US',
                        },
                        u'property': u'location',
                    },
                    u'default_factory': None,
                    u'description': u'',
                    u'enum': [
                        u'CH',
                        u'DE',
                        u'US',
                    ],
                    u'enumNames': [
                        u'CH',
                        u'DE',
                        u'US',
                    ],
                    u'factory': u'Choice',
                    u'title': u'Choice with default from Member',
                    u'type': u'string',
                },
                u'choice_with_unicode': {
                    u'choices': [
                        [u'Deutsch', u'Deutsch'],
                        [u'Fran\\xe7ais', u'Fran\xe7ais'],
                    ],
                    u'default': u'Fran\\xe7ais',
                    u'description': u'',
                    u'enum': [
                        u'Deutsch',
                        u'Fran\\xe7ais',
                    ],
                    u'enumNames': [
                        u'Deutsch',
                        u'Fran\xe7ais',
                    ],
                    u'factory': u'Choice',
                    u'title': u'Choice with Unicode',
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
                u'choice_with_default_factory',
                u'choice_with_default_expression',
                u'choice_with_default_from_member',
                u'choice_with_unicode',
                u'num',
                u'blabla',
                u'bla',
            ],
            'title': 'schema',
            'type': 'object',
        }     

        self.assertEqual(expected, json_schema)
