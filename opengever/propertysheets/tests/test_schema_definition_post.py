from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase
from zope import schema
from zope.schema import getFieldNamesInOrder
import json


class TestSchemaDefinitionPost(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_property_sheet_schema_definition_post_defaults(self, browser):
        self.login(self.manager, browser)

        data = {"fields": [{"name": "foo", "field_type": "text"}]}
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )
        storage = PropertySheetSchemaStorage()
        self.assertEqual(1, len(storage.list()))
        definition = storage.get("question")

        self.assertEqual("question", definition.name)
        schema_class = definition.schema_class

        self.assertEqual(["foo"], schema_class.names())
        field = schema_class["foo"]
        self.assertIsInstance(field, schema.Text)
        self.assertEqual(
            u"foo", field.title, "Expected title to default to name"
        )
        self.assertEqual(u"", field.description)
        self.assertFalse(field.required)

    @browsing
    def test_property_sheet_schema_definition_post(self, browser):
        self.login(self.manager, browser)

        data = {
            "fields": [
                {
                    "name": "foo",
                    "field_type": "bool",
                    "title": u"Y/N",
                    "description": u"yes or no",
                    "required": True,
                }
            ],
            "assignments": [u"IDocumentMetadata.document_type.question"],
        }
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        self.assertEqual(
            {
                u"assignments": [u"IDocumentMetadata.document_type.question"],
                u"fieldsets": [
                    {
                        u"behavior": u"plone",
                        u"fields": [u"foo"],
                        u"id": u"default",
                        u"title": u"Default",
                    }
                ],
                u"properties": {
                    u"foo": {
                        u"description": u"yes or no",
                        u"factory": u"Yes/No",
                        u"title": u"Y/N",
                        u"type": u"boolean",
                    },
                },
                u"required": [u"foo"],
                u"title": u"question",
                u"type": u"object",
            },
            browser.json,
        )
        self.assertEqual("application/json+schema", browser.mimetype)

        storage = PropertySheetSchemaStorage()
        self.assertEqual(1, len(storage.list()))
        definition = storage.get("question")

        self.assertEqual("question", definition.name)
        self.assertEqual((u"IDocumentMetadata.document_type.question",),
                         definition.assignments)
        schema_class = definition.schema_class

        self.assertEqual(["foo"], schema_class.names())
        field = schema_class["foo"]
        self.assertIsInstance(field, schema.Bool)
        self.assertEqual(
            u"Y/N",
            field.title,
        )
        self.assertEqual(u"yes or no", field.description)
        self.assertTrue(field.required)

    @browsing
    def test_property_sheet_schema_definition_post_supports_all_field_types(self, browser):
        self.login(self.manager, browser)

        data = {
            "fields": [
                {
                    "name": "yn",
                    "field_type": u"bool",
                    "title": u"ja oder nein"
                },
                {
                    "name": "wahl",
                    "field_type": u"choice",
                    "title": u"w\xe4hl was",
                    "values": [u"eins", u"zwei"]
                },
                {
                    "name": "nummer",
                    "field_type": u"int",
                    "title": u"zahl"
                },
                {
                    "name": "text",
                    "field_type": u"text",
                    "title": u"text",
                    "required": True
                },
                {
                    "name": "zeiletext",
                    "field_type": u"textline",
                    "title": u"zeile"
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
        self.assertEqual(1, len(storage.list()))
        definition = storage.get("meinschema")

        self.assertEqual(
            ["yn", "wahl", "nummer", "text", "zeiletext"],
            getFieldNamesInOrder(definition.schema_class)
        )

    @browsing
    def test_property_sheet_schema_definition_post_replaces_existing_schema(self, browser):
        self.login(self.manager, browser)
        create(Builder("property_sheet_schema").named("question"))

        data = {
            "fields": [
                {
                    "name": "foo",
                    "field_type": "bool",
                    "title": u"Y/N",
                    "description": u"yes or no",
                    "required": True,
                }
            ],
        }
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual(1, len(storage.list()))
        definition = storage.get("question")

        self.assertEqual("question", definition.name)
        self.assertEqual(["foo"], definition.schema_class.names())

    @browsing
    def test_property_sheet_schema_definition_post_requires_valid_assignment(
        self, browser
    ):
        self.login(self.manager, browser)

        data = {
            "fields": [{"name": "foo", "field_type": "bool"}],
            "assignments": [u"fail"],
        }
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/invalidassignment",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"The assignment 'fail' is invalid.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual([], storage.list())

    @browsing
    def test_property_sheet_schema_definition_post_requires_unique_assignment(
        self, browser
    ):
        self.login(self.manager, browser)
        create(
            Builder("property_sheet_schema")
            .named("fixture")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
        )

        data = {
            "fields": [{"name": "foo", "field_type": "bool"}],
            "assignments": [u"IDocumentMetadata.document_type.question"],
        }
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/invalidassignment",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"The assignment 'IDocumentMetadata.document_type."
                            "question' is already in use.",
                "type": "BadRequest",
            },
            browser.json,
        )
        storage = PropertySheetSchemaStorage()
        self.assertEqual(1, len(storage.list()))

    @browsing
    def test_property_sheet_schema_definition_post_requires_name(
        self, browser
    ):
        self.login(self.manager, browser)

        data = {"fields": [{"name": "foo", "field_type": "bool"}]}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Missing parameter sheet_name.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual([], storage.list())

    @browsing
    def test_property_sheet_schema_definition_post_requires_valid_name(
        self, browser
    ):
        self.login(self.manager, browser)

        data = {"fields": [{"name": "foo", "field_type": "bool"}]}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/in-val.id",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"The name 'in-val.id' is invalid.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual([], storage.list())

    @browsing
    def test_property_sheet_schema_definition_post_requires_fields(
        self, browser
    ):
        self.login(self.manager, browser)

        data = {"fields": []}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/foo",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Missing or invalid field definitions.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual([], storage.list())

    @browsing
    def test_property_sheet_schema_definition_post_requires_valid_fields_type(
        self, browser
    ):
        self.login(self.manager, browser)

        data = {"fields": {"foo": None}}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/foo",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Missing or invalid field definitions.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual([], storage.list())

    @browsing
    def test_property_sheet_schema_definition_post_prevents_duplicate_field_name(
        self, browser
    ):
        self.login(self.manager, browser)

        dupe1 = {"name": "dupe", "field_type": "text"}
        dupe2 = {"name": "foo", "field_type": "text"}
        data = {"fields": [dupe1, dupe1, dupe2, dupe2]}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/foo",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Duplicate fields 'dupe', 'foo'.",
                "type": "BadRequest",
            },
            browser.json,
        )

        storage = PropertySheetSchemaStorage()
        self.assertEqual([], storage.list())

    @browsing
    def test_property_sheet_schema_definition_post_invalid_type(self, browser):
        self.login(self.manager, browser)

        data = {"fields": [{"name": "foo", "field_type": "invalid"}]}
        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/question",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )
        self.assertDictContainsSubset(
            {
                "type": "BadRequest",
            },
            browser.json,
        )
        storage = PropertySheetSchemaStorage()
        self.assertEqual([], storage.list())

    @browsing
    def test_non_managers_cannot_post(self, browser):
        self.login(self.administrator, browser)

        data = {"fields": [{"name": "foo", "field_type": "text"}]}
        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets/test",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )
