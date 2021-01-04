from opengever.propertysheets.exceptions import InvalidFieldType
from opengever.propertysheets.exceptions import InvalidFieldTypeDefinition
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.schemaeditor import fields
from plone.schemaeditor.utils import IEditableSchema
from plone.supermodel import loadString
from plone.supermodel import model
from plone.supermodel import serializeSchema
import keyword
import re
import tokenize


def isidentifier(val):
    return re.match(tokenize.Name + r'\Z', val) and not keyword.iskeyword(val)


class PropertySheetSchemaDefinition(object):
    """Wraps a schema definition and handles schema modifications.

    This class represents the schema definition of a property sheet. It allows
    to add fields to an existing schema.
    It also handles serialization and deserialization to a dict-like persistent
    storage.
    """
    FACTORIES = {
        'bool': fields.BoolFactory,
        'choice': fields.ChoiceFactory,
        'int': fields.IntFactory,
        'text': fields.TextFactory,
        'textline': fields.TextLineFactory,
    }

    @classmethod
    def create(cls, name, identifiers=None):

        class SchemaClass(model.Schema):
            pass

        return cls(name, SchemaClass, identifiers=identifiers)

    def __init__(self, name, schema_class, identifiers=None):
        self.name = name
        self.schema_class = schema_class
        if identifiers is None:
            identifiers = tuple()
        else:
            identifiers = tuple(identifiers)
        self.identifiers = identifiers

    def add_field(self, field_type, name, title, description, required, values=None):
        if field_type not in self.FACTORIES:
            raise InvalidFieldType("Field type '{}' is invalid.".format(field_type))

        if not isidentifier(name):
            raise InvalidFieldTypeDefinition(
                "The name '{}' is not a valid identifier.".format(name)
            )

        factory = self.FACTORIES[field_type]
        properties = {
            "title": title,
            "__name__": name,
            "description": description,
            "required": required,
        }

        if field_type == 'choice':
            if not values:
                raise InvalidFieldTypeDefinition(
                    "For 'choice' fields types values are required."
                )
            properties['values'] = values
        elif values:
            raise InvalidFieldTypeDefinition(
                "The argument 'values' is only valid for 'choice' fields."
            )

        field = factory(**properties)
        schema = IEditableSchema(self.schema_class)
        schema.addField(field)

    def _save(self, storage):
        serialized_schema = serializeSchema(self.schema_class, name=self.name)
        definition_data = PersistentMapping()
        definition_data['schema'] = serialized_schema
        definition_data['identifiers'] = PersistentList(self.identifiers)
        storage[self.name] = definition_data

    @classmethod
    def _load(cls, storage, name):
        definition_data = storage[name]
        serialized_schema = definition_data['schema']
        identifiers = definition_data['identifiers']
        model = loadString(serialized_schema, policy=u'propertysheets')
        schema_class = model.schemata[name]

        return cls(name, schema_class, identifiers=identifiers)
