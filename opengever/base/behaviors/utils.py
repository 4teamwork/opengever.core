from opengever.base.acquisition import acquire_field_value
from opengever.base.acquisition import NO_VALUE_FOUND
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.namedfile.utils import get_contenttype
from Products.CMFPlone.utils import safe_callable
from urllib import quote
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IValue
from z3c.form.value import ComputedValue
from zope.component import getMultiAdapter
import re
import zope.schema.vocabulary


def create_simple_vocabulary(choices, message_factory):

    class GenericSimpleVocabulary(object):

        choices = None
        message_factory = None

        def __call__(self, context):
            terms = []
            for item in self.choices:
                title = item
                if self.message_factory:
                    title = self.message_factory(item)
                terms.append(
                    zope.schema.vocabulary.SimpleTerm(item, title=title))
            return zope.schema.vocabulary.SimpleVocabulary(terms)

    GenericSimpleVocabulary.choices = choices
    GenericSimpleVocabulary.message_factory = message_factory
    return GenericSimpleVocabulary


class RestrictedVocabularyFactory(object):
    """Factory for a restricted vocabulary.

    Expects a `choices` list which looks as follows:
    choices = (
    (0,     u'none'),
    (1,     u'raw_choice_one'),
    (1,     u'raw_choice_two'),
    (2,     u'detailed_choice_one'),
    (2,     u'detailed_choice_two'),
    )

    Use the string as internationalization message-id.

    Alternatively, `choices` can be a callable that produces such a list.

    What it does in the example:
    if the parent object has a "raw" choice set, then only detailed
    choices or the selected raw choice are allowed to be selected.

    `restricted` can be a boolean or a callable (with no arguments) that
    returns a boolean, indicating whether the vocabulary should be restricted
    or not.
    """

    def __init__(self, field, choices, message_factory, restricted=True):
        self.field = field
        self._choices = choices
        self.message_factory = message_factory
        self._restricted = restricted

    @property
    def restricted(self):
        if safe_callable(self._restricted):
            return self._restricted()
        return self._restricted

    @property
    def choice_level_mapping(self):
        choice_level_mapping = [list(a) for a in self.choices[:]]
        choice_level_mapping = dict([a for a in choice_level_mapping
                                     if not a.reverse()])
        return choice_level_mapping

    @property
    def choice_names(self):
        return [a[1] for a in self.choices]

    @property
    def choices(self):
        if safe_callable(self._choices):
            return self._choices()
        return self._choices

    def __call__(self, context):
        self.context = context

        terms = []
        for name in self.get_allowed_choice_names():
            title = name
            if self.message_factory:
                title = self.message_factory(name)
            terms.append(
                zope.schema.vocabulary.SimpleTerm(name, title=title))
        return zope.schema.vocabulary.SimpleVocabulary(terms)

    def get_allowed_choice_names(self):
        acquisition_value = self._get_acquisiton_value()

        if not self.restricted:
            return self.choice_names

        if not acquisition_value or acquisition_value not in self.choice_names:
            return self.choice_names

        allowed_choice_names = []
        allowed_choice_names.append(acquisition_value)
        allowed_level = self.choice_level_mapping[acquisition_value] + 1
        for level, name in self.choices:
            if level >= allowed_level:
                allowed_choice_names.append(name)

        return allowed_choice_names

    def _get_acquisiton_value(self):
        context = self.context
        if isinstance(context, MetadataBase) or context is None:
            # we do not test the factory, it is not acquisition wrapped and
            # we cant get the request...
            return None
        request = self.context.REQUEST
        # XXX CHANGED FROM PATH_TRANSLATED TO PATH_INFO
        # because the test don't work
        if '++add++' in request.get('PATH_INFO', ''):
            # object is not yet existing, context is container
            container = context
        else:
            # object is existing, container is parent of context
            container = context.aq_inner.aq_parent

        acquired_value = acquire_field_value(self.field, container)

        # Use acquired value if one was found
        if acquired_value is not NO_VALUE_FOUND:
            return acquired_value

        # Otherwise use the field default
        return self.field.default


def set_default_with_acquisition(field, default=None):
    """
    Sets a default value generator which uses the value
    from the parent object, if existing, otherwise it uses
    the given default value.
    """
    field._acquisition_default = default

    def default_value_generator(data):
        container = data.context

        acquired_value = acquire_field_value(data.field, container)
        if acquired_value is not NO_VALUE_FOUND:
            return acquired_value

        # otherwise use default value
        if field._acquisition_default:
            # XXX: Use sentinel value (Issue #2029)
            return field._acquisition_default
        else:
            # use first value
            try:
                return tuple(data.widget.terms)[0].value
            except AttributeError:
                return None

    return default_value_generator


def overrides_child(folder, event, aq_fields, marker):
    interface = aq_fields[0].interface
    check_fields = []
    change_fields = []

    # set changed fields
    for life_event in event.descriptions:
        for attr in life_event.attributes:
            change_fields.append(attr)

    # set check_fields
    for field in aq_fields:
        field_name = interface.__name__ + '.' + field.__name__
        if field_name in change_fields:
            check_fields.append(field.__name__)

    if check_fields != []:
        children = folder.portal_catalog(
            path={'depth': 2,
                  'query': '/'.join(folder.getPhysicalPath())},
            object_provides=(marker.__identifier__,)
        )

        for child in children:
            obj = child.getObject()
            for field in check_fields:
                schema_field = interface.get(field)
                voc = schema_field.bind(obj).source
                if schema_field.get(schema_field.interface(obj)) not in voc:
                    # obj, request, form, field, widget
                    default = getMultiAdapter((
                        obj.aq_inner.aq_parent,
                        obj.REQUEST,
                        None,
                        schema_field,
                        None,
                    ), IValue, name='default')
                    if isinstance(default, ComputedValue):
                        default = default.get()
                    setattr(schema_field.interface(obj), field, default)


# Used as sortkey for sorting strings in numerical order
# TODO: Move to a more suitable place
def split_string_by_numbers(x):
    x = str(x)
    r = re.compile('(\d+)')
    l = r.split(x)
    return [int(y) if y.isdigit() else y for y in l]


def set_attachment_content_disposition(request, filename, file=None):
    """ Set the content disposition on the request for the given browser
    """
    if not filename:
        return

    if file:
        contenttype = get_contenttype(file)
        request.response.setHeader("Content-Type", contenttype)
        request.response.setHeader("Content-Length", file.getSize())

    user_agent = request.get('HTTP_USER_AGENT', '')
    if 'MSIE' in user_agent:
        filename = quote(filename)
        request.response.setHeader(
            "Content-disposition", 'attachment; filename=%s' % filename)

    else:
        request.response.setHeader(
            "Content-disposition", 'attachment; filename="%s"' % filename)


def hide_fields_from_behavior(form, fieldnames):
    """Hide fields defined in behaviors.
    """
    for group in form.groups:
        for fieldname in fieldnames:
            if fieldname in group.fields:
                group.fields[fieldname].mode = HIDDEN_MODE
