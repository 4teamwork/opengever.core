from copy import deepcopy
from ftw.solr.converters import to_iso8601
from opengever.propertysheets.default_expression import attach_expression_default_factory
from opengever.propertysheets.default_from_member import attach_member_property_default_factory
from opengever.propertysheets.exceptions import InvalidFieldType
from opengever.propertysheets.exceptions import InvalidFieldTypeDefinition
from opengever.propertysheets.helpers import add_current_value_to_allowed_terms
from opengever.propertysheets.helpers import is_choice_field
from opengever.propertysheets.helpers import is_multiple_choice_field
from opengever.propertysheets.interfaces import IDuringPropertySheetFieldDeserialization
from opengever.propertysheets.schema import get_property_sheet_schema
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.schemaeditor import fields
from plone.schemaeditor.utils import IEditableSchema
from plone.supermodel import loadString
from plone.supermodel import model
from plone.supermodel import serializeSchema
from Products.CMFCore.Expression import Expression
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.dottedname.resolve import resolve
from zope.globalrequest import getRequest
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Date
from zope.schema import getFieldNamesInOrder
from zope.schema import getFieldsInOrder
from zope.schema import Int
from zope.schema import Set
from zope.schema import TextLine
from zope.schema import ValidationError
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import WrongType
from zope.schema.vocabulary import SimpleVocabulary
import json
import keyword
import re
import tokenize


def isidentifier(val):
    return re.match(tokenize.Name + r'\Z', val) and not keyword.iskeyword(val)


