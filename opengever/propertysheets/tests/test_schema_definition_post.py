from ftw.testbrowser import browsing
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase
from zope import schema
import json


class TestSchemaDefinitionPost(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_property_sheet_schema_definition_post_defaults(self, browser):
        self.login(self.manager, browser)

        data = {"fields": {"foo": {"field_type": "text"}}}
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
            "fields": {
                "foo": {
                    "field_type": "bool",
                    "title": u"Y/N",
                    "description": u"yes or no",
                    "required": True,
                }
            },
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
    def test_property_sheet_schema_definition_post_replaces_existing_schema(self, browser):
        self.login(self.manager, browser)

        definition = PropertySheetSchemaDefinition.create("question")
        storage = PropertySheetSchemaStorage()
        storage.save(definition)

        data = {
            "fields": {
                "foo": {
                    "field_type": "bool",
                    "title": u"Y/N",
                    "description": u"yes or no",
                    "required": True,
                }
            },
        }
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

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
            "fields": {"foo": {"field_type": "bool"}},
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
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create(
            "fixture",
            assignments=[u"IDocumentMetadata.document_type.question"]
        )
        storage.save(fixture)

        data = {
            "fields": {"foo": {"field_type": "bool"}},
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
        self.assertEqual([], storage.list())

    @browsing
    def test_property_sheet_schema_definition_post_requires_unique_assignment(
        self, browser
    ):
        self.login(self.manager, browser)
        storage = PropertySheetSchemaStorage()
        fixture = PropertySheetSchemaDefinition.create(
            "fixture",
            assignments=[u"IDocumentMetadata.document_type.question"]
        )
        storage.save(fixture)

        data = {
            "fields": {"foo": {"field_type": "bool"}},
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
        self.assertEqual(1, len(storage.list()))

    @browsing
    def test_property_sheet_schema_definition_post_requires_name(
        self, browser
    ):
        self.login(self.manager, browser)

        data = {"fields": {"foo": {"field_type": "bool"}}}
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

        data = {"fields": {"foo": {"field_type": "bool"}}}
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
    def test_property_sheet_schema_definition_post_invalid_type(self, browser):
        self.login(self.manager, browser)

        data = {"fields": {"foo": {"field_type": "invalid"}}}
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

        data = {"fields": {"foo": {"field_type": "text"}}}
        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets/test",
                method="POST",
                data=json.dumps(data),
                headers=self.api_headers,
            )
