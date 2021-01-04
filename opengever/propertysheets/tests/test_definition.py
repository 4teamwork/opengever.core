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

    def test_create_schema_definition_with_one_assignment(self):
        definition = PropertySheetSchemaDefinition.create(
            "myschema", assignments=[u"foo.bar"]
        )

        self.assertEqual("myschema", definition.name)
        self.assertEqual((u"foo.bar",), definition.assignments)

    def test_create_schema_definition_with_mulitple_assignments(self):
        definition = PropertySheetSchemaDefinition.create(
            "myschema", assignments=[u"foo.bar", u"qux"]
        )

        self.assertEqual("myschema", definition.name)
        self.assertEqual((u"foo.bar", u"qux"), definition.assignments)

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

    def test_add_choice_field_with_simple_values(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = ['one', 'two', 'three']
        definition.add_field(
            "choice", u"chooseone", u"choose", u"", False, values=choices
        )

        self.assertEqual(["chooseone"], definition.schema_class.names())
        field = definition.schema_class['chooseone']
        self.assertIsInstance(field, schema.Choice)

        voc_values = [each.value for each in field.vocabulary]
        voc_tokens = [each.token for each in field.vocabulary]

        self.assertEqual(choices, voc_values)
        self.assertEqual(choices, voc_tokens)

    def test_add_choice_field_requires_values(self):
        definition = PropertySheetSchemaDefinition.create("foo")

        with self.assertRaises(InvalidFieldTypeDefinition):
            definition.add_field(
                "choice", u"chooseone", u"choose", u"", False, values=None
            )

        with self.assertRaises(InvalidFieldTypeDefinition):
            definition.add_field(
                "choice", u"chooseone", u"choose", u"", False, values=[]
            )

    def test_add_choice_field_prevents_duplicate_values(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = ['duplicate', 'duplicate']
        with self.assertRaises(ValueError):
            definition.add_field(
                "choice", u"chooseone", u"choose", u"", False, values=choices
            )

    def test_add_non_choice_field_prevents_adding_values(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        with self.assertRaises(InvalidFieldTypeDefinition):
            definition.add_field(
                "int", u"num", u"A number", u"Put a number.", True, values=[1]
            )

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

    def test_enforces_valid_assignments_as_fieldnames(self):
        definition = PropertySheetSchemaDefinition.create("foo")

        with self.assertRaises(InvalidFieldTypeDefinition):
            definition.add_field(
                "bool", u"in val id!", u"", u"", True
            )
