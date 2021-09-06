from opengever.propertysheets.definition import isidentifier
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exceptions import InvalidFieldTypeDefinition
from opengever.propertysheets.exportimport import dottedname
from opengever.propertysheets.testing import dummy_default_factory_42
from opengever.propertysheets.testing import dummy_default_factory_fr
from opengever.propertysheets.testing import dummy_default_factory_some_text
from opengever.propertysheets.testing import dummy_default_factory_some_text_line
from opengever.propertysheets.testing import dummy_default_factory_true
from opengever.testing.test_case import FunctionalTestCase
from opengever.testing.test_case import TestCase
from plone import api
from zope import schema
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import WrongType


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


class TestSchemaDefinitionRichComparison(FunctionalTestCase):

    def test_eq_truthy(self):
        self.assertTrue(
            PropertySheetSchemaDefinition.create('foo')
            == PropertySheetSchemaDefinition.create('foo')
        )

    def test_eq_falsy_other_name(self):
        self.assertFalse(
            PropertySheetSchemaDefinition.create('foo')
            == PropertySheetSchemaDefinition.create('bar')
        )

    def test_eq_falsy_other_object(self):
        self.assertFalse(
            PropertySheetSchemaDefinition.create('foo') == object()
        )

    def test_eq_falsy_other_primitive(self):
        self.assertFalse(
            PropertySheetSchemaDefinition.create('foo') == 123
        )

    def test_eq_falsy_none(self):
        val = None  # prevent code style complaints via indirection
        self.assertFalse(
            PropertySheetSchemaDefinition.create('foo') == val
        )

    def test_ne_falsy(self):
        self.assertFalse(
            PropertySheetSchemaDefinition.create('foo')
            != PropertySheetSchemaDefinition.create('foo')
        )

    def test_ne_truthy_other_name(self):
        self.assertTrue(
            PropertySheetSchemaDefinition.create('foo')
            != PropertySheetSchemaDefinition.create('qux')
        )

    def test_ne_truthy_other_object(self):
        self.assertTrue(
            PropertySheetSchemaDefinition.create('foo') != object()
        )

    def test_ne_truthy_other_primitive(self):
        self.assertTrue(
            PropertySheetSchemaDefinition.create('foo') != 123
        )

    def test_ne_truthy_none(self):
        val = None  # prevent code style complaints via indirection
        self.assertTrue(
            PropertySheetSchemaDefinition.create('foo') != val
        )


