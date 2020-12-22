from ftw.testbrowser import browsing
from opengever.document.behaviors.propertysheets import IPropertySheets
from opengever.testing import IntegrationTestCase
import json


class TestPropertySheet(IntegrationTestCase):
    @browsing
    def test_set_property_sheet_schema(self, browser):
        self.login(self.manager, browser)

        browser.open(view="@propertysheets", method="GET", headers=self.api_headers)
        self.assertEqual([], browser.json)

        # set property sheet schema definition
        data = {"fields": {"foo": {"type": "text", "required": True}}}
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        expected = {
            u"required": [u"foo"],
            u"id": u"question",
            u"fieldsets": [
                {
                    u"fields": [u"foo"],
                    u"id": u"default",
                    u"behavior": u"plone",
                    u"title": u"Default",
                }
            ],
            u"properties": {
                u"foo": {
                    u"widget": u"textarea",
                    u"title": u"foo",
                    u"type": u"string",
                    u"description": u"",
                    u"factory": u"Text",
                }
            },
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_property_sheet_set_via_api(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, method="GET", headers=self.api_headers)
        self.assertEqual(None, browser.json["property_sheets"])

        data = {"property_sheets": {"foo": "bar"}}

        browser.open(
            self.document,
            method="PATCH",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        self.assertEqual(
            data["property_sheets"], IPropertySheets(self.document).property_sheets
        )
        browser.open(self.document, method="GET", headers=self.api_headers)
        self.assertEqual(data["property_sheets"], browser.json["property_sheets"])

    @browsing
    def test_property_sheet_validated_via_api_patch(self, browser):
        self.login(self.manager, browser)

        self.document.document_type = u"question"

        # set property sheet schema definition
        data = {"fields": {"foo": {"type": "text", "required": True}}}
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        bad_data = {"property_sheets": {"question": {"qux": "123"}}}
        with browser.expect_http_error(400):
            browser.open(
                self.document,
                method="PATCH",
                data=json.dumps(bad_data),
                headers=self.api_headers,
            )

        good_data = {"property_sheets": {"question": {"foo": "123"}}}
        browser.open(
            self.document,
            method="PATCH",
            data=json.dumps(good_data),
            headers=self.api_headers,
        )
        self.assertEqual(
            good_data["property_sheets"], IPropertySheets(self.document).property_sheets
        )
