from opengever.propertysheets.definition import isidentifier
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exceptions import InvalidFieldTypeDefinition
from opengever.testing.test_case import FunctionalTestCase
from opengever.testing.test_case import TestCase
from zope import schema


class TestIsIdentifier(TestCase):

    def test_isidentifier_truthy(self):
        self.assertTrue(isidentifier('asd'))
        self.assertTrue(isidentifier('asd12'))
        self.assertTrue(isidentifier('asd_12'))
        self.assertTrue(isidentifier('AsdASdd_12_KUX'))

    def test_whitespace_is_invalid_identifier(self):
        self.assertFalse(isidentifier(' asd'))
        self.assertFalse(isidentifier('asd '))
        self.assertFalse(isidentifier('as dd'))
        self.assertFalse(isidentifier('asd\n'))
        self.assertFalse(isidentifier('\nasd'))
        self.assertFalse(isidentifier('\tasd'))

    def test_various_other_chars_are_invalid_identifier(self):
        self.assertFalse(isidentifier(u'f\xfc\xfc'))
        self.assertFalse(isidentifier('a%sd'))
        self.assertFalse(isidentifier('asd*'))
        self.assertFalse(isidentifier('asd\\x'))
        self.assertFalse(isidentifier('asd\\as'))

    def test_cant_start_with_number(self):
        self.assertFalse(isidentifier('1bah'))

    def test_cant_be_keyword(self):
        self.assertFalse(isidentifier('def'))
        self.assertFalse(isidentifier('break'))
        self.assertFalse(isidentifier('import'))


class TestSchemaDefinition(FunctionalTestCase):

    def test_create_empty_schema_definition(self):
        definition = PropertySheetSchemaDefinition.create("myschema")

        self.assertEqual("myschema", definition.name)
        self.assertEqual(
            [], definition.schema_class.names(),
            "No fields should be defined initially"
        )

    def test_add_field_sets_correct_field_properties(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "bool", u"yesorno", u"Yes or no", u"Say yes or no.", False
        )

        self.assertEqual(["yesorno"], definition.schema_class.names())
        field = definition.schema_class['yesorno']

        self.assertEqual(u'Yes or no', field.title)
        self.assertEqual(u'Say yes or no.', field.description)
        self.assertFalse(field.required)

    def test_add_bool_field(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field("bool", u"yesorno", u"y/n", u"", False)

        self.assertEqual(["yesorno"], definition.schema_class.names())
        field = definition.schema_class['yesorno']
        self.assertIsInstance(field, schema.Bool)

    def test_add_int_field(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "int", u"num", u"A number", u"Put a number.", True
        )

        self.assertEqual(["num"], definition.schema_class.names())
        field = definition.schema_class['num']
        self.assertIsInstance(field, schema.Int)

    def test_add_text_field(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "text", u"blabla", u"Text", u"Say something long.", True
        )

        self.assertEqual(["blabla"], definition.schema_class.names())
        field = definition.schema_class['blabla']
        self.assertIsInstance(field, schema.Text)

    def test_add_textline_field(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "textline", u"bla", u"Textline", u"Say something short.", True
        )

        self.assertEqual(["bla"], definition.schema_class.names())
        field = definition.schema_class['bla']
        self.assertIsInstance(field, schema.TextLine)

    def test_enforces_valid_identifiers_as_fieldnames(self):
        definition = PropertySheetSchemaDefinition.create("foo")

        with self.assertRaises(InvalidFieldTypeDefinition):
            definition.add_field(
                "bool", u"in val id!", u"", u"", True
            )
