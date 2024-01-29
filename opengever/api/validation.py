from inspect import isclass
from opengever.api.exceptions import InvalidBase64DataURI
from opengever.api.exceptions import UnknownField
from urlparse import urlparse
from zope.interface.exceptions import Invalid
from zope.schema import Choice
from zope.schema import getFieldNamesInOrder
from zope.schema import getFieldsInOrder
from zope.schema import List
from zope.schema import URI
from zope.schema import ValidationError
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import RequiredMissing
import binascii
import dateutil


class SchemaValidationData(dict):

    def __getattr__(self, name):
        return self.get(name)


class Base64DataURI(URI):
    """Field type for a Base64 encoded data URI.
    """

    def _validate(self, value):
        super(Base64DataURI, self)._validate(value)
        if not value.startswith('data:'):
            raise InvalidBase64DataURI(value)

        contents = urlparse(value).path.strip()
        params, payload = contents.strip().split(',', 1)

        # This validation is not perfect. Actual parsing of data URI parameters
        # would be much more complicated than this.
        if 'base64' not in params.lower():
            raise InvalidBase64DataURI("Data URI does not seem to declare base64 encoding.")

        params = params.split(';')
        if not len(params) > 1:
            raise InvalidBase64DataURI("Data URI does not seem to declare a mimetype.")

        try:
            payload.decode('base64')
        except binascii.Error as exc:
            raise InvalidBase64DataURI("Data URI could not be decoded as base64 (%r)." % exc)


def get_unknown_fields(action_data, schema):
    """Return an error list of unknown fields that are not part of the schema.
    """
    errors = []
    known_field_names = getFieldNamesInOrder(schema)
    for key in action_data:
        if key not in known_field_names:
            errors.append((key, UnknownField(key)))
    return errors


def get_schema_validation_errors(action_data, schema, allow_unknown_fields=False):
    """Validate a dict against a schema.

    Return a list of basic schema validation errors (required fields,
    constraints, but doesn't check invariants yet).

    Loosely based on zope.schema.getSchemaValidationErrors, but:

    - Processes fields in schema order
    - Handles dict subscription access instead of object attribute access
    - Respects required / optional fields
    - Raises RequiredMissing instead of SchemaNotFullyImplemented
    """
    errors = []
    for name, field in getFieldsInOrder(schema):
        try:
            value = action_data[name]
        except KeyError:
            # property for the given name is not implemented
            if not field.required:
                continue
            errors.append((name, RequiredMissing(name)))
        else:
            try:
                bound = field.bind(action_data)
                bound.validate(value)
            except ValidationError as e:
                # For datetime strings can't be parsed by dateutil because of
                # an invalid format, just a generic WrongType will be raised.
                errors.append((name, e))

    if not allow_unknown_fields:
        # Also reject fields that are not part of the schema
        errors.extend(get_unknown_fields(action_data, schema))

    return errors


def get_validation_errors(action_data, schema, allow_unknown_fields=False):
    """Validate a dict against a schema and invariants.

    Return a list of all validation errors, including invariants.
    Based on zope.schema.getValidationErrors.
    """
    errors = get_schema_validation_errors(action_data, schema,
                                          allow_unknown_fields)
    if errors:
        return errors

    # Only validate invariants if there were no previous errors. Previous
    # errors could be missing attributes which would most likely make an
    # invariant raise an AttributeError.
    invariant_errors = []
    try:
        schema.validateInvariants(SchemaValidationData(action_data), invariant_errors)
    except Invalid:
        # Just collect errors
        pass
    errors = [(None, e) for e in invariant_errors]
    return errors


def validate_schema(action_data, schema):
    """Validate a dict against a schema, raise on error.
    """
    errors = get_validation_errors(action_data, schema)
    if errors:
        raise ValidationError(
            "WebAction doesn't conform to schema (First error: %s)." % str(errors[0]))


def validate_no_unknown_fields(action_data, schema):
    """Validate that data only contains known fields.

    No other validations are performed though. This is needed in situations
    where only have partial webaction data, like on PATCH / update(), and
    therefore can't expect invariant validations to succeed.
    """
    errors = get_unknown_fields(action_data, schema)
    if errors:
        raise ValidationError(
            "WebAction doesn't conform to schema (First error: %s)." % str(errors[0]))


def scrub_json_payload(jsondata, schema):
    """Casts some of the unicode strings in JSON payloads to bytestrings
    or datetimes.

    Strings in dicts deserialized from JSON are always unicode. But because
    some of the fields as defined in the zope schema are actually ASCII
    based types (URIs, identifiers that should never contain non-ASCII, etc.)
    we cast them to bytestrings here before even attempting validation.

    In some cases (top-level ASCII fields) validation would fail outright if
    we didn't do this, but in more subtle cases (e.g. Choice fields with
    vocabs that contain ASCII values) this would go unnoticed, and we could
    end up with a mix of bytestrings vs. unicode for the same field in our
    storage, depending on how exactly they were set.

    For datetimes, JSON has no native datetime type, and those strings
    therefore need to be parsed to Python datetimes first.
    """
    def safe_utf8(s):
        if isinstance(s, unicode):
            s = s.encode('utf8')
        return s

    def is_datetime_like(pytype):
        if not isclass(pytype):
            return False
        return pytype.__name__ in ('datetime', 'FrozenDatetime')

    for key, value in jsondata.items():
        if key in schema:
            field = schema[key]

            # If field is a Choice field, also accept {"token": "..."}
            # style object's to make API consumers' life easier.
            if isinstance(field, Choice) and isinstance(value, dict):
                if 'token' in value:
                    value = jsondata[key] = value['token']

            # Field may be a datetime
            pytype = getattr(field, '_type', None)
            if is_datetime_like(pytype) and isinstance(value, unicode):
                try:
                    jsondata[key] = dateutil.parser.parse(value)
                except ValueError:
                    # Don't raise validation errors yet, that's the
                    # responsibility of get_schema_validation_errors()
                    pass
                continue

            # Field itself may be of a bytestring type
            pytype = getattr(field, '_type', None)
            if pytype is str and isinstance(value, unicode):
                jsondata[key] = value.encode('utf-8')
                continue

            # Fields vocabulary terms may be of a bytestring type
            if isinstance(field, Choice):
                if IVocabularyFactory.providedBy(field.vocabulary):
                    vocabulary = field.vocabulary(None)
                elif IContextSourceBinder.providedBy(field.vocabulary):
                    vocabulary = field.vocabulary(None)
                else:
                    vocabulary = field.vocabulary

                if vocabulary:
                    terms = [t.value for t in vocabulary]

                    if terms and isinstance(terms[0], str) and isinstance(value, unicode):
                        jsondata[key] = value.encode('utf-8')
                        continue

            # Field's value_type may indicate bytestring type
            if isinstance(field, List):
                pytype = getattr(field.value_type, '_type', None)
                if pytype is str and isinstance(value, list):
                    jsondata[key] = [safe_utf8(s) for s in value]
                    continue
