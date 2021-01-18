from ftw.builder import Builder
from ftw.builder import create
from mock import Mock
from opengever.propertysheets.assignment import DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX
from opengever.propertysheets.field import PropertySheetField
from opengever.propertysheets.tests.fixture import fixture_assignment_factory
from opengever.testing import FunctionalTestCase
from zope.schema import ValidationError
from zope.schema.interfaces import RequiredMissing
from zope.schema.interfaces import WrongType


class TestPropertySheetField(FunctionalTestCase):

    def setUp(self):
        super(TestPropertySheetField, self).setUp()

        self.field = PropertySheetField(
            "some_request_key",
            "some_attribute",
            DOCUMENT_TYPE_ASSIGNMENT_SLOT_PREFIX,
            fixture_assignment_factory,
        )

    def test_validation_fails_when_required_field_of_mandatory_sheet_is_not_provided(
        self,
    ):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_simple_boolean_field()
        )

        self.request["some_request_key"] = [u"question"]

        with self.assertRaises(RequiredMissing):
            self.field.validate({})

    def test_validation_fails_when_field_of_mandatory_sheet_is_of_wrong_type(
        self,
    ):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_simple_boolean_field()
        )

        self.request["some_request_key"] = [u"question"]

        with self.assertRaises(WrongType):
            self.field.validate(
                {"IDocumentMetadata.document_type.question": {"yesorno": "X"}}
            )

    def test_validation_fails_when_providing_extra_fields_to_mandatory_sheet(
        self,
    ):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_simple_boolean_field()
        )

        self.request["some_request_key"] = [u"question"]

        with self.assertRaises(ValidationError) as cm:
            self.field.validate(
                {
                    "IDocumentMetadata.document_type.question": {
                        "yesorno": True,
                        "qux": "i should fail",
                    }
                }
            )
        self.assertEqual("Cannot set properties 'qux'.", cm.exception.message)

    def test_validation_fails_when_required_field_of_optional_sheet_is_not_provided(
        self,
    ):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.contract")
            .with_simple_boolean_field()
        )

        with self.assertRaises(RequiredMissing):
            self.field.validate(
                {u"IDocumentMetadata.document_type.contract": {}}
            )

    def test_validation_fails_when_field_of_optional_sheet_is_of_wrong_type(
        self,
    ):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.contract")
            .with_simple_boolean_field()
        )

        with self.assertRaises(WrongType):
            self.field.validate(
                {"IDocumentMetadata.document_type.contract": {"yesorno": "X"}}
            )

    def test_validation_fails_when_providing_extra_fields_to_optional_sheet(
        self,
    ):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.contract")
            .with_simple_boolean_field()
        )

        with self.assertRaises(ValidationError) as cm:
            self.field.validate(
                {
                    "IDocumentMetadata.document_type.contract": {
                        "yesorno": True,
                        "qux": "i should fail",
                    }
                }
            )
        self.assertEqual("Cannot set properties 'qux'.", cm.exception.message)

    def test_validation_fails_when_providing_nonexisting_sheets(
        self,
    ):
        with self.assertRaises(ValidationError) as cm:
            self.field.validate(
                {
                    "some.inexisting.sheet": {
                        "yesorno": True,
                    }
                }
            )
        self.assertEqual(
            u"Custom properties for 'some.inexisting.sheet' supplied, but no "
            u"such property sheet is defined.",
            cm.exception.message,
        )

    def test_validation_fails_when_providing_sheets_not_available_on_context(
        self,
    ):
        create(
            Builder("property_sheet_schema")
            .named("somename")
            .assigned_to_slots(u"IDocumentMetadata.document_type.regulations")
            .with_simple_boolean_field()
        )

        with self.assertRaises(ValidationError) as cm:
            self.field.validate(
                {
                    "IDocumentMetadata.document_type.regulations": {
                        "yesorno": True,
                    }
                }
            )
        self.assertEqual(
            u"The property sheet 'somename' cannot be used in this "
            u"context with assignment "
            u"'IDocumentMetadata.document_type.regulations'",
            cm.exception.message,
        )

    def test_successful_field_validation_with_active_slot_from_request_key(
        self,
    ):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_simple_boolean_field()
        )

        self.request["some_request_key"] = [u"question"]

        self.field.validate(
            {"IDocumentMetadata.document_type.question": {"yesorno": True}}
        )

    def test_successful_field_validation_with_active_slot_from_context_attribute(
        self,
    ):
        create(
            Builder("property_sheet_schema")
            .named("schema")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_simple_boolean_field()
        )

        context = Mock()
        context.some_attribute = u"question"
        field = self.field.bind(context)

        field.validate(
            {"IDocumentMetadata.document_type.question": {"yesorno": True}}
        )
