from ftw.builder import Builder
from ftw.builder import create
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.testing import IntegrationTestCase
from plone.restapi.interfaces import IFieldDeserializer
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.schema.interfaces import ConstraintNotSatisfied


class TestPropertySheetFieldDeserializer(IntegrationTestCase):

    def setUp(self):
        super(TestPropertySheetFieldDeserializer, self).setUp()

        with self.login(self.regular_user):
            self.annotations = IAnnotations(self.document)
            field = IDocumentCustomProperties["custom_properties"]
            self.deserializer = getMultiAdapter(
                (field, self.document, self.request), IFieldDeserializer
            )

    def test_deserializes_choice_fields_from_token_to_value(self):
        self.login(self.regular_user)

        choices = ["one", "two", "five"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.contract")
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
        )

        deserialized_data = self.deserializer(
            {
                "IDocumentMetadata.document_type.contract": {
                    "choose": {"title": "two", "token": "two"}
                }
            }
        )
        self.assertEqual(
            {
                "IDocumentMetadata.document_type.contract": {
                    "choose": "two",
                },
            },
            deserialized_data,
        )

    def test_deserializes_flat_choice_fields(self):
        self.login(self.regular_user)

        choices = ["one", "two", "five"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.contract")
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
        )

        deserialized_data = self.deserializer(
            {"IDocumentMetadata.document_type.contract": {"choose": "two"}}
        )
        self.assertEqual(
            {
                "IDocumentMetadata.document_type.contract": {
                    "choose": "two",
                },
            },
            deserialized_data,
        )

    def test_deserializes_empty_multiple_choice(self):
        self.login(self.regular_user)

        choices = ["one", "two", "five"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.contract")
            .with_field(
                "multiple_choice", u"choose", u"Choose", u"", False, values=choices
            )
        )

        deserialized_data = self.deserializer(
            {
                "IDocumentMetadata.document_type.contract": {
                    "choose": None
                }
            }
        )
        self.assertEqual(
            {
                "IDocumentMetadata.document_type.contract": {
                    "choose": set([]),
                },
            },
            deserialized_data,
        )

    def test_deserializes_current_invalid_value_for_choice_field(self):
        self.login(self.regular_user)

        choices = ["one", "two", "five"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.contract")
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
        )

        IDocumentCustomProperties(self.document).custom_properties = {
            u"IDocumentMetadata.document_type.contract": {u"choose": "once_valid"}
        }
        deserialized_data = self.deserializer(
            {
                "IDocumentMetadata.document_type.contract": {
                    "choose": "once_valid"
                }
            }
        )
        self.assertEqual(
            {
                "IDocumentMetadata.document_type.contract": {
                    "choose": 'once_valid',
                },
            },
            deserialized_data,
        )

        IDocumentCustomProperties(self.document).custom_properties = {
            u"IDocumentMetadata.document_type.contract": {u"choose": "one"}
        }

        with self.assertRaises(ConstraintNotSatisfied):
            self.deserializer(
                {
                    "IDocumentMetadata.document_type.contract": {
                        "choose": "once_valid"
                    }
                }
            )

    def test_deserializes_current_invalid_value_for_multiple_choice_field(self):
        self.login(self.regular_user)

        choices = ["one", "two", "five"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.contract")
            .with_field(
                "multiple_choice", u"choose", u"Choose", u"", False, values=choices
            )
        )

        IDocumentCustomProperties(self.document).custom_properties = {
            u"IDocumentMetadata.document_type.contract": {u"choose": ["once_valid", "two"]}
        }
        deserialized_data = self.deserializer(
            {
                "IDocumentMetadata.document_type.contract": {
                    "choose": ["once_valid", "one"]
                }
            }
        )
        self.assertEqual(
            {
                "IDocumentMetadata.document_type.contract": {
                    "choose": set(["once_valid", "one"]),
                },
            },
            deserialized_data,
        )

        IDocumentCustomProperties(self.document).custom_properties = {
            u"IDocumentMetadata.document_type.contract": {u"choose": ["two"]}
        }
        with self.assertRaises(ConstraintNotSatisfied):
            self.deserializer(
                {
                    "IDocumentMetadata.document_type.contract": {
                        "choose": ["once_valid", "one"]
                    }
                }
            )
