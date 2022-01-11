from ftw.testbrowser import browsing
from jsonschema import Draft4Validator
from jsonschema import FormatChecker
from jsonschema import validate
from opengever.testing import IntegrationTestCase


class TestPropertysheetMetaschemaEndpoint(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_is_valid_jsonschema(self, browser):
        self.login(self.propertysheets_manager, browser)

        browser.open(
            view="@propertysheet-metaschema",
            headers=self.api_headers,
        )
        Draft4Validator.check_schema(browser.json)

    @browsing
    def test_produces_metaschema(self, browser):
        self.login(self.propertysheets_manager, browser)

        browser.open(
            view="@propertysheet-metaschema",
            headers=self.api_headers,
        )

        fields_schema = {
            u"additionalProperties": False,
            u"description": u"Fields",
            u"items": {
                u"properties": {
                    u"description": {
                        u"description": u"",
                        u"title": u"",
                        u"type": u"string",
                    },
                    u"field_type": {
                        u"choices": [
                            [u"int", None],
                            [u"multiple_choice", None],
                            [u"choice", None],
                            [u"bool", None],
                            [u"text", None],
                            [u"date", None],
                            [u"textline", None],
                        ],
                        u"description": u"",
                        u"enum": [
                            u"int",
                            u"multiple_choice",
                            u"choice",
                            u"bool",
                            u"text",
                            u"date",
                            u"textline",
                        ],
                        u"enumNames": [None, None, None, None, None, None, None],
                        u"title": u"",
                        u"type": u"string",
                    },
                    u"name": {
                        u"description": u"",
                        u"title": u"",
                        u"type": u"string",
                    },
                    u"required": {
                        u"description": u"",
                        u"title": u"",
                        u"type": u"boolean",
                    },
                    u"title": {
                        u"description": u"",
                        u"title": u"",
                        u"type": u"string",
                    },
                    u"values": {
                        u"description": u"",
                        u"items": {
                            u"description": u"",
                            u"factory": u"Text line (String)",
                            u"title": u"",
                            u"type": u"string",
                        },
                        u"title": u"",
                        u"type": u"array",
                        u"uniqueItems": False,
                    },
                },
                u"required": [u"name", u"field_type"],
                u"type": u"object",
            },
            u"title": u"Fields",
            u"type": u"array",
            u"uniqueItems": False,
        }

        assignments_schema = {
            u"additionalProperties": False,
            u"description": u"What type of content this property sheet will "
                            u"be available for",
            u"items": {
                u"choices": [
                    [u"IDocument.default", u"Document"],
                    [
                        u"IDocumentMetadata.document_type.contract",
                        u"Document (Type: Contract)",
                    ],
                    [
                        u"IDocumentMetadata.document_type.directive",
                        u"Document (Type: Directive)",
                    ],
                    [
                        u"IDocumentMetadata.document_type.question",
                        u"Document (Type: Inquiry)",
                    ],
                    [
                        u"IDocumentMetadata.document_type.offer",
                        u"Document (Type: Offer)",
                    ],
                    [
                        u"IDocumentMetadata.document_type.protocol",
                        u"Document (Type: Protocol)",
                    ],
                    [
                        u"IDocumentMetadata.document_type.regulations",
                        u"Document (Type: Regulations)",
                    ],
                    [
                        u"IDocumentMetadata.document_type.report",
                        u"Document (Type: Report)",
                    ],
                    [
                        u"IDocumentMetadata.document_type.request",
                        u"Document (Type: Request)",
                    ],
                    [u"IDossier.default", u"Dossier"],
                    [
                        u"IDossier.dossier_type.businesscase",
                        u"Dossier (Type: Business case)",
                    ],
                ],
                u"enum": [
                    u"IDocument.default",
                    u"IDocumentMetadata.document_type.contract",
                    u"IDocumentMetadata.document_type.directive",
                    u"IDocumentMetadata.document_type.question",
                    u"IDocumentMetadata.document_type.offer",
                    u"IDocumentMetadata.document_type.protocol",
                    u"IDocumentMetadata.document_type.regulations",
                    u"IDocumentMetadata.document_type.report",
                    u"IDocumentMetadata.document_type.request",
                    u"IDossier.default",
                    u"IDossier.dossier_type.businesscase",
                ],
                u"enumNames": [
                    u"Document",
                    u"Document (Type: Contract)",
                    u"Document (Type: Directive)",
                    u"Document (Type: Inquiry)",
                    u"Document (Type: Offer)",
                    u"Document (Type: Protocol)",
                    u"Document (Type: Regulations)",
                    u"Document (Type: Report)",
                    u"Document (Type: Request)",
                    u"Dossier",
                    u"Dossier (Type: Business case)",
                ],
                u"type": u"string",
            },
            u"title": u"Assignments",
            u"type": u"array",
            u"uniqueItems": True,
        }

        full_schema = {
            u"$schema": u"http://json-schema.org/draft-04/schema#",
            u"additionalProperties": False,
            u"field_order": [u'fields', u'assignments'],
            u"properties": {
                u"assignments": assignments_schema,
                u"fields": fields_schema,
            },
            u"required": [u"fields"],
            u"title": u"Propertysheet Meta Schema",
            u"type": u"object",
        }

        self.assertEqual(full_schema, browser.json)

    @browsing
    def test_complex_definition_validates_against_jsonschema(self, browser):
        self.login(self.propertysheets_manager, browser)

        browser.open(
            view="@propertysheet-metaschema",
            headers=self.api_headers,
        )
        schema = browser.json

        colors = [u"Rot", u"Gr\xfcn", u"Blau"]
        labels = [u"Alpha", u"Beta", u"Gamma", u"Delta"]

        definition = {
            "fields": [
                {
                    "name": "color",
                    "field_type": "choice",
                    "title": "Color",
                    "description": "Color",
                    "required": True,
                    "values": colors,
                    "default": u"Gr\xfcn",
                },
                {
                    "name": "digital",
                    "field_type": "bool",
                    "title": "Digital",
                    "description": "Digital",
                    "required": True,
                },
                {
                    "name": "labels",
                    "field_type": "multiple_choice",
                    "title": "Labels",
                    "description": "Labels",
                    "required": False,
                    "values": labels,
                    "default": [u"Alpha", u"Gamma"],
                },
                {
                    "name": "age",
                    "field_type": "int",
                    "title": "Age",
                    "description": "Age",
                    "required": True,
                    "default": 42,
                },
                {
                    "name": "note",
                    "field_type": "text",
                    "title": "Note",
                    "description": "Note",
                    "required": False,
                },
                {
                    "name": "short_note",
                    "field_type": "textline",
                    "title": "Short Note",
                    "description": "Short Note",
                    "required": False,
                },
                {
                    "name": "birthday",
                    "field_type": "date",
                    "title": "Birthday",
                    "required": False,
                    "default": "2022-07-30",
                },
            ],
            "assignments": ["IDossier.default"],
        }

        def validate_schema(items, schema):
            # May raise jsonschema.ValidationError
            return validate(items, schema, format_checker=FormatChecker())

        validate_schema(definition, schema)

    @browsing
    def test_assignment_vocabularies_are_translated(self, browser):
        self.login(self.propertysheets_manager, browser)

        headers = self.api_headers.copy()
        headers.update({'Accept-Language': 'de-ch'})

        browser.open(
            view="@propertysheet-metaschema",
            headers=headers,
        )

        properties = browser.json['properties']
        self.assertEqual(
            [
                u'Dokument',
                u'Dokument (Typ: Anfrage)',
                u'Dokument (Typ: Antrag)',
                u'Dokument (Typ: Bericht)',
                u'Dokument (Typ: Offerte)',
                u'Dokument (Typ: Protokoll)',
                u'Dokument (Typ: Reglement)',
                u'Dokument (Typ: Vertrag)',
                u'Dokument (Typ: Weisung)',
                u'Dossier',
                u'Dossier (Typ: Gesch\xe4ftsfall)',
            ],
            properties['assignments']['items']['enumNames'])
