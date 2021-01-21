from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.testing import IntegrationTestCase
import json


class TestDocumentCustomPropertiesPatch(IntegrationTestCase):

    @browsing
    def test_correctly_stores_custom_properties_with_all_field_types(self, browser):
        self.login(self.manager, browser)

        choices = ["one", "two", "three"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("bool", u"yesorno", u"Yes or no", u"", True)
            .with_field("choice", u"choose", u"Choose", u"", True, values=choices)
            .with_field("int", u"num", u"Number", u"", True)
            .with_field("text", u"text", u"Some lines of text", u"", True)
            .with_field("textline", u"textline", u"A line of text", u"", True)
        )
        self.document.document_type = u"question"

        self.login(self.regular_user, browser)
        good_data = {
            "custom_properties": {
                "IDocumentMetadata.document_type.question": {
                    "yesorno": False,
                    "choose": "two",
                    "num": 123,
                    "text": u"bl\xe4\nblub",
                    "textline": u"bl\xe4",
                },
            }
        }
        browser.open(
            self.document,
            method="PATCH",
            data=json.dumps(good_data),
            headers=self.api_headers,
        )
        self.assertEqual(
            good_data["custom_properties"],
            IDocumentCustomProperties(self.document).custom_properties,
        )

    @browsing
    def test_does_not_allow_arbitrary_json_in_custom_properties(self, browser):
        self.login(self.regular_user, browser)

        bad_data = {"custom_properties": {"foo": "bar"}}
        with browser.expect_http_error(400):
            browser.open(
                self.document,
                method="PATCH",
                data=json.dumps(bad_data),
                headers=self.api_headers,
            )
        self.assertDictContainsSubset(
            {
                "type": "BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_raises_validation_error_when_selected_assignment_validation_fails(
        self, browser
    ):
        self.login(self.manager, browser)

        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", True)
        )
        self.document.document_type = u"question"

        self.login(self.regular_user, browser)
        bad_data = {
            "custom_properties": {
                "IDocumentMetadata.document_type.question": {"qux": "123"}
            }
        }
        with browser.expect_http_error(400):
            browser.open(
                self.document,
                method="PATCH",
                data=json.dumps(bad_data),
                headers=self.api_headers,
            )
        self.assertDictContainsSubset(
            {
                "type": "BadRequest",
            },
            browser.json,
        )

    @browsing
    def test_validates_required_field_in_selected_assignment(
        self, browser
    ):
        self.login(self.manager, browser)
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", True)
        )
        self.document.document_type = u"question"

        self.login(self.regular_user, browser)

        good_data = {
            "custom_properties": {
                "IDocumentMetadata.document_type.question": {"foo": "blabla"}
            }
        }
        browser.open(
            self.document,
            method="PATCH",
            data=json.dumps(good_data),
            headers=self.api_headers,
        )
        self.assertEqual(
            good_data["custom_properties"],
            IDocumentCustomProperties(self.document).custom_properties,
        )

    @browsing
    def test_allows_empty_data_if_only_non_required_fields_in_selected_assignment(self, browser):
        self.login(self.manager, browser)
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", False)
        )
        self.document.document_type = u"question"

        self.login(self.regular_user, browser)
        good_data = {"custom_properties": {}}
        browser.open(
            self.document,
            method="PATCH",
            data=json.dumps(good_data),
            headers=self.api_headers,
        )
        self.assertEqual(
            {},
            IDocumentCustomProperties(self.document).custom_properties,
        )

    @browsing
    def test_allows_other_valid_property_sheet_fields_next_to_selected_assignment(self, browser):
        self.login(self.manager, browser)

        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", True)
        )
        create(
            Builder("property_sheet_schema")
            .named("schema2")
            .assigned_to_slots(u"IDocumentMetadata.document_type.report")
            .with_field("int", u"num", u"A number", u"Put a number.", True)
        )
        self.document.document_type = u"report"

        self.login(self.regular_user, browser)
        good_data = {
            "custom_properties": {
                "IDocumentMetadata.document_type.question": {"foo": "blabla"},
                "IDocumentMetadata.document_type.report": {"num": 123},
            }
        }
        browser.open(
            self.document,
            method="PATCH",
            data=json.dumps(good_data),
            headers=self.api_headers,
        )
        self.assertEqual(
            good_data["custom_properties"],
            IDocumentCustomProperties(self.document).custom_properties,
        )


class TestDocumentCustomPropertiesPost(IntegrationTestCase):

    @browsing
    def test_stores_custom_properties_when_no_document_type_selected(self, browser):
        self.login(self.manager, browser)
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", False)
        )

        self.login(self.regular_user, browser)
        property_data = {
            "IDocumentMetadata.document_type.question": {
                "foo": u"f\xfc"
            }
        }
        data = {
            "@type": "opengever.document.document",
            "file": {
                "data": "foo bar",
                "filename": "test.txt",
            },
            "custom_properties": property_data,
        }

        with self.observe_children(self.dossier) as children:
            browser.open(self.dossier, data=json.dumps(data), method="POST",
                         headers=self.api_headers)

        self.assertEqual(property_data, browser.json['custom_properties'])
        self.assertEqual(1, len(children['added']))
        new_document = children['added'].pop()
        self.assertEqual(
            property_data,
            IDocumentCustomProperties(new_document).custom_properties,
        )

    @browsing
    def test_validates_custom_properties_when_document_type_selected(self, browser):
        self.login(self.manager, browser)
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", False)
        )

        self.login(self.regular_user, browser)
        bad_data = {
            "IDocumentMetadata.document_type.question": {
                "qux": u"i am invalid"
            }
        }
        data = {
            "@type": "opengever.document.document",
            "file": {
                "data": "foo bar",
                "filename": "test.txt",
            },
            "document_type": "question",
            "custom_properties": bad_data,
        }

        with browser.expect_http_error(400):
            browser.open(self.dossier, data=json.dumps(data), method="POST",
                         headers=self.api_headers)

        self.assertIn("'field': 'custom_properties'", browser.json["message"])
        self.assertDictContainsSubset({u"type": u"BadRequest"}, browser.json)

    @browsing
    def test_validates_custom_properties_when_no_document_type_selected(self, browser):
        self.login(self.manager, browser)
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", False)
        )

        self.login(self.regular_user, browser)
        bad_data = {
            "IDocumentMetadata.document_type.question": {
                "qux": u"i am invalid"
            }
        }
        data = {
            "@type": "opengever.document.document",
            "file": {
                "data": "foo bar",
                "filename": "test.txt",
            },
            "custom_properties": bad_data,
        }

        with browser.expect_http_error(400):
            browser.open(self.dossier, data=json.dumps(data), method="POST",
                         headers=self.api_headers)

        self.assertIn("'field': 'custom_properties'", browser.json["message"])
        self.assertDictContainsSubset({u"type": u"BadRequest"}, browser.json)


class TestDocumentCustomPropertiesGet(IntegrationTestCase):

    @browsing
    def test_always_returns_all_custom_property_data(self, browser):
        self.login(self.regular_user, browser)

        props_data = {
            "IDocumentMetadata.document_type.question": {
                "foo": u"f\xfc",
            },
            "something": {
                "else": 123,
            }
        }
        IDocumentCustomProperties(self.document).custom_properties = props_data

        browser.open(self.document, method="GET", headers=self.api_headers)
        self.assertEqual(props_data, browser.json['custom_properties'])
