from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.namedfile.utils import get_contenttype
from Products.CMFCore.interfaces import ISiteRoot
from urllib import quote
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IValue
from z3c.form.value import ComputedValue
from zope.component import getMultiAdapter
import re
import zope.schema.vocabulary


def create_simple_vocabulary(options, message_factory):

    class GenericSimpleVocabulary(object):

        options = None
        message_factory = None

        def __call__(self, context):
            terms = []
            for item in self.options:
                title = item
                if self.message_factory:
                    title = self.message_factory(item)
                terms.append(
                    zope.schema.vocabulary.SimpleTerm(item, title=title))
            return zope.schema.vocabulary.SimpleVocabulary(terms)

    GenericSimpleVocabulary.options = options
    GenericSimpleVocabulary.message_factory = message_factory
    return GenericSimpleVocabulary


def create_restricted_vocabulary(field, options,
                                 message_factory=None,
                                 restricted=lambda x: True):
    """
    Creates a restricted vocabulary.
    Expects a options list which looks as follows:
    options = (
    (0,     u'none'),
    (1,     u'raw_option_one'),
    (1,     u'raw_option_two'),
    (2,     u'detailed_option_one'),
    (2,     u'detailed_option_two'),
    )

    Use the string as internationalization message-id.

    What it does in the example:
    if the parent object has a "raw" option set, then only detailed
    options or the selected raw option are allowed to be selected.
    """
    class GeneratedVocabulary(object):

        @property
        def option_level_mapping(self):
            option_level_mapping = [list(a) for a in self.options[:]]
            option_level_mapping = dict([a for a in option_level_mapping
                                         if not a.reverse()])
            return option_level_mapping

        @property
        def option_names(self):
            return [a[1] for a in self.options]

        @property
        def options(self):
            if callable(self._options):
                return self._options()
            else:
                return self._options

        def __call__(self, context):
            self.context = context

            terms = []
            for name in self.get_allowed_option_names():
                title = name
                if message_factory:
                    title = self._(name)
                terms.append(
                    zope.schema.vocabulary.SimpleTerm(name, title=title))
            return zope.schema.vocabulary.SimpleVocabulary(terms)

        def get_allowed_option_names(self):
            acquisition_value = self._get_acquisiton_value()

            if not self.restricted():
                return self.option_names

            if not acquisition_value or acquisition_value not in self.option_names:
                return self.option_names

            allowed_option_names = []
            allowed_option_names.append(acquisition_value)
            allowed_level = self.option_level_mapping[acquisition_value] + 1
            for level, name in self.options:
                if level >= allowed_level:
                    allowed_option_names.append(name)

            return allowed_option_names

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
                obj = context
            else:
                # object is existing, container is parent of context
                obj = context.aq_inner.aq_parent
            while not ISiteRoot.providedBy(obj):
                try:
                    interface_ = self.field.interface
                except AttributeError:
                    pass
                else:
                    try:
                        adpt = interface_(obj)
                    except TypeError:
                        # could not adapt
                        try:
                            return self.field.get(obj)
                        except AttributeError:
                            pass
                    else:
                        return self.field.get(adpt)

                obj = obj.aq_inner.aq_parent
            return self.field.default

    GeneratedVocabulary.field = field
    GeneratedVocabulary._options = options
    GeneratedVocabulary._ = message_factory
    GeneratedVocabulary.restricted = restricted

    return GeneratedVocabulary


# XXX: Eventually this should be rewritten to be compatible with the use of
# context aware default factories.
# The combination of acquired default values with restricted vocabularies
# makes this tricky though. _get_acquisiton_value() in particular is
# problematic because it needs to distinguish between "add" and "edit"
# situations, and currently does so in a way that doesn't work for
# programmatic content creation.

def set_default_with_acquisition(field, default=None):
    """
    Sets a default value generator which uses the value
    from the parent object, if existing, otherwise it uses
    the given default value.
    """
    field._acquisition_default = default

    def default_value_generator(data):
        obj = data.context
        # try to get it from context or a parent
        while obj and not ISiteRoot.providedBy(obj):
            try:
                interface_ = data.field.interface
            except AttributeError:
                pass
            else:
                try:
                    adpt = interface_(obj)
                except TypeError:
                    # could not adapt
                    pass
                else:
                    value = data.field.get(adpt)
                    if value is not None:
                        return value
            obj = aq_parent(aq_inner(obj))
        # otherwise use default value
        if field._acquisition_default:
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
