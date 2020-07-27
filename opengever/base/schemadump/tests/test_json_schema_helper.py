from collections import OrderedDict
from opengever.base.schemadump.json_schema_helper import JSONSchema
from opengever.base.schemadump.json_schema_helper import order_dict
from os.path import join
from tempfile import mkdtemp
from textwrap import dedent
import shutil
import unittest


class TestJSONSchema(unittest.TestCase):

    def setUp(self):
        self.tempdir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_constructs_minimal_schema(self):
        schema = JSONSchema()
        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)
        self.assertIsInstance(serialized, OrderedDict)

    def test_constructor_accepts_title(self):
        schema = JSONSchema(title=u'Foobar')
        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'title': 'Foobar',
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)
        self.assertIsInstance(serialized, OrderedDict)

    def test_constructor_accepts_type(self):
        schema = JSONSchema(type_='array')
        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'array',
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)
        self.assertIsInstance(serialized, OrderedDict)

    def test_constructor_accepts_additional_properties_flag(self):
        schema = JSONSchema(additional_properties=False)
        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'additionalProperties': False,
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)
        self.assertIsInstance(serialized, OrderedDict)

    def test_add_property(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'})
        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
            },
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)
        self.assertIsInstance(serialized, OrderedDict)
        self.assertIsInstance(serialized['properties'], OrderedDict)
        self.assertIsInstance(serialized['properties']['foo'], OrderedDict)

    def test_add_property_supports_required_kwarg(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'}, required=True)
        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
            },
            'required': ['foo'],
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_drop_property(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'})
        schema.add_property('bar', {'type': 'string'})
        schema.drop_property('foo')

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'bar': {'type': 'string'},
            },
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_drop_property_with_missing_property(self):
        schema = JSONSchema()
        schema.drop_property('doesnt-exist')

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
        }
        serialized = schema.serialize()
        self.assertEqual(expected, serialized)

    def test_drop_required_property(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'}, required=True)
        schema.add_property('bar', {'type': 'string'}, required=True)
        schema.drop_property('foo')

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'bar': {'type': 'string'},
            },
            'required': ['bar'],
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_dropping_last_property_removes_properties_key(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'})
        schema.drop_property('foo')

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_set_required(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'})
        schema.set_required('foo')

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
            },
            'required': ['foo'],
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_set_required_doesnt_add_property_twice_to_requireds(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'})
        schema.set_required('foo')
        schema.set_required('foo')

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
            },
            'required': ['foo'],
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_set_not_required(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'}, required=True)
        schema.add_property('bar', {'type': 'string'}, required=True)
        schema.set_not_required('foo')

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
                'bar': {'type': 'string'},
            },
            'required': ['bar'],
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_set_not_required_removes_empty_requires_list(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'}, required=True)
        schema.set_not_required('foo')

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
            },
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_require_any_of(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'})
        schema.add_property('bar', {'type': 'string'})
        schema.require_any_of(['foo', 'bar'])

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
                'bar': {'type': 'string'},
            },
            'allOf': [
                {
                    'anyOf': [
                        {'required': ['foo']},
                        {'required': ['bar']}
                    ],
                },
            ],

        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_set_field_order(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'})
        schema.add_property('bar', {'type': 'string'})
        schema.set_field_order(['foo', 'bar'])

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
                'bar': {'type': 'string'},
            },
            'field_order': ['foo', 'bar'],
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_add_definition(self):
        schema = JSONSchema()
        subschema = JSONSchema()
        subschema.add_property('subfoo', {'type': 'string'})
        schema.add_definition('sub', subschema)

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'definitions': {
                'sub': {
                    'type': 'object',
                    'properties': {
                        'subfoo': {'type': 'string'},
                    },
                }
            }
        }
        serialized = schema.serialize()

        self.assertDictEqual(expected, serialized)

    def test_make_optional_properties_nullable(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'}, required=True)
        schema.add_property('bar', {'type': 'string'})
        schema.make_optional_properties_nullable()

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
                'bar': {'type': ['null', 'string']},
            },
            'required': ['foo'],
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_make_optional_properties_nullable_with_enum(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'}, required=True)
        schema.add_property('bar', {'type': 'integer', 'enum': [1, 2]})
        schema.make_optional_properties_nullable()

        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
                'bar': {'type': ['null', 'integer'],
                        'enum': [None, 1, 2]},
            },
            'required': ['foo'],
        }
        serialized = schema.serialize()

        self.assertEqual(expected, serialized)

    def test_dumping_schema(self):
        schema = JSONSchema()
        schema.add_property('foo', {'type': 'string'}, required=True)
        expected = dedent("""
        {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "foo": {
                    "type": "string"
                }
            },
            "required": [
                "foo"
            ]
        }
        """).strip() + '\n'

        dump_path = join(self.tempdir, 'test.schema.json')
        schema.dump(dump_path)

        with open(dump_path) as f:
            actual = f.read()

        self.assertEqual(expected, actual)


class TestOrderDictHelper(unittest.TestCase):

    def test_returns_ordered_dict_instance(self):
        dct = {'foo': 1}

        self.assertEqual(OrderedDict({'foo': 1}), order_dict(dct))
        self.assertIsInstance(order_dict(dct), OrderedDict)

    def test_orders_keys_alphabetically_by_default(self):
        dct = {'b': 1, 'a': 1, 'd': 1, 'e': 1, 'c': 1}

        self.assertEqual(
            ['a', 'b', 'c', 'd', 'e'],
            order_dict(dct).keys(),
        )

    def test_orders_keys_in_given_order(self):
        dct = {'fourth': 1, 'first': 1, 'third': 1, 'fifth': 1, 'second': 1}

        order = ['first', 'second', 'third', 'fourth', 'fifth']
        self.assertEqual(order, order_dict(dct, order).keys())

    def test_falls_back_to_alphabetical_for_unspecified_keys(self):
        dct = {
            'fourth': 1, 'first': 1, 'third': 1, 'fifth': 1, 'second': 1,
            'b': 1, 'a': 1, 'd': 1, 'e': 1, 'c': 1,
        }

        order = ['first', 'second', 'third', 'fourth', 'fifth']
        self.assertEqual(
            ['first', 'second', 'third', 'fourth', 'fifth',
             'a', 'b', 'c', 'd', 'e'],
            order_dict(dct, order).keys())

    def test_puts_keys_with_specified_order_first(self):
        dct = {
            'b': 1, 'a': 1, 'd': 1, 'e': 1, 'c': 1,
            'Xfourth': 1, 'Xfirst': 1, 'Xthird': 1, 'Xfifth': 1, 'Xsecond': 1,
        }

        order = ['Xfirst', 'Xsecond', 'Xthird', 'Xfourth', 'Xfifth']
        self.assertEqual(
            ['Xfirst', 'Xsecond', 'Xthird', 'Xfourth', 'Xfifth',
             'a', 'b', 'c', 'd', 'e'],
            order_dict(dct, order).keys())

    def test_ignores_missing_keys(self):
        dct = {'foo': 1}

        self.assertEqual(
            OrderedDict({'foo': 1}),
            order_dict(dct, key_order=['bar']),
        )
