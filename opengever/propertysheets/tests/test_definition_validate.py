from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.testing.test_case import FunctionalTestCase
from zope.schema.interfaces import RequiredMissing
from zope.schema.interfaces import ValidationError
from zope.schema.interfaces import WrongType


class TestSchemaDefinitionValidate(FunctionalTestCase):

    def test_schema_validation_validates_types(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "bool", u"yesorno", u"Yes or no", u"Say yes or no.", True
        )

        with self.assertRaises(WrongType):
            definition.validate({"yesorno": "i will fail"})

    def test_schema_validation_validates_presence(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "bool", u"yesorno", u"Yes or no", u"Say yes or no.", True
        )

        with self.assertRaises(RequiredMissing):
            definition.validate({})

    def test_schema_validation_passes_for_valid_data(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "bool", u"yesorno", u"Yes or no", u"Say yes or no.", True
        )

        definition.validate({"yesorno": True})

    def test_schema_validation_allows_empty_when_nothing_required(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "bool", u"yesorno", u"Yes or no", u"Say yes or no.", False
        )

        definition.validate({})

    def test_schema_validation_allows_none_when_nothing_required(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "bool", u"yesorno", u"Yes or no", u"Say yes or no.", False
        )

        definition.validate(None)

    def test_schema_validation_disallows_wrong_type(self):
        definition = PropertySheetSchemaDefinition.create("foo")

        with self.assertRaises(WrongType) as cm:
            definition.validate([])

        self.assertEqual(
            "Only 'dict' is allowed for properties.", cm.exception.message
        )

    def test_schema_validation_prevents_setting_extra_properties(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "bool", u"yesorno", u"Yes or no", u"Say yes or no.", True
        )

        with self.assertRaises(ValidationError) as cm:
            definition.validate(
                {
                    "yesorno": False,
                    "extra": "I will fail!",
                    "blub": 123,
                }
            )
        self.assertEqual(
            "Cannot set properties 'extra', 'blub'.", cm.exception.message
        )
