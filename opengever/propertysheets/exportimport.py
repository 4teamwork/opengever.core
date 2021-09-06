"""
Here we override all of plone.supermodel's export / import handlers with
our custom ones.

We mainly want to customize behavior in the BaseHandler class, in order to add
support for serialization / deserialization of additional attributes, like
defaultFactory.

But because the BaseHandler isn't a utility on its own, but instead gets
subclassed, we need to re-instantiate and re-register all of the type
specific handlers to make use of it.
"""

from opengever.propertysheets.default_expression import attach_expression_default_factory
from opengever.propertysheets.default_from_member import attach_member_property_default_factory
from plone.supermodel.converters import ObjectFromUnicode
from plone.supermodel.exportimport import BaseHandler as PSBaseHandler
from plone.supermodel.exportimport import ChoiceHandler as PSChoiceHandler
from plone.supermodel.exportimport import DictHandler as PSDictHandler
from plone.supermodel.exportimport import ObjectHandler as PSObjectHandler
from zope.component import adapter
from zope.dottedname.resolve import resolve
from zope.interface import implementer
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import IObject
import zope.schema


CUSTOM_FIELD_ATTRIBUTES = (
    'default_expression',
    'default_from_member',
)


class BaseHandler(PSBaseHandler):

    # Remove 'defaultFactory' from the write-blacklist
    filteredAttributes = PSBaseHandler.filteredAttributes.copy()
    filteredAttributes.pop('defaultFactory')

    def __init__(self, klass):
        """Add support for our custom attributes.

        These get stored as plain Python attributes on the IField that
        gets passed from/to the plone.supermodel export/import handlers.
        """
        super(BaseHandler, self).__init__(klass)

        # default_expression - string with a TALES expression
        self.fieldAttributes['default_expression'] = \
            zope.schema.TextLine(
                __name__='default_expression',
                title=u"Default from TALES expression"
            )

        # default_from_member - string wth a JSON encoded dict
        self.fieldAttributes['default_from_member'] = \
            zope.schema.TextLine(
                __name__='default_from_member',
                title=u"Default from Member property"
            )

    def _constructField(self, attributes):
        """Sneak our custom attributes by the zope.schema Field constructors.
        """
        custom_attrs = {name: None for name in CUSTOM_FIELD_ATTRIBUTES}

        # Pop them from the attributes dict passed to field constructors
        for attr_name in custom_attrs:
            custom_attrs[attr_name] = attributes.pop(attr_name, None)

        # Have the superclass construct the field as usual
        field = super(BaseHandler, self)._constructField(attributes)

        # Set the custom attributes as plain Python attributes on the field
        for attr_name, value in custom_attrs.items():
            if value is not None:
                setattr(field, attr_name, value)

        # If a default_expression is present, turn it into a defaultFactory
        default_expression = getattr(field, 'default_expression', None)
        if default_expression is not None:
            attach_expression_default_factory(field, default_expression)

        # If default_from_member is present, turn it into a defaultFactory
        default_from_member = getattr(field, 'default_from_member', None)
        if default_from_member is not None:
            attach_member_property_default_factory(field, default_from_member)

        return field

    def writeAttribute(self, attributeField, field, ignoreDefault=True):
        """Add support for serialization of our custom attributes.
        """
        attribute_name = attributeField.getName()

        # First, we serialize defaultFactories to dottednames.
        #
        # plone.supermodel's BaseHandler only supports deserialization,
        # probably because not all Python callables can be addressed via
        # dotted names, but we can make it work for simple cases without
        # any fancy scopes.
        if attribute_name == 'defaultFactory' and field.defaultFactory:
            # Create a clone of the field, with its defaultFactory callable
            # turned into a dottedname string so it can be serialized.
            clone = self.klass.__new__(self.klass)
            clone.__dict__.update(field.__dict__)
            clone.defaultFactory = dottedname(field.defaultFactory)
            field = clone

        # We also serialize some completely custom attributes that we
        # piggy-back on the IField. Because these are not part of the IField
        # schema (unlike defaultFactory), we need to make sure they don't get
        # in the way of serialization. We added them to fieldAttributes above,
        # which means they'll automatically be serialized. But if they don't
        # exist, we need to handle that here to avoid an AttributeError.
        if attribute_name in CUSTOM_FIELD_ATTRIBUTES:
            if not hasattr(field, attribute_name):
                return None

        return super(BaseHandler, self).writeAttribute(
            attributeField, field, ignoreDefault=ignoreDefault)


