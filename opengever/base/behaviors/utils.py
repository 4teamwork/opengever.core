from opengever.base.acquisition import acquire_field_value
from opengever.base.acquisition import NO_VALUE_FOUND
from opengever.base.interfaces import IDuringContentCreation
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
        acquired_value = self._acquire_value()

        if not self.restricted:
            return self.choice_names

        if not acquired_value or acquired_value not in self.choice_names:
            # XXX: Compare against sentinel value (Issue #2030)
            return self.choice_names

        allowed_choice_names = []
        allowed_choice_names.append(acquired_value)
        allowed_level = self.choice_level_mapping[acquired_value] + 1
        for level, name in self.choices:
            if level >= allowed_level:
                allowed_choice_names.append(name)

        return allowed_choice_names

    def _acquire_value(self):
        context = self.context
        if isinstance(context, MetadataBase) or context is None:
            # we do not test the factory, it is not acquisition wrapped and
            # we cant get the request...
            return None

        request = self.context.REQUEST
        if IDuringContentCreation.providedBy(request):
            # object does not yet exist, context is container (add)
            container = context
        else:
            # object already exists, container is parent of context (edit)
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

    def default_value_generator(data):
        container = data.context

        acquired_value = acquire_field_value(field, container)
        if acquired_value is not NO_VALUE_FOUND:
            return acquired_value

        # otherwise use default value
        if default:
            # XXX: Use sentinel value (Issue #2029)
            return default
        else:
            # use first value
            try:
                return tuple(data.widget.terms)[0].value
            except AttributeError:
                return None

    return default_value_generator


def propagate_vocab_restrictions(container, event, restricted_fields, marker):

    def dottedname(field):
        return '.'.join((field.interface.__name__, field.__name__))

    changed_fields = []
    for desc in event.descriptions:
        for name in desc.attributes:
            changed_fields.append(name)

    fields_to_check = []
    for field in restricted_fields:
        if dottedname(field) in changed_fields:
            fields_to_check.append(field)

    if not fields_to_check:
        return

    children = container.portal_catalog(
        # XXX: Depth should not be limited (Issue #2027)
        path={'depth': 2,
              'query': '/'.join(container.getPhysicalPath())},
        object_provides=(marker.__identifier__,)
    )

    for child in children:
        obj = child.getObject()
        for field in fields_to_check:
            voc = field.bind(obj).source
            value = field.get(field.interface(obj))
            if value not in voc:
                # obj, request, form, field, widget
                default = getMultiAdapter((
                    obj.aq_inner.aq_parent,
                    obj.REQUEST,
                    None,
                    field,
                    None,
                ), IValue, name='default')
                if isinstance(default, ComputedValue):
                    default = default.get()
                field.set(field.interface(obj), default)


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
