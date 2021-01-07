from ftw.testbrowser import browsing
from opengever.document.behaviors.customproperties import ICustomProperties
from opengever.testing import IntegrationTestCase
import json


class TestDocumentCustomProperties(IntegrationTestCase):

    @browsing
    def test_property_sheet_set_via_api(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, method="GET", headers=self.api_headers)
        self.assertEqual(None, browser.json["custom_properties"])

        data = {"custom_properties": {"foo": "bar"}}

        browser.open(
            self.document,
            method="PATCH",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        self.assertEqual(
            data["custom_properties"], ICustomProperties(self.document).custom_properties
        )
        browser.open(self.document, method="GET", headers=self.api_headers)
        self.assertEqual(data["custom_properties"], browser.json["custom_properties"])

    @browsing
    def test_property_sheet_validated_via_api_patch(self, browser):
        self.login(self.manager, browser)

        self.document.document_type = u"question"

        # set property sheet schema definition
        data = {"fields": {"foo": {"field_type": "text", "required": True}},
                "assignments": ["IDocumentMetadata.document_type.question"]}
        browser.open(
            view="@propertysheets/question",
            method="POST",
            data=json.dumps(data),
            headers=self.api_headers,
        )

        bad_data = {"custom_properties": {"question": {"qux": "123"}}}
        with browser.expect_http_error(400):
            browser.open(
                self.document,
                method="PATCH",
                data=json.dumps(bad_data),
                headers=self.api_headers,
            )

        good_data = {"custom_properties": {"question": {"foo": "123"}}}
        browser.open(
            self.document,
            method="PATCH",
            data=json.dumps(good_data),
            headers=self.api_headers,
        )
        self.assertEqual(
            good_data["custom_properties"], ICustomProperties(self.document).custom_properties
        )