class SolrDynamicField(object):

    SUPPORTED_TYPES = {
        Bool: 'boolean',
        Choice: 'string',
        Int: 'int',
        TextLine: 'string',
        # We currently only support multiple_choice for string values
        Set: 'strings',
        Date: 'date'
    }
    DYNAMIC_FIELD_IDENT = '_custom_field_'

    @classmethod
    def is_dynamic_field(cls, name):
        return cls.DYNAMIC_FIELD_IDENT in name

    @classmethod
    def supports(cls, field):
        return type(field) in cls.SUPPORTED_TYPES

    def __init__(self, name, field):
        assert self.supports(field)

        solr_type = self.SUPPORTED_TYPES[type(field)]
        self.solr_field_name = '{}{}{}'.format(
            name, self.DYNAMIC_FIELD_IDENT, solr_type
        )
        self.field = field
        self.name = name

    def get_schema(self):
        provider = queryMultiAdapter(
            (self.field, api.portal.get(), getRequest()),
            interface=IJsonSchemaProvider
        )
        schema = provider.get_schema()

        return {
            'title': schema['title'],
            'name': self.solr_field_name,
            'type': schema['type'],
            'widget': schema.get('widget'),
        }

    def convert_value(self, value):
        """Jsonify values but use ftw.solrs own to_iso8601 for date fields
        """
        solr_type = self.SUPPORTED_TYPES[type(self.field)]
        if solr_type == 'date':
            return to_iso8601(value)

        return json_compatible(value)


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
        'date': fields.DateFactory,
        'multiple_choice': fields.MultiChoiceFactory,
        'int': fields.IntFactory,
        'text': fields.TextFactory,
        'textline': fields.TextLineFactory,
    }

    DYNAMIC_DEFAULT_PROPERTIES = (
        'default_factory',
        'default_expression',
        'default_from_member',
    )

    @classmethod
    def create(cls, name, assignments=None, docprops=[]):

        class SchemaClass(model.Schema):
            pass
        SchemaClass.__name__ = name

        return cls(name, SchemaClass, assignments=assignments, docprops=docprops)

    def __init__(self, name, schema_class, assignments=None, docprops=[]):
        self.name = name
        self.schema_class = schema_class
        if assignments is None:
            assignments = tuple()
        self.assignments = assignments
        self.docprops = docprops

        for field in self.get_fields():
            self._init_field(field[1])

    def _init_field(self, field):
        """Make sure field initialization is completed.

        Choice fields are constructed by `ChoiceHandler`, a choice-field
        specific `IFieldExportImportHandler` implementation. It does not seem
        to construct the fields via their constructor and thus never sets
        the `_init_field` instance variable to `False` to signal that
        initialization is complete. This will cause the field to always skip
        validation.

        To work around this issue we set the attribute manually after the
        schema class and its fields have been loaded or a field is added.

        This is fixed with https://github.com/plone/plone.supermodel/pull/12
        and available when we make the move to plone 5.
        """
        if isinstance(field, Choice):
            field._init_field = False
        elif isinstance(field, Set) and isinstance(field.value_type, Choice):
            # For multiple choice fields
            field.value_type._init_field = False

    def __eq__(self, other):
        if isinstance(other, PropertySheetSchemaDefinition):
            return other.name == self.name
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    @property
    def assignments(self):
        return self._assignments

    @assignments.setter
    def assignments(self, values):
        vocabulary_factory = getUtility(
            IVocabularyFactory,
            name="opengever.propertysheets.PropertySheetAssignmentsVocabulary"
        )
        assignment_slots = vocabulary_factory(None)

        assignments = []
        for token in values:
            try:
                term = assignment_slots.getTermByToken(token)
                assignments.append(term.value)
            except LookupError:
                # Missing slots should be ignored without raising an error.
                # This allows custom properties to remain usable even if the corresponding slots no longer exist.
                # Currently, this mainly occurs during testing or local development
                # when switching between Gever and Teamraum.
                continue

        self._assignments = tuple(assignments)

    def add_field(self, field_type, name, title, description, required,
                  values=None, default=None, default_factory=None,
                  default_expression=None, default_from_member=None,
                  available_as_docproperty=False):
        if field_type not in self.FACTORIES:
            raise InvalidFieldType("Field type '{}' is invalid.".format(field_type))

        if not isidentifier(name):
            raise InvalidFieldTypeDefinition(
                "The name '{}' is not a valid identifier.".format(name)
            )

        # Make all default value properties mutually exclusive
        dynamic_defaults = [
            default_factory,
            default_expression,
            default_from_member
        ]
        assert len(dynamic_defaults) == len(self.DYNAMIC_DEFAULT_PROPERTIES)

        all_defaults = [default] + dynamic_defaults
        if len(filter(None, all_defaults)) > 1:
            raise InvalidFieldTypeDefinition(
                "The default value properties ('default', {}) are mutually "
                "exclusive".format(','.join(self.DYNAMIC_DEFAULT_PROPERTIES))
            )

        factory = self.FACTORIES[field_type]
        properties = {
            "title": title,
            "__name__": name,
            "description": description,
            "required": required,
        }

        if field_type in ['choice', 'multiple_choice']:
            if not values:
                raise InvalidFieldTypeDefinition(
                    "For 'choice' or 'multiple_choice' fields types "
                    "values are required."
                )

            if not all(isinstance(choice, basestring) for choice in values):
                raise InvalidFieldTypeDefinition(
                    "For 'choice' or 'multiple_choice' fields types "
                    "values must be string."
                )

            # Using `unicode_escape` encoding for tokens is a requirement of
            # `ChoiceHandler` which otherwise refuses to write the vocabulary
            # to XML.
            terms = [
                SimpleVocabulary.createTerm(
                    item, item.encode("unicode_escape"), item
                )
                for item in values
            ]

            vocabulary = SimpleVocabulary(terms)
            if field_type == 'multiple_choice':
                properties['value_type'] = Choice(
                    values=None, vocabulary=SimpleVocabulary(terms))
            else:
                properties['vocabulary'] = vocabulary
                # The field factory injects an empty list as values argument if it
                # is not set. This will lead to a conflict with the vocabylary we
                # provide here. We prevent this error by actively setting the
                # values argument to None.
                properties['values'] = None

        elif values:
            raise InvalidFieldTypeDefinition(
                "The argument 'values' is only valid for 'choice' fields."
            )

        if default is not None:
            if field_type == 'multiple_choice' and isinstance(default, list):
                # Multiple choice fields strictly require their default to be
                # of type 'set' (which can't be specified in JSON). So if it's
                # list, convert it. Otherwise, it's an invalid default anyway,
                # so we just let zope.schema handle raise WrongType.
                default = set(default)

            properties['default'] = default

        # Resolve a possible defaultFactory dottedname into callable
        if default_factory is not None:
            properties['defaultFactory'] = resolve(default_factory)

        field = factory(**properties)

        if default_expression is not None:
            # Validate default_expression and set it as an attribute on the
            # IField to carry it over to the export/import handler.
            if not isinstance(default_expression, basestring):
                raise InvalidFieldTypeDefinition(
                    "default_expression must be a string")
            try:
                Expression(default_expression)
            except Exception as exc:
                raise InvalidFieldTypeDefinition(
                    "default_expression must be a valid TALES expression. "
                    "Got: %r" % exc)
            field.default_expression = default_expression

            # This is only really needed for cases where the added field
            # is immediately used, like in tests. Usually, the schema goes
            # through a save/load pass and plone.supermodel deserialization
            # takes care of this for us.
            attach_expression_default_factory(field, default_expression)

        if default_from_member is not None:
            # Validate options format and set it as an attribute on the
            # IField to carry it over to the export/import handler.
            if not isinstance(default_from_member, dict):
                raise InvalidFieldTypeDefinition(
                    'default_from_member must be a dictionary')

            property_name = default_from_member.get('property')
            if not property_name:
                raise InvalidFieldTypeDefinition(
                    '"default_from_member" key "property" is required '
                    'for "default_from_member"')

            mapping = default_from_member.get('mapping', {})
            if not isinstance(mapping, dict):
                raise InvalidFieldTypeDefinition(
                    '"default_from_member" key "mapping" must be a dictionary '
                    'with strings for both keys and values')

            # For ease of serialization we store the default_from_member
            # options as a JSON encoded string.
            default_from_member = json.dumps(default_from_member)

            field.default_from_member = default_from_member

            # This is only really needed for cases where the added field
            # is immediately used, like in tests. Usually, the schema goes
            # through a save/load pass and plone.supermodel deserialization
            # takes care of this for us.
            attach_member_property_default_factory(field, default_from_member)

        schema = IEditableSchema(self.schema_class)
        schema.addField(field)
        self._init_field(field)

    def get_fields(self):
        """Return a list of (name, field) tuples in native schema order."""
        return getFieldsInOrder(self.schema_class)

    def get_solr_dynamic_fields(self):
        """Return all solr dynamic fields for this definition's schema."""
        return [
            SolrDynamicField(name, field) for name, field in self.get_fields()
            if SolrDynamicField.supports(field)
        ]

    def get_fieldnames(self):
        """Return a list of fieldnames in native schema order."""
        return getFieldNamesInOrder(self.schema_class)

    def get_json_schema(self):
        schema_info = get_property_sheet_schema(self.schema_class)
        schema_info["assignments"] = IJsonCompatible(self.assignments)
        return schema_info

    def get_solr_dynamic_field_schema(self):
        solr_schema = {}
        for solr_field in self.get_solr_dynamic_fields():
            solr_schema[solr_field.solr_field_name] = solr_field.get_schema()
        return solr_schema

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

        for name, field in self.get_fields():
            value = data_to_validate.pop(name, None)
            if is_choice_field(field) or is_multiple_choice_field(field):
                request = getRequest()
                if IDuringPropertySheetFieldDeserialization.providedBy(request):
                    add_current_value_to_allowed_terms(field, request.context)

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
        definition_data['docprops'] = PersistentList(self.docprops)
        storage[self.name] = definition_data

    @classmethod
    def _load(cls, storage, name):
        definition_data = storage[name]
        serialized_schema = definition_data['schema']
        assignments = definition_data['assignments']
        docprops = definition_data.get('docprops', [])
        model = loadString(serialized_schema, policy=u'propertysheets')
        schema_class = model.schemata[name]

        return cls(name, schema_class, assignments=assignments, docprops=docprops)
