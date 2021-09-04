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

from plone.supermodel.exportimport import BaseHandler as PSBaseHandler
from plone.supermodel.exportimport import ChoiceHandler as PSChoiceHandler
from plone.supermodel.exportimport import DictHandler as PSDictHandler
from plone.supermodel.exportimport import ObjectHandler as PSObjectHandler
from zope.dottedname.resolve import resolve
import zope.schema


class BaseHandler(PSBaseHandler):

    # Remove 'defaultFactory' from the write-blacklist
    filteredAttributes = PSBaseHandler.filteredAttributes.copy()
    filteredAttributes.pop('defaultFactory')

    def writeAttribute(self, attributeField, field, ignoreDefault=True):
        """Add support for serialization of defaultFactories to dottednames.

        plone.supermodel's BaseHandler only supports deserialization, probably
        because not all Python callables can be addressed via dotted names,
        but we can make it work for simple cases without any fancy scopes.
        """
        if attributeField.getName() == 'defaultFactory' and field.defaultFactory:
            # Create a clone of the field, with its defaultFactory callable
            # turned into a dottedname string so it can be serialized.
            clone = self.klass.__new__(self.klass)
            clone.__dict__.update(field.__dict__)
            clone.defaultFactory = dottedname(field.defaultFactory)
            field = clone

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
    path = (func.__module__, func.__name__)
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
