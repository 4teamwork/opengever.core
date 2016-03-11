from collections import OrderedDict
from opengever.base.schemadump.config import DEFAULT_OVERRIDES
from opengever.base.schemadump.config import VOCAB_OVERRIDES
from opengever.base.schemadump.helpers import translate_de
from opengever.base.schemadump.log import setup_logging
from plone.autoform.interfaces import MODES_KEY
from plone.autoform.interfaces import OMITTED_KEY
from pprint import pprint
from z3c.form.interfaces import IValue
from zope.component import ComponentLookupError
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.schema import Choice
from zope.schema.interfaces import IVocabularyFactory
import json


log = setup_logging(__name__)


NO_DEFAULT_MARKER = object()


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
            ('desc', field_desc),
            ('required', field.required),
        ))

        # Determine the field's default value
        log.debug("      Determining default...")
        default_value = self._get_default(field)
        if default_value is not NO_DEFAULT_MARKER:
            field_dump['default'] = default_value

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
                    vf = field.vocabulary
            elif field.vocabularyName:
                try:
                    vf = getUtility(
                        IVocabularyFactory, name=field.vocabularyName)
                except ComponentLookupError:
                    pass

            if vf is not None:
                # Ignore context dependent vocabularies
                vocabulary = vf(None)
                terms = [t.value for t in vocabulary._terms]
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
