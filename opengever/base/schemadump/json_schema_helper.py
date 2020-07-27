from collections import OrderedDict
from copy import deepcopy
from jsonschema import Draft4Validator
from opengever.base.utils import pretty_json
import logging


SCHEMA_KEYS_ORDER = [
    '$schema',
    'type',
    'items',
    'title',
    'additionalProperties',
    'properties',
    'required',
    'allOf',
    'anyOf',
    'field_order',
]

PROPERTY_KEYS_ORDER = (
    'type',
    'title',
    'format',
    'maxLength',
    'description',
    '_zope_schema_type',
    'default',
    'enum',
)


log = logging.getLogger(__name__)


class JSONSchema(object):
    """Convenience class to build and manipulate JSON schemas more easily.
    """

    def __init__(self, title=None, type_='object', additional_properties=None):
        self._schema = OrderedDict([
            ('$schema', 'http://json-schema.org/draft-04/schema#'),
            ('type', type_),
        ])

        if title is not None:
            self._schema['title'] = title

        if additional_properties is not None:
            self._schema['additionalProperties'] = additional_properties

    def add_property(self, prop_name, prop_def, required=False):
        """Add a property.

        `prop_def` must be a dictionary with the property definition.
        """
        if 'properties' not in self._schema:
            self._schema['properties'] = OrderedDict()

        self._schema['properties'][prop_name] = prop_def
        if required:
            self.set_required(prop_name)

    def drop_property(self, prop_name):
        """Remove a property.
        """
        if 'properties' not in self._schema:
            return

        self._schema['properties'].pop(prop_name, None)
        if prop_name in self._schema.get('required', []):
            self.set_not_required(prop_name)

        if not self._schema['properties']:
            self._schema.pop('properties')

    def set_required(self, prop_name):
        """Set a property as required.
        """
        if 'required' not in self._schema:
            self._schema['required'] = []

        if prop_name not in self._schema['required']:
            self._schema['required'].append(prop_name)

    def set_not_required(self, prop_name):
        """Set a property as not required.
        """
        if 'required' in self._schema:
            self._schema['required'].remove(prop_name)
            if not self._schema['required']:
                self._schema.pop('required')

    def require_any_of(self, prop_names):
        """Add an 'anyOf' constraint requiring either of the properties.

        The anyOf constraint will be added to a global 'allOf' constraint.
        """
        if 'allOf' not in self._schema:
            self._schema['allOf'] = []

        constraint = {'anyOf': [{'required': [p]} for p in prop_names]}
        self._schema['allOf'].append(constraint)

    def set_field_order(self, field_order):
        """Populate the `field_order` key.
        """
        self._schema['field_order'] = field_order

    def add_definition(self, name, schema):
        """Add another JSONSchema to the #/definitions/ section.

        Since it will be serialized, the other JSONSchema needs to be
        finalized when it's added as a definition.
        """
        assert isinstance(schema, self.__class__)
        if 'definitions' not in self._schema:
            self._schema['definitions'] = OrderedDict()

        subschema = schema.serialize()
        subschema.pop('$schema', None)
        self._schema['definitions'][name] = subschema

    def make_optional_properties_nullable(self):
        """Modify all non-required properties so that they also accept `null`
        as a valid value. Also updates any enums accordingly if necessary.
        """
        for prop_name, prop_def in self._schema.get('properties', {}).items():
            if prop_name not in self._schema.get('required', []):
                existing_type = prop_def.get('type')
                if not existing_type:
                    continue

                # Add null/None as one of the allowed data types
                assert isinstance(existing_type, basestring)
                prop_def['type'] = ['null'] + [existing_type]

                # If the field has a vocabulary, null/None also needs to be
                # part of that vocabulary in order for the schema to validate
                if 'enum' in prop_def:
                    prop_def['enum'].insert(0, None)

    def serialize(self):
        """Serialize the schema to a pure Python data structure.

        After serializing the schema once, it's not possible to mutate
        self._schema any more, since these changes would not be reflected in
        the serialized output.
        """
        # Order keys before serializing.
        # This is to get a stable sort order when dumping schemas, and a
        # convenient API at the same time (no need to pass in OrderedDicts
        # all the time). This keeps calling code more readable.
        self._schema = order_dict(self._schema, SCHEMA_KEYS_ORDER)
        if 'properties' in self._schema:
            for prop_name, prop_def in self._schema['properties'].items():
                self._schema['properties'][prop_name] = order_dict(
                    prop_def, PROPERTY_KEYS_ORDER)

        schema = deepcopy(self._schema)
        Draft4Validator.check_schema(schema)

        # Prevent access to self._schema after serialization in order to avoid
        # gotchas where mutations to self._schema don't take effect any more
        del self._schema

        return schema

    def dump(self, dump_path):
        """Dump serialized schema to a file.
        """
        with open(dump_path, 'w') as dump_file:
            json_dump = pretty_json(self.serialize())
            dump_file.write(json_dump.strip() + '\n')

        log.info('Dumped: %s\n' % dump_path)


def order_dict(dct, key_order=None):
    """Create a new OrderedDict() with keys in order given by `key_order`.

    Keys specified in `key_order` will always be listed first. Other keys
    will be sorted by using default sort order, and placed last.
    """
    ordered_dict = OrderedDict()
    if key_order:
        # Insert specified keys first, in order
        for key in key_order:
            if key not in dct:
                continue
            ordered_dict[key] = dct[key]

    for key in sorted(dct):
        # Insert non-specified keys last, in default sort order
        if key in ordered_dict:
            continue
        ordered_dict[key] = dct[key]

    return ordered_dict
