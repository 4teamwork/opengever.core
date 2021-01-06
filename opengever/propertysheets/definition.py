from opengever.base.filename import filenamenormalizer
from opengever.propertysheets.exceptions import InvalidFieldType
from opengever.propertysheets.exceptions import InvalidFieldTypeDefinition
from opengever.propertysheets.schema import get_property_sheet_schema
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.restapi.serializer.converters import IJsonCompatible
from plone.schemaeditor import fields
from plone.schemaeditor.utils import IEditableSchema
from plone.supermodel import loadString
from plone.supermodel import model
from plone.supermodel import serializeSchema
from zope.schema.vocabulary import SimpleVocabulary
import keyword
import re
import tokenize


def isidentifier(val):
    return re.match(tokenize.Name + r'\Z', val) and not keyword.iskeyword(val)


def ascii_token(text):
    return filenamenormalizer.normalize(text)


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
    def create(cls, name, assignments=None):

        class SchemaClass(model.Schema):
            pass
        SchemaClass.__name__ = name

        return cls(name, SchemaClass, assignments=assignments)

    def __init__(self, name, schema_class, assignments=None):
        self.name = name
        self.schema_class = schema_class
        if assignments is None:
            assignments = tuple()
        else:
            assignments = tuple(assignments)
        self.assignments = assignments

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
            terms = [SimpleVocabulary.createTerm(item, ascii_token(item), item)
                     for item in values]
            properties['vocabulary'] = SimpleVocabulary(terms)
            # The field factory injects an empty list as values argument if it
            # is not set. This will lead to a conflict with the vocabylary we
            # provide here. We prevent this error by actively setting the
            # values argument to None.
            properties['values'] = None
        elif values:
            raise InvalidFieldTypeDefinition(
                "The argument 'values' is only valid for 'choice' fields."
            )

        field = factory(**properties)
        schema = IEditableSchema(self.schema_class)
        schema.addField(field)

    def get_json_schema(self):
        schema_info = get_property_sheet_schema(self.schema_class)
        schema_info["assignments"] = IJsonCompatible(self.assignments)
        return schema_info

    def _save(self, storage):
        serialized_schema = serializeSchema(self.schema_class, name=self.name)
        definition_data = PersistentMapping()
        definition_data['schema'] = serialized_schema
        definition_data['assignments'] = PersistentList(self.assignments)
        storage[self.name] = definition_data

    @classmethod
    def _load(cls, storage, name):
        definition_data = storage[name]
        serialized_schema = definition_data['schema']
        assignments = definition_data['assignments']
        model = loadString(serialized_schema, policy=u'propertysheets')
        schema_class = model.schemata[name]

        return cls(name, schema_class, assignments=assignments)
