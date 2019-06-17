from collections import OrderedDict
from collective.elephantvocabulary.interfaces import IElephantVocabulary
from collective.vdexvocabulary.vocabulary import VdexVocabulary
from opengever.base.schemadump.config import DEFAULT_OVERRIDES
from opengever.base.schemadump.config import PYTHON_TO_JS_TYPES
from opengever.base.schemadump.config import VOCAB_OVERRIDES
from opengever.base.schemadump.helpers import translate_de
from plone.autoform.interfaces import MODES_KEY
from plone.autoform.interfaces import OMITTED_KEY
from pprint import pprint
from sqlalchemy.sql.schema import ColumnDefault
from sqlalchemy.sql.schema import Sequence
from z3c.form.interfaces import IValue
from zope.component import ComponentLookupError
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.schema import Choice
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
import json
import logging


log = logging.getLogger(__name__)


NO_DEFAULT_MARKER = object()

STRING_TYPES = ('Text', 'TextLine', 'ASCII', 'ASCIILine')


class FieldDumper(object):
    """Dumps a simple Python representation of a zope.schema Field.
    """

    def __init__(self, schema):
        self.schema = schema

    def dump(self, field):
        log.info("    Dumping field %r" % field.getName())

        field_title = translate_de(field.title)
        field_desc = translate_de(field.description)
        field_type = field.__class__.__name__

        field_dump = OrderedDict((
            ('name', field.getName()),
            ('type', field_type),
            ('title', field_title),
            ('description', field_desc),
            ('required', field.required),
        ))

        if field_dump['type'] in STRING_TYPES:
            field_dump['max_length'] = field.max_length

        # Determine the field's default value
        log.debug("      Determining default...")
        default_value = self._get_default(field)
        if default_value is not NO_DEFAULT_MARKER:
            field_dump['default'] = default_value
            # Also remove a potential `required` flag from the field if there
            # is a default. The field may be tagged as being required on a
            # zope.schema level, but functionally it's not actually required
            # if a default value is defined.
            field_dump['required'] = False

        # Determine vocabulary, if applicable
        log.debug("      Determining vocabulary...")
        field_vocab = self._get_vocabulary(field)
        if field_vocab:
            field_dump['vocabulary'] = field_vocab

        # Field omitted?
        omitted = self._get_omitted_for_field(field)
        if omitted:
            field_dump['omitted'] = omitted

        # Field modes
        modes_for_field = self._get_modes_for_field(field)
        if modes_for_field:
            field_dump['modes'] = modes_for_field

        if isinstance(field, Choice):
            # Include the value type of the field by looking at the
            # terms in the vocabulary
            vocab_type = type(field_vocab[0])
            assert all(isinstance(item, vocab_type) for item in field_vocab)
            value_type = PYTHON_TO_JS_TYPES[vocab_type]
            field_dump['value_type'] = value_type

        try:
            json.dumps(field_dump)
        except TypeError:
            msg = "Failed to convert dump for field {!r} to JSON!"
            log.error(msg.format(field.getName()))
            pprint(field_dump)
            raise

        return field_dump

    def _get_vocab_override(self, field):
        return self._get_override(field, VOCAB_OVERRIDES)

    def _get_default_override(self, field):
        return self._get_override(field, DEFAULT_OVERRIDES, NO_DEFAULT_MARKER)

    def _get_override(self, field, mapping, sentinel=None):
        return mapping.get(
            self.schema.__identifier__, {}).get(field.getName(), sentinel)

    def _get_vocabulary(self, field):
        """Try to determine the vocabulary for a field, if possible.

        Loosely based on z3c.form.widget.Widget.update().
        """
        # XXX: Refactor this method

        field_vocab = None
        vf = None
        if isinstance(field, Choice):
            # First check whether an override is defined in the configuration
            # for vocabularies we can't (or don't want to) serialize
            override = self._get_vocab_override(field)
            if override is not None:
                return override

            elif field.vocabulary:
                if IVocabularyFactory.providedBy(field.vocabulary):
                    vocabulary = field.vocabulary(None)
                elif IContextSourceBinder.providedBy(field.vocabulary):
                    vocabulary = field.vocabulary(None)
                else:
                    vocabulary = field.vocabulary

            elif field.vocabularyName:
                try:
                    vf = getUtility(
                        IVocabularyFactory, name=field.vocabularyName)
                except ComponentLookupError:
                    pass

                vocabulary = vf(None)

            # Determine whether term order is significant or not
            order_significant = True
            wrapped_vocab = vocabulary
            if IElephantVocabulary.providedBy(vocabulary):
                # VDEX vocaby might be potentially wrapped by Elephant vocabs.
                # In that case, we need to inspect the wrapped vocab to
                # determine whether order is significant or not
                wrapped_vocab = queryUtility(
                    IVocabularyFactory, name=field.vocabulary.vocab)

            if isinstance(wrapped_vocab, VdexVocabulary):
                order_significant = wrapped_vocab.vdex.isOrderSignificant()

            # XXX: The getTaskTypeVocabulary() factory destroys the reference
            # to the underlying VDEX vocabulary by incorrectly wrapping it.
            # Therefore the detection for order significance doesn't work.
            if field.vocabulary and getattr(field.vocabulary, '__name__', '') == 'getTaskTypeVocabulary':  # noqa
                order_significant = False

            # Build list of terms
            if vocabulary is not None:
                terms = [t.value for t in vocabulary._terms]

                if not order_significant:
                    # For VDEX vocabularies with orderSignificant="false" we
                    # explicitly sort terms to get a stable sort order
                    terms = sorted(terms)

                field_vocab = terms
        return field_vocab

    def _get_default(self, field):
        """Try to determine the default value for a field, if possible.

        Loosely based on z3c.form.widget.Widget.update().
        """
        # First check whether an override is defined in the configuration
        # for default values we can't (or don't want to) determine
        override = self._get_default_override(field)
        if override is not NO_DEFAULT_MARKER:
            return override

        # See if we can find an IValue adapter named 'default' for this
        # field that doesn't require context, request, form, or widget
        adapter = queryMultiAdapter(
            (None, None, None, field, None), IValue, name='default')

        if adapter:
            value = adapter.get()
        else:
            # Otherwise see if the field has a schema level default
            value = field.default

        if value is not field.missing_value:
            return value
        return NO_DEFAULT_MARKER

    def _get_modes_for_field(self, field):
        """Get and serialize the modes for this field, as defined by tagged
        values on the field's schema.

        A field can have different modes for different forms, thefore this
        returns a mapping of interface (IEditForm, IAddForm, ...) to mode
        for this field.

        """
        modes_for_field = {}

        for field_mode in self.schema.queryTaggedValue(MODES_KEY, []):
            iface, field_name, mode_name = field_mode
            if field_name == field.getName():
                modes_for_field[iface.__identifier__] = mode_name
        return modes_for_field

    def _get_omitted_for_field(self, field):
        """Get and serialize the ommited states for this field, as defined by
        tagged values on the field's schema.

        A field can be omitted for different forms, thefore this
        returns a mapping of interface (IEditForm, IAddForm, ...) to omitted
        state for this field.
        """
        omitted_for_field = {}

        for field_omitted in self.schema.queryTaggedValue(OMITTED_KEY, []):
            iface, field_name, omitted_value = field_omitted
            omitted = True if omitted_value.lower() == 'true' else False
            if field_name == field.getName():
                omitted_for_field[iface.__identifier__] = omitted
        return omitted_for_field


