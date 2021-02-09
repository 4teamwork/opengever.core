from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from opengever.testing import IntegrationTestCase


class TestSchemaDefinitionDelete(IntegrationTestCase):

    @browsing
    def test_property_sheet_schema_definition_delete_existing_schema(self, browser):
        self.login(self.manager, browser)
        create(Builder("property_sheet_schema").named("sheet"))
        self.assertEqual(3, len(PropertySheetSchemaStorage()))

        browser.open(
            view="@propertysheets/sheet", method="DELETE", headers=self.api_headers
        )
        self.assertEqual(browser.status_code, 204)
        self.assertEqual(2, len(PropertySheetSchemaStorage()))

    @browsing
    def test_property_sheet_schema_definition_delete_requires_name(
        self, browser
    ):
        self.login(self.manager, browser)

        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets",
                method="DELETE",
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"Missing parameter sheet_name.",
                "type": "BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_property_sheet_schema_definition_delete_requires_valid_sheet(
        self, browser
    ):
        self.login(self.manager, browser)

        with browser.expect_http_error(400):
            browser.open(
                view="@propertysheets/idontexist",
                method="DELETE",
                headers=self.api_headers,
            )

        self.assertDictContainsSubset(
            {
                u"message": u"The property sheet 'idontexist' does not exist.",
                "type": "BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_non_managers_cannot_delete(self, browser):
        self.login(self.administrator, browser)
        create(Builder("property_sheet_schema").named("sheet"))

        with browser.expect_unauthorized():
            browser.open(
                view="@propertysheets/sheet",
                method="DELETE",
                headers=self.api_headers,
            )