def dottedname(func):
    """Construct the dotted name for the given function.

    This only works for functions in module scope. Attempts to build a dotted
    name for an object any other scope will return `None`.

    We need to be defensive here, because we don't want this to trip up
    plone.supermodel XML serialization of regular types, outside the context
    of PropertySheets. Also, by making sure the name we built actually
    resolves back to the same object, we ensure roundtrip-safety.
    """
    path = (getattr(func, '__module__', None),
            getattr(func, '__name__', None))

    if not all(path):
        return None

    name = '.'.join(path)
    try:
        resolved = resolve(name)
    except (ImportError, ValueError, AttributeError):
        resolved = None

    # Make sure the name we constructed resolves to the given function
    if resolved is not func:
        return None

    return name


class DictHandlerFactory(BaseHandler, PSDictHandler):
    pass


class ObjectHandlerFactory(BaseHandler, PSObjectHandler):

    # Need to redefine those (like on PSObjectHandler) because we need to
    # inject our custom BaseHandler so it comes first in the MRO.
    filteredAttributes = BaseHandler.filteredAttributes.copy()
    filteredAttributes.update({'default': 'w', 'missing_value': 'w'})


class ChoiceHandlerFactory(BaseHandler, PSChoiceHandler):

    # Need to redefine those (like on PSChoiceHandler) because we need to
    # inject our custom BaseHandler so it comes first in the MRO.
    filteredAttributes = BaseHandler.filteredAttributes.copy()
    filteredAttributes.update(
        {'vocabulary': 'w',
         'values': 'w',
         'source': 'w',
         'vocabularyName': 'rw'
         }
    )


@implementer(IFromUnicode)
@adapter(IObject)
class SafeObjectFromUnicode(ObjectFromUnicode):

    def __init__(self, context):
        self.context = context

    def fromUnicode(self, value):
        # Fail gracefully if unable to resolve dotted name for a defaultFactory
        # (for example, because the function was deleted in the meantime) 
        if getattr(self.context, '__name__') == 'defaultFactory':
            try:
                obj = resolve(value)
                self.context.validate(obj)
                return obj
            except Exception:
                return None

        # Delegate to original implementation for all other cases
        return super(SafeObjectFromUnicode, self).fromUnicode(value)


# These are all the handlers from plone.supermodel.fields.
#
# We need to reinstantiate them here (and re-register them in overrides.zcml)
# to make sure they use or subclass our customized BaseHandler class from
# above.


BytesHandler = BaseHandler(zope.schema.Bytes)
ASCIIHandler = BaseHandler(zope.schema.ASCII)
BytesLineHandler = BaseHandler(zope.schema.BytesLine)
ASCIILineHandler = BaseHandler(zope.schema.ASCIILine)
TextHandler = BaseHandler(zope.schema.Text)
TextLineHandler = BaseHandler(zope.schema.TextLine)
BoolHandler = BaseHandler(zope.schema.Bool)
IntHandler = BaseHandler(zope.schema.Int)
FloatHandler = BaseHandler(zope.schema.Float)
DecimalHandler = BaseHandler(zope.schema.Decimal)
TupleHandler = BaseHandler(zope.schema.Tuple)
ListHandler = BaseHandler(zope.schema.List)
SetHandler = BaseHandler(zope.schema.Set)
FrozenSetHandler = BaseHandler(zope.schema.FrozenSet)
PasswordHandler = BaseHandler(zope.schema.Password)
DictHandler = DictHandlerFactory(zope.schema.Dict)
DatetimeHandler = BaseHandler(zope.schema.Datetime)
DateHandler = BaseHandler(zope.schema.Date)
SourceTextHandler = BaseHandler(zope.schema.SourceText)
URIHandler = BaseHandler(zope.schema.URI)
IdHandler = BaseHandler(zope.schema.Id)
DottedNameHandler = BaseHandler(zope.schema.DottedName)
InterfaceFieldHandler = BaseHandler(zope.schema.InterfaceField)
ObjectHandler = ObjectHandlerFactory(zope.schema.Object)
ChoiceHandler = ChoiceHandlerFactory(zope.schema.Choice)
