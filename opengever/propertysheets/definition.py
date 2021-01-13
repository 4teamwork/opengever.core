from copy import deepcopy
from opengever.base.filename import filenamenormalizer
from opengever.propertysheets.exceptions import InvalidFieldType
from opengever.propertysheets.exceptions import InvalidFieldTypeDefinition
from opengever.propertysheets.exceptions import InvalidSchemaAssignment
from opengever.propertysheets.schema import get_property_sheet_schema
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.restapi.serializer.converters import IJsonCompatible
from plone.schemaeditor import fields
from plone.schemaeditor.utils import IEditableSchema
from plone.supermodel import loadString
from plone.supermodel import model
from plone.supermodel import serializeSchema
from zope.component import getUtility
from zope.schema import getFieldsInOrder
from zope.schema import ValidationError
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import WrongType
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
        self.assignments = assignments

    @property
    def assignments(self):
        return self._assignments

    @assignments.setter
    def assignments(self, values):
        vocabulary_factory = getUtility(
            IVocabularyFactory,
            name="opengever.propertysheets.PropertySheetAssignmentsVocabulary"
        )
        vocabulary = vocabulary_factory(None)

        assignments = []
        for token in values:
            try:
                term = vocabulary.getTermByToken(token)
                assignments.append(term.value)
            except LookupError:
                raise InvalidSchemaAssignment(
                    "The assignment '{}' is invalid.".format(token)
                )

        self._assignments = tuple(assignments)

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

    def validate(self, data):
        """Validate data against the definition's schema.

        The parameter data is expected to be a dict containing field name and
        field value as items. Validation of field values is delegated to
        the corresponding fields.
        Partial data for non-required fields is allowed. No remainders are
        allowed, each item in data must correspond to a field.

        """
        if data is None:
            data_to_validate = {}
        else:
            if not isinstance(data, dict):
                raise WrongType("Only 'dict' is allowed for properties.")
            data_to_validate = deepcopy(data)

        for name, field in getFieldsInOrder(self.schema_class):
            value = data_to_validate.pop(name, None)
            field.validate(value)

        # prevent setting arbitrary properties, don't allow remainders
        if data_to_validate:
            raise ValidationError("Cannot set properties '{}'.".format(
                "', '".join(data_to_validate.keys()))
            )

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