class SQLFieldDumper(object):
    """Dumps a simple Python representation of a SQLAlchemy Column.
    """

    # Mapping from SQLAlchemy column types to zope.schema field types
    SQL_FIELD_TYPES = {
        'Integer': 'Int',
        'String': 'Text',
        'UnicodeCoercingText': 'Text',
        'Boolean': 'Bool',
    }

    def __init__(self, klass):
        self.schema = klass

    def dump(self, column):
        log.info("    Dumping SQL field %r" % column.name)

        field_dump = OrderedDict((
            ('name', column.name),
            ('type', self._map_field_type(column)),
            ('title', column.name),
            ('description', ''),
            ('required', not column.nullable),
        ))

        if field_dump['type'] in STRING_TYPES:
            field_dump['max_length'] = column.type.length

        # Determine the column's default value
        log.debug("      Determining default...")
        default_value = column.default
        if default_value is None:
            default_value = NO_DEFAULT_MARKER

        if isinstance(default_value, ColumnDefault):
            default_value = default_value.arg

        if isinstance(default_value, Sequence):
            default_value = 'Sequence(%s)' % default_value.name

        if default_value is not NO_DEFAULT_MARKER:
            field_dump['default'] = default_value

        # TODO: Determine vocabulary, if applicable?
        # We currently don't use any SQL ENUMS though.

        try:
            json.dumps(field_dump)
        except TypeError:
            msg = "Failed to convert dump for field {!r} to JSON!"
            log.error(msg.format(column.name))
            pprint(field_dump)
            raise

        return field_dump

    def _map_field_type(self, column):
        col_type = column.type.__class__.__name__
        if col_type not in self.SQL_FIELD_TYPES:
            raise Exception('Unmapped SQL column type %r!' % col_type)
        return self.SQL_FIELD_TYPES[col_type]
