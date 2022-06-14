from datetime import date
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

    def test_serializes_complex_propertysheet(self):
        self.login(self.regular_user)

        choices = [u'Rot', u'Gr\xfcn', u'Blau']
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("bool", u"yesorno", u"Yes or no", u"", True)
            .with_field("choice", u"choose", u"Choose", u"", True, values=choices)
            .with_field("multiple_choice", u"choosemulti",
                        u"Choose Multi", u"", True, values=choices)
            .with_field("int", u"num", u"Number", u"", True)
            .with_field("text", u"text", u"Some lines of text", u"", True)
            .with_field("textline", u"textline", u"A line of text", u"", True)
            .with_field("date", u"birthday", u"Birthday", u"", True)
        )

        self.document.document_type = u'question'
        IDocumentCustomProperties(self.document).custom_properties = {
            'IDocumentMetadata.document_type.question': {
                'yesorno': True,
                'choose': u'Gr\xfcn',
                'choosemulti': set([u'Gr\xfcn', u'Rot']),
                'num': 42,
                'text': u'B\xfcrgermeister\nLorem Ipsum',
                'textline': u'B\xfcrgermeister',
                'birthday': date(2022, 1, 30),

            }
        }

        self.assertEqual(
            {
                "IDocumentMetadata.document_type.question": {
                    u'birthday': u'2022-01-30',
                    u'choose': {
                        u'title': u'Gr\xfcn',
                        u'token': u'Gr\\xfcn',
                    },
                    u'choosemulti': [
                        {
                            u'title': u'Gr\xfcn',
                            u'token': u'Gr\\xfcn',
                        },
                        {
                            u'title': u'Rot',
                            u'token': u'Rot',
                        },
                    ],
                    u'num': 42,
                    u'text': u'B\xfcrgermeister\nLorem Ipsum',
                    u'textline': u'B\xfcrgermeister',
                    u'yesorno': True,
                }
            },
            self.serializer(),
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

    def test_serializes_multiple_choice_fields_as_a_list_of_token_title_object(self):
        self.login(self.regular_user)

        choices = [u"one", u"two", u"dr\xfc\xfc"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field(
                "multiple_choice", u"multichoose", u"Multi Choose", u"", True, values=choices
            )
        )
        self.document.document_type = u"question"
        IDocumentCustomProperties(self.document).custom_properties = {
            "IDocumentMetadata.document_type.question": {
                "multichoose": [u"dr\xfc\xfc", u"one"],
            }
        }

        self.assertEqual(
            {
                "IDocumentMetadata.document_type.question": {
                    "multichoose": [
                        {"title": u"dr\xfc\xfc",
                         "token": u"dr\xfc\xfc".encode("unicode_escape")},
                        {"title": u"one", "token": u"one"}
                    ]
                }
            },
            self.serializer(),
        )

    def test_does_not_skip_invalid_vocabulary_values_during_serialization(self):
        self.login(self.regular_user)

        choices = ["just one"]
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field(
                "choice", u"choose", u"Choose", u"", True, values=choices
            )
            .with_field(
                "multiple_choice", u"multichoose", u"Multi Choose", u"", True, values=choices
            )
        )
        self.document.document_type = u"question"
        IDocumentCustomProperties(self.document).custom_properties = {
            "IDocumentMetadata.document_type.question": {
                "choose": "invalid choice",
                "multichoose": ["just one", "invalid choice"]
            }
        }

        self.assertEqual(
            {
                "IDocumentMetadata.document_type.question": {
                    "choose": {
                        "title": u"invalid choice",
                        "token": u"invalid choice"
                    },
                    "multichoose": [
                        {
                            "title": u"just one",
                            "token": u"just one"
                        },
                        {
                            "title": u"invalid choice",
                            "token": u"invalid choice"
                        },
                    ]
                }
            },
            self.serializer(),
        )

    def test_correctly_serializes_none_values_for_choice_fields(self):
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
                "choose": None,
            }
        }

        self.assertEqual(
            {
                "IDocumentMetadata.document_type.question": {
                    "choose": None,
                }
            },
            self.serializer(),
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
