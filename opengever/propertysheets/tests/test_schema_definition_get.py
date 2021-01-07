from ftw.testbrowser import browsing
from jsonschema import Draft4Validator
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase


class TestSchemaDefinitionGet(IntegrationTestCase):

    maxDiff = None

    @browsing
    def test_property_sheet_schema_definition_get_empty_list(self, browser):
        self.login(self.regular_user, browser)

        browser.open(
            view="@propertysheets", method="GET", headers=self.api_headers
        )
        self.assertEqual(
            {
                u"items": [],
                u"@id": u"http://nohost/plone/@propertysheets",
            },
            browser.json,
        )

    @browsing
    def test_property_sheet_schema_definition_get_list(self, browser):
        self.login(self.regular_user, browser)

        definition1 = PropertySheetSchemaDefinition.create("schema1")
        definition2 = PropertySheetSchemaDefinition.create("schema2")

        storage = PropertySheetSchemaStorage()
        storage.save(definition1)
        storage.save(definition2)

        browser.open(
            view="@propertysheets", method="GET", headers=self.api_headers
        )
        self.assertEqual(
            {
                u"@id": u"http://nohost/plone/@propertysheets",
                u"items": [
                    {u"@id": u"http://nohost/plone/@propertysheets/schema1"},
                    {u"@id": u"http://nohost/plone/@propertysheets/schema2"},
                ],
            },
            browser.json,
        )

    @browsing
    def test_property_sheet_schema_definition_get_sheet_schema(self, browser):
        self.login(self.regular_user, browser)

        definition = PropertySheetSchemaDefinition.create(
            "schema", assignments=[u"IDocumentMetadata.document_type.question"]
        )
        definition.add_field("bool", u"yesorno", u"y/n", u"", False)
        choices = ["one", "two", "three"]
        definition.add_field(
            "choice", u"chooseone", u"choose", u"", False, values=choices
        )
        storage = PropertySheetSchemaStorage()
        storage.save(definition)

        browser.open(
            view="@propertysheets/schema",
            method="GET",
            headers=self.api_headers,
        )

        self.assertEqual(
            {
                u"assignments": [u"IDocumentMetadata.document_type.question"],
                u"fieldsets": [
                    {
                        u"behavior": u"plone",
                        u"fields": [u"yesorno", u"chooseone"],
                        u"id": u"default",
                        u"title": u"Default",
                    }
                ],
                u"properties": {
                    u"chooseone": {
                        u"choices": [
                            [u"one", u"one"],
                            [u"two", u"two"],
                            [u"three", u"three"],
                        ],
                        u"description": u"",
                        u"enum": [u"one", u"two", u"three"],
                        u"enumNames": [u"one", u"two", u"three"],
                        u"factory": u"Choice",
                        u"title": u"choose",
                        u"type": u"string",
                    },
                    u"yesorno": {
                        u"description": u"",
                        u"factory": u"Yes/No",
                        u"title": u"y/n",
                        u"type": u"boolean",
                    },
                },
                u"title": u"schema",
                u"type": u"object",
            },
            browser.json,
        )
        self.assertEqual("application/json+schema", browser.mimetype)
        Draft4Validator.check_schema(browser.json)

    @browsing
    def test_property_sheet_schema_definition_get_404(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(404):
            browser.open(
                view="@propertysheets/idonotexist",
                method="GET",
                headers=self.api_headers
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Sheet 'idonotexist' not found.",
                "type": "NotFound",
            },
            browser.json,
        )

    @browsing
    def test_property_sheet_schema_definition_get_too_many_path_segments(self, browser):
        self.login(self.regular_user, browser)

        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/foo/bar",
                method="GET",
                headers=self.api_headers
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Must supply either zero or one parameters.",
                "type": "BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_anonymous_cannot_get_property_sheets(self, browser):
        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets",
                method="GET",
                headers=self.api_headers
            )
