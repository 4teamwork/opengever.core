from ftw.testbrowser import browsing
from opengever.propertysheets.exportimport import dottedname
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.propertysheets.testing import dummy_default_factory_fr
from opengever.testing import IntegrationTestCase
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter
import json


class TestPropertySheetSchemaDefinitionSerializer(IntegrationTestCase):

    maxDiff = None

    def serialize(self, definition):
        serializer = getMultiAdapter(
            (definition, self.request), ISerializeToJson)
        return serializer()

    @browsing
    def test_serializes_all_field_types(self, browser):
        self.login(self.propertysheets_manager, browser)

        data = {
            "fields": [
                {
                    "name": "active",
                    "field_type": u"bool",
                    "title": u"Active",
                    "default": True,
                },
                {
                    "name": "language",
                    "field_type": u"choice",
                    "title": u"Language",
                    "values": [u"de", u"fr", u"en"],
                    "default": u"fr",
                },
                {
                    "name": "colors",
                    "field_type": u"multiple_choice",
                    "title": u"Colors",
                    "description": "A selection of colors",
                    "values": [u"Rot", u"Gr\xfcn", "Blau"],
                    "default": [u"Gr\xfcn"],
                },
                {
                    "name": "number",
                    "field_type": u"int",
                    "title": u"Number",
                    "default": 42,
                },
                {
                    "name": "text",
                    "field_type": u"text",
                    "title": u"Text",
                    "required": True,
                    "default": u"some text",
                },
                {
                    "name": "lineoftext",
                    "field_type": u"textline",
                    "title": u"Line of text",
                    "default": u"some text line",
                },
                {
                    "name": "birthday",
                    "field_type": u"date",
                    "title": u"Birthday",
                },
            ],
            "assignments": ["IDocumentMetadata.document_type.question"],
        }
        browser.open(
            view="@propertysheets/meinschema",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        definition = storage.get("meinschema")

        serialized = self.serialize(definition)
        self.assertEqual('meinschema', serialized['id'])
        self.assertEqual(data['assignments'], serialized['assignments'])
        self.assertEqual(len(data['fields']), len(serialized['fields']))

        for input_field, serialized_field in zip(data['fields'], serialized['fields']):
            # Fill in any implied defaults in the input fields so they
            # actually match the equivalent serialized field
            if 'description' not in input_field:
                input_field['description'] = ''
            if 'required' not in input_field:
                input_field['required'] = False

            self.assertEqual(input_field, serialized_field)

    @browsing
    def test_serializes_default_factory(self, browser):
        self.login(self.manager, browser)

        data = {
            "fields": [
                {
                    "name": "language",
                    "field_type": u"choice",
                    "title": u"Language",
                    "values": [u"de", u"fr", u"en"],
                    "default_factory": dottedname(dummy_default_factory_fr),
                },
            ],
            "assignments": ["IDocument.default"],
        }
        browser.open(
            view="@propertysheets/meinschema",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        definition = storage.get("meinschema")

        serialized = self.serialize(definition)
        self.assertEqual(
            {
                u'id': u'meinschema',
                u'assignments': [u'IDocument.default'],
                u'fields': [
                    {
                        u'name': u'language',
                        u'field_type': u'choice',
                        u'title': u'Language',
                        u'description': u'',
                        u'required': False,
                        u'values': [u'de', u'fr', u'en'],
                        u'default_factory': dottedname(dummy_default_factory_fr),
                    },
                ],
            },
            serialized,
        )

    @browsing
    def test_serializes_default_expression(self, browser):
        self.login(self.manager, browser)

        data = {
            "fields": [
                {
                    "name": "language",
                    "field_type": u"choice",
                    "title": u"Language",
                    "values": [u"de", u"fr", u"en"],
                    "default_expression": "python: 'fr'",
                },
            ],
            "assignments": ["IDocument.default"],
        }
        browser.open(
            view="@propertysheets/meinschema",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        definition = storage.get("meinschema")

        serialized = self.serialize(definition)
        self.assertEqual(
            {
                u'id': u'meinschema',
                u'assignments': [u'IDocument.default'],
                u'fields': [
                    {
                        u'name': u'language',
                        u'field_type': u'choice',
                        u'title': u'Language',
                        u'description': u'',
                        u'required': False,
                        u'values': [u'de', u'fr', u'en'],
                        u'default_expression': u"python: 'fr'",
                    },
                ],
            },
            serialized,
        )

    @browsing
    def test_serializes_default_from_member(self, browser):
        self.login(self.manager, browser)

        default_from_member = {
            'property': 'location',
            'mapping': {
                'Switzerland': 'CH',
                'Germany': 'DE',
                'United States': 'US',
            }
        }

        data = {
            "fields": [
                {
                    "name": "language",
                    "field_type": u"choice",
                    "title": u"Language",
                    "values": [u"de", u"fr", u"en"],
                    "default_from_member": default_from_member,
                },
            ],
            "assignments": ["IDocument.default"],
        }
        browser.open(
            view="@propertysheets/meinschema",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        definition = storage.get("meinschema")

        serialized = self.serialize(definition)
        self.assertEqual(
            {
                u'id': u'meinschema',
                u'assignments': [u'IDocument.default'],
                u'fields': [
                    {
                        u'name': u'language',
                        u'field_type': u'choice',
                        u'title': u'Language',
                        u'description': u'',
                        u'required': False,
                        u'values': [u'de', u'fr', u'en'],
                        u'default_from_member': default_from_member,
                    },
                ],
            },
            serialized,
        )
