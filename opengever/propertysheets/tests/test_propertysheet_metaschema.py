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

        id_schema = {
            u"additionalProperties": False,
            u"description": u"ID of this property sheet",
            u"pattern": u"^[a-z_0-9]*$",
            u"title": u"ID",
            u"type": u"string",
        }

        fields_schema = {
            u"additionalProperties": False,
            u"description": u"Fields",
            u"items": {
                u"properties": {
                    u"default": {
                        u"description": u"Default value for this field",
                        u"title": u"Default",
                        u"type": [u"integer", u"array", u"boolean", u"string"],
                    },
                    u"description": {
                        u"description": u"Description",
                        u"maxLength": 128,
                        u"title": u"Description",
                        u"type": u"string",
                    },
                    u"field_type": {
                        u"choices": [
                            [u"int", u"Integer"],
                            [u"multiple_choice", u"Multiple Choice"],
                            [u"choice", u"Choice"],
                            [u"bool", u"Yes/No"],
                            [u"text", u"Text"],
                            [u"date", u"Date"],
                            [u"textline", u"Text line (String)"],
                        ],
                        u"description": u"Data type of this field",
                        u"enum": [
                            u"int",
                            u"multiple_choice",
                            u"choice",
                            u"bool",
                            u"text",
                            u"date",
                            u"textline",
                        ],
                        u"enumNames": [
                            u"Integer",
                            u"Multiple Choice",
                            u"Choice",
                            u"Yes/No",
                            u"Text",
                            u"Date",
                            u"Text line (String)",
                        ],
                        u"title": u"Field type",
                        u"type": u"string",
                    },
                    u"name": {
                        u"description": u"Field name (alphanumeric, lowercase)",
                        u"pattern": u"^[a-z_0-9]*$",
                        u"title": u"Name",
                        u"type": u"string",
                    },
                    u"required": {
                        u"description": u"Whether or not the field is required",
                        u"title": u"Required",
                        u"type": u"boolean",
                    },
                    u"title": {
                        u"description": u"Title",
                        u"maxLength": 48,
                        u"title": u"Title",
                        u"type": u"string",
                    },
                    u"values": {
                        u"description": u"List of values that are allowed for "
                                        u"this field",
                        u"items": {
                            u"description": u"",
                            u"factory": u"Text line (String)",
                            u"title": u"",
                            u"type": u"string",
                        },
                        u"title": u"Allowed values",
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
            u"field_order": [u'id', u'fields', u'assignments'],
            u"properties": {
                u"assignments": assignments_schema,
                u"fields": fields_schema,
                u"id": id_schema,
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

    @browsing
    def test_field_titles_are_translated(self, browser):
        self.login(self.propertysheets_manager, browser)

        headers = self.api_headers.copy()
        headers.update({'Accept-Language': 'de-ch'})

        browser.open(
            view="@propertysheet-metaschema",
            headers=headers,
        )

        properties = browser.json['properties']

        self.assertItemsEqual(
            [
                u'ID',
                u'Felder',
                u'Slots',
            ],
            [prop['title'] for prop in properties.values()]
        )

        field_properties = properties['fields']['items']['properties']
        self.assertItemsEqual(
            [
                u'Name',
                u'Feld-Typ',
                u'Titel',
                u'Beschreibung',
                u'Pflichtfeld',
                u'Default',
                u'Wertebereich',
            ],
            [prop['title'] for prop in field_properties.values()]
        )

    @browsing
    def test_field_descriptions_are_translated(self, browser):
        self.login(self.propertysheets_manager, browser)

        headers = self.api_headers.copy()
        headers.update({'Accept-Language': 'de-ch'})

        browser.open(
            view="@propertysheet-metaschema",
            headers=headers,
        )

        properties = browser.json['properties']

        self.assertItemsEqual(
            [
                u'ID dieses Property Sheets',
                u'Felder',
                u'F\xfcr welche Arten von Inhalten dieses Property Sheet verf\xfcgbar sein soll',
            ],
            [prop['description'] for prop in properties.values()]
        )

        field_properties = properties['fields']['items']['properties']
        self.assertItemsEqual(
            [
                u'Name (Alphanumerisch, nur Kleinbuchstaben)',
                u'Datentyp f\xfcr dieses Feld',
                u'Titel',
                u'Beschreibung',
                u'Angabe, ob Benutzer dieses Feld zwingend ausf\xfcllen m\xfcssen',
                u'Default-Wert f\xfcr dieses Feld',
                u'Liste der erlaubten Werte f\xfcr das Feld',
            ],
            [prop['description'] for prop in field_properties.values()]
        )
