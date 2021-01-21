from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from jsonschema import Draft4Validator
from opengever.testing import IntegrationTestCase


class TestCustomPropertiesFieldSchemaEndpoint(IntegrationTestCase):

    @browsing
    def test_document_schema_contains_available_property_sheet(self, browser):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo", u"some input", u"", True)
        )

        self.login(self.regular_user, browser)
        schema = browser.open(
            self.leaf_repofolder,
            view="@schema/opengever.document.document",
            method="GET",
            headers=self.api_headers,
        ).json

        # smoke-test to validate the schema
        Draft4Validator.check_schema(schema)

        props = schema["properties"]["custom_properties"]["properties"]
        # we just validate presence of the schema, serialization of the
        # complete schema is tested in functional tests
        self.assertIsNotNone(props)
        self.assertIn(
            "IDocumentMetadata.document_type.question",
            props,
        )

    @browsing
    def test_sheet_assigned_to_multiple_slots_is_serialized_for_each_slot(
        self, browser
    ):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(
                u"IDocumentMetadata.document_type.contract",
                u"IDocumentMetadata.document_type.question",
            )
            .with_field("text", u"foo", u"some input", u"", True)
        )

        self.login(self.regular_user, browser)
        schema = browser.open(
            self.leaf_repofolder,
            view="@schema/opengever.document.document",
            method="GET",
            headers=self.api_headers,
        ).json

        # smoke-test to validate the schema
        Draft4Validator.check_schema(schema)

        props = schema["properties"]["custom_properties"]["properties"]
        # we just validate presence of the schema, serialization of the
        # complete schema is tested in functional tests
        self.assertIsNotNone(props)
        self.assertIn("IDocumentMetadata.document_type.contract", props)
        self.assertIn("IDocumentMetadata.document_type.question", props)
        self.assertEqual(
            props["IDocumentMetadata.document_type.question"],
            props["IDocumentMetadata.document_type.question"],
        )

    @browsing
    def test_representation_when_no_schemas_are_available(self, browser):
        self.login(self.regular_user, browser)
        schema = browser.open(
            self.leaf_repofolder,
            view="@schema/opengever.document.document",
            method="GET",
            headers=self.api_headers,
        ).json

        # smoke-test to validate the schema
        Draft4Validator.check_schema(schema)

        self.assertEqual(
            {
                u"behavior": u"opengever.document.behaviors.customproperties.IDocumentCustomProperties",
                u"description": u'Contains data for user defined custom properties.',
                u"title": u"Custom properties",
                u"type": u"null",
            },
            schema["properties"]["custom_properties"],
        )