class TestSchemaDefinitionSolrFields(FunctionalTestCase):

    maxDiff = None

    def test_bool_field_solr_dynamic_field_info(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field("bool", u"yesorno", u"y/n", u"", False)

        self.assertEqual(
            {
                'yesorno_custom_field_boolean': {
                    'name': 'yesorno_custom_field_boolean',
                    'title': u'y/n',
                    'type': u'boolean',
                }
            },
            definition.get_solr_dynamic_field_schema()
        )

    def test_choice_field_solr_dynamic_field_info(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = ['one', 'two', 'three']
        definition.add_field(
            "choice", u"chooseone", u"choose", u"", False, values=choices
        )

        self.assertEqual(
            {
                'chooseone_custom_field_string': {
                    'name': 'chooseone_custom_field_string',
                    'title': u'choose',
                    'type': u'string',
                }
            },
            definition.get_solr_dynamic_field_schema()
        )

    def test_int_field_solr_dynamic_field_info(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "int", u"num", u"A number", u"Put a number.", True
        )

        self.assertEqual(
            {
                'num_custom_field_int': {
                    'name': 'num_custom_field_int',
                    'title': u'A number',
                    'type': u'integer',
                }
            },
            definition.get_solr_dynamic_field_schema()
        )

    def test_text_field_solr_dynamic_field_info(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "text", u"blabla", u"Text", u"Say something long.", True
        )

        self.assertEqual({}, definition.get_solr_dynamic_field_schema())

    def test_textline_field_solr_dynamic_field_info(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "textline", u"bla", u"Textline", u"Say something short.", True
        )

        self.assertEqual(
            {
                'bla_custom_field_string': {
                    'name': 'bla_custom_field_string',
                    'title': u'Textline',
                    'type': u'string',
                }
            },
            definition.get_solr_dynamic_field_schema()
        )


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
            "myschema",
            assignments=[u"IDocumentMetadata.document_type.contract"]
        )

        self.assertEqual("myschema", definition.name)
        self.assertEqual(
            (u"IDocumentMetadata.document_type.contract",),
            definition.assignments
        )

    def test_create_schema_definition_with_mulitple_assignments(self):
        definition = PropertySheetSchemaDefinition.create(
            "myschema",
            assignments=[
                u"IDocumentMetadata.document_type.contract",
                u"IDocumentMetadata.document_type.question"
            ]
        )

        self.assertEqual("myschema", definition.name)
        self.assertEqual(
            (u"IDocumentMetadata.document_type.contract",
             u"IDocumentMetadata.document_type.question"),
            definition.assignments
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

    def test_add_bool_field_with_static_default(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field("bool", u"yesorno", u"y/n", u"", False,
                             default=True)

        field = definition.schema_class['yesorno']
        self.assertEqual(True, field.default)

    def test_add_bool_field_rejects_default_with_wrong_type(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        with self.assertRaises(WrongType):
            definition.add_field("bool", u"yesorno", u"y/n", u"", False,
                                 default=['a string'])

    def test_add_bool_field_with_default_factory(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "bool", u"yesorno", u"y/n", u"", False,
            default_factory=dottedname(dummy_default_factory_true))

        field = definition.schema_class['yesorno']
        self.assertEqual(dummy_default_factory_true, field.defaultFactory)
        self.assertEqual(True, field.default)

    def test_add_bool_field_with_default_expression(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "bool", u"yesorno", u"y/n", u"", False,
            default_expression="portal/validate_email")

        field = definition.schema_class['yesorno']
        self.assertEqual("portal/validate_email", field.default_expression)
        self.assertEqual(True, field.defaultFactory())
        self.assertEqual(True, field.default)

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
        voc_titles = [each.token for each in field.vocabulary]
        voc_tokens = [each.token for each in field.vocabulary]

        self.assertEqual(choices, voc_values)
        self.assertEqual(choices, voc_titles)
        self.assertEqual(choices, voc_tokens)

    def test_add_choice_field_with_unicode_values(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = [u"bl\xe4h", u"blub"]
        definition.add_field(
            "choice", u"chooseone", u"choose", u"", False, values=choices
        )

        self.assertEqual(["chooseone"], definition.schema_class.names())
        field = definition.schema_class["chooseone"]
        self.assertIsInstance(field, schema.Choice)

        voc_values = [each.value for each in field.vocabulary]
        voc_titles = [each.title for each in field.vocabulary]
        voc_tokens = [each.token for each in field.vocabulary]

        self.assertEqual([u"bl\xe4h", u"blub"], voc_values)
        self.assertEqual([u"bl\xe4h", u"blub"], voc_titles)
        self.assertEqual(
            [u"bl\xe4h".encode("unicode_escape"), "blub"], voc_tokens
        )

    def test_add_choice_field_with_static_default(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = [u'de', u'fr', u'en']
        definition.add_field(
            "choice", u"language", u"Language", u"", True,
            values=choices, default=u'fr'
        )

        field = definition.schema_class["language"]
        self.assertEqual(u'fr', field.default)

    def test_add_choice_field_with_default_factory(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = [u'de', u'fr', u'en']
        definition.add_field(
            "choice", u"language", u"Language", u"", True, values=choices,
            default_factory=dottedname(dummy_default_factory_fr)
        )

        field = definition.schema_class["language"]
        self.assertEqual(dummy_default_factory_fr, field.defaultFactory)
        self.assertEqual(u'fr', field.default)

    def test_add_choice_field_with_default_expression(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = [u'de', u'fr', u'en']
        definition.add_field(
            "choice", u"language", u"Language", u"", True, values=choices,
            default_expression="portal/language"
        )

        field = definition.schema_class["language"]
        self.assertEqual("portal/language", field.default_expression)
        self.assertEqual(u'en', field.defaultFactory())
        self.assertEqual(u'en', field.default)

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

    def test_add_choice_field_rejects_integer_values(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = [1, 2]
        with self.assertRaises(InvalidFieldTypeDefinition):
            definition.add_field(
                "choice", u"chooseone", u"choose", u"", False, values=choices
            )

    def test_add_choice_field_rejects_boolean_values(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = [True, False]
        with self.assertRaises(InvalidFieldTypeDefinition):
            definition.add_field(
                "choice", u"chooseone", u"choose", u"", False, values=choices
            )

    def test_add_choice_field_rejects_mixed_values(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = ["blah", u'blub', 1, True]
        with self.assertRaises(InvalidFieldTypeDefinition):
            definition.add_field(
                "choice", u"chooseone", u"choose", u"", False, values=choices
            )

    def test_add_choice_field_rejects_default_not_in_vocab(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        choices = [u'de', u'fr', u'en']

        with self.assertRaises(ConstraintNotSatisfied):
            definition.add_field(
                "choice", u"language", u"Language", u"", True,
                values=choices, default=u'not-in-vocab'
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

    def test_add_int_field_with_static_default(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "int", u"num", u"A number", u"Put a number.", True,
            default=42
        )

        field = definition.schema_class['num']
        self.assertEqual(42, field.default)

    def test_add_int_field_with_default_factory(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "int", u"num", u"A number", u"Put a number.", True,
            default_factory=dottedname(dummy_default_factory_42)
        )

        field = definition.schema_class['num']
        self.assertEqual(dummy_default_factory_42, field.defaultFactory)
        self.assertEqual(42, field.default)

    def test_add_text_field(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "text", u"blabla", u"Text", u"Say something long.", True
        )

        self.assertEqual(["blabla"], definition.schema_class.names())
        field = definition.schema_class['blabla']
        self.assertIsInstance(field, schema.Text)

    def test_add_text_field_with_static_default(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "text", u"blabla", u"Text", u"Say something long.", True,
            default=u'Some text'
        )

        field = definition.schema_class['blabla']
        self.assertEqual(u'Some text', field.default)

    def test_add_text_field_with_default_factory(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "text", u"blabla", u"Text", u"Say something long.", True,
            default_factory=dottedname(dummy_default_factory_some_text)
        )

        field = definition.schema_class['blabla']
        self.assertEqual(dummy_default_factory_some_text, field.defaultFactory)
        self.assertEqual(u'Some text', field.default)

    def test_add_textline_field(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "textline", u"bla", u"Textline", u"Say something short.", True
        )

        self.assertEqual(["bla"], definition.schema_class.names())
        field = definition.schema_class['bla']
        self.assertIsInstance(field, schema.TextLine)

    def test_add_textline_field_with_static_default(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "textline", u"bla", u"Textline", u"Say something short.", True,
            default=u'Some text line'
        )

        field = definition.schema_class['bla']
        self.assertEqual(u'Some text line', field.default)

    def test_add_textline_field_with_default_factory(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "textline", u"bla", u"Textline", u"Say something short.", True,
            default_factory=dottedname(dummy_default_factory_some_text_line)
        )

        field = definition.schema_class['bla']
        self.assertEqual(dummy_default_factory_some_text_line, field.defaultFactory)
        self.assertEqual(u'Some text line', field.default)

    def test_add_textline_field_with_default_expression(self):
        definition = PropertySheetSchemaDefinition.create("foo")
        definition.add_field(
            "textline", u"userid", u"User ID from Member object", u"", True,
            default_expression="member/getId"
        )

        field = definition.schema_class['userid']
        self.assertEqual("member/getId", field.default_expression)
        self.assertEqual(u'test_user_1_', field.defaultFactory())
        self.assertEqual(u'test_user_1_', field.default)

    def test_add_textline_field_with_default_from_member(self):
        definition = PropertySheetSchemaDefinition.create("foo")

        definition.add_field(
            "textline", u"userid", u"Location from Member property", u"", True,
            default_from_member={"property": "location"}
        )

        member = api.user.get_current()
        field = definition.schema_class['userid']
        self.assertEqual('{"property": "location"}', field.default_from_member)

        member.setProperties({'location': 'Bern'})
        self.assertEqual(u'Bern', field.defaultFactory())
        self.assertEqual(u'Bern', field.default)

        member.setProperties({'location': 'St. Gallen'})
        self.assertEqual(u'St. Gallen', field.defaultFactory())
        self.assertEqual(u'St. Gallen', field.default)

    def test_enforces_valid_assignments_as_fieldnames(self):
        definition = PropertySheetSchemaDefinition.create("foo")

        with self.assertRaises(InvalidFieldTypeDefinition):
            definition.add_field(
                "bool", u"in val id!", u"", u"", True
            )
