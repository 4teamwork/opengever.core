from ftw.builder import Builder
from ftw.builder import create
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.testing import IntegrationTestCase
from plone.restapi.interfaces import IFieldDeserializer
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter


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
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
        )

        deserialized_data = self.deserializer(
            {
                "IDocumentMetadata.document_type.question": {
                    "choose": {"title": "two", "token": "two"}
                }
            }
        )
        self.assertEqual(
            {
                "IDocumentMetadata.document_type.question": {
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
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
        )

        deserialized_data = self.deserializer(
            {"IDocumentMetadata.document_type.question": {"choose": "two"}}
        )
        self.assertEqual(
            {
                "IDocumentMetadata.document_type.question": {
                    "choose": "two",
                },
            },
            deserialized_data,
        )
