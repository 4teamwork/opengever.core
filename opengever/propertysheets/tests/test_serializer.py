from ftw.builder import Builder
from ftw.builder import create
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.testing import IntegrationTestCase
from plone.restapi.interfaces import IFieldSerializer
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter


class TestPropertySheetFieldSerializer(IntegrationTestCase):

    ANNOTATION_KEY = (
        "opengever.document.behaviors.customproperties"
        ".IDocumentCustomProperties.custom_properties"
    )

    def setUp(self):
        super(TestPropertySheetFieldSerializer, self).setUp()

        with self.login(self.regular_user):
            self.annotations = IAnnotations(self.document)
            field = IDocumentCustomProperties["custom_properties"]
            self.serializer = getMultiAdapter(
                (field, self.document, self.request), IFieldSerializer
            )

    def test_serializes_choice_fields_as_token_title_object(self):
        self.login(self.regular_user)

        choices = [u"one", u"two", u"dr\xfc\xfc"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
        )
        self.document.document_type = u"question"
        IDocumentCustomProperties(self.document).custom_properties = {
            "IDocumentMetadata.document_type.question": {
                "choose": u"dr\xfc\xfc",
            }
        }

        self.assertEqual(
            {
                "IDocumentMetadata.document_type.question": {
                    "choose": {
                        "title": u"dr\xfc\xfc",
                        "token": u"dr\xfc\xfc".encode("unicode_escape")
                    }
                }
            },
            self.serializer(),
        )

    def test_skips_invalid_vocabulary_values_during_serialization(self):
        self.login(self.regular_user)

        choices = ["just one"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
        )
        self.document.document_type = u"question"
        IDocumentCustomProperties(self.document).custom_properties = {
            "IDocumentMetadata.document_type.question": {
                "choose": "invalid choice",
            }
        }

        self.assertEqual(
            {"IDocumentMetadata.document_type.question": {}}, self.serializer()
        )

    def test_greafcully_returns_incorrect_toplevel_data_structure(self):
        self.login(self.regular_user)

        self.annotations[self.ANNOTATION_KEY] = ["broken", "data"]
        self.assertEqual(["broken", "data"], self.serializer())

    def test_greafcully_returns_data_for_no_longer_existing_property_sheets(
        self,
    ):
        self.login(self.regular_user)

        data = {"deleted_sheet": {"attr": "value"}}
        self.annotations[self.ANNOTATION_KEY] = data

        self.assertEqual(data, self.serializer())

    def test_greafcully_returns_incorrect_sheet_data(self):
        self.login(self.regular_user)

        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"text", u"Text", u"", True)
        )
        self.document.document_type = u"question"
        data = {
            "IDocumentMetadata.document_type.question": "invalid, not a dict"
        }
        self.annotations[self.ANNOTATION_KEY] = data

        self.assertEqual(data, self.serializer())
