from ftw.builder import Builder
from ftw.builder import create
from jsonschema import Draft4Validator
from opengever.propertysheets.assignment import DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX
from opengever.propertysheets.field import PropertySheetField
from opengever.propertysheets.tests.fixture import fixture_assignment_factory
from opengever.testing import FunctionalTestCase
from plone.restapi.types.interfaces import IJsonSchemaProvider
from zope.component import getMultiAdapter


class TestPropertySheetFieldSchemaProvider(FunctionalTestCase):

    maxDiff = None

    def setUp(self):
        super(TestPropertySheetFieldSchemaProvider, self).setUp()

        self.field = PropertySheetField(
            "unused_request_key",
            "unused_attribute",
            DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX,
            fixture_assignment_factory,
        )

    @property
    def schema_provider(self):
        return getMultiAdapter(
            (self.field, self.portal, self.request), IJsonSchemaProvider
        )

    def test_returns_json_schema_only_for_assignment_slots(self):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(
                u"IDocumentMetadata.document_type.question",
                u"IDocumentMetadata.document_type.offer",  # not in factory
            )
            .with_field("text", u"foo", u"some input", u"", True)
        )
        create(
            Builder("property_sheet_schema")
            .named("not_inlcuded")
            .assigned_to_slots(u"IDocumentMetadata.document_type.request")
            .with_field("text", u"bar", u"discard me", u"", False)
        )

        json_schema = self.schema_provider.get_schema()
        expected = {
            "type": "object",
            "title": u"Property sheets with custom properties",
            "description": "",
            "properties": {
                u"IDocumentMetadata.document_type.question": {
                    "assignments": [
                        u"IDocumentMetadata.document_type.question",
                        u"IDocumentMetadata.document_type.offer",
                    ],
                    "fieldsets": [
                        {
                            "behavior": "plone",
                            "fields": ["foo"],
                            "id": "default",
                            "title": "Default",
                        }
                    ],
                    "properties": {
                        u"foo": {
                            u"description": u"",
                            u"factory": u"Text",
                            u"title": u"some input",
                            u"type": u"string",
                            u"widget": u"textarea",
                        }
                    },
                    "required": ["foo"],
                    "title": "schema",
                    "type": "object",
                }
            },
        }
        self.assertEqual(expected, json_schema)

        # smoke-test to validate the schema
        Draft4Validator.check_schema(json_schema)

    def test_sheet_assigned_to_multiple_slots_is_serialized_for_each_slot(
        self,
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

        json_schema = self.schema_provider.get_schema()
        schema_properties = json_schema["properties"]

        self.assertIn(
            "IDocumentMetadata.document_type.contract",
            schema_properties,
        )
        self.assertIn(
            "IDocumentMetadata.document_type.question",
            schema_properties,
        )
        self.assertEqual(
            schema_properties["IDocumentMetadata.document_type.contract"],
            schema_properties["IDocumentMetadata.document_type.question"],
        )

    def test_returns_empty_dict_when_no_schemas_are_available(self):
        json_schema = self.schema_provider.get_schema()
        self.assertEqual(
            {
                "description": u"",
                "title": u"Property sheets with custom properties",
                "type": "null",
            },
            json_schema,
        )

        # smoke-test to validate the schema
        Draft4Validator.check_schema(json_schema)
