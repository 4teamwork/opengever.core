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
import zope.schema


class BaseHandler(PSBaseHandler):
    pass


class DictHandlerFactory(BaseHandler, PSDictHandler):
    pass


class ObjectHandlerFactory(BaseHandler, PSObjectHandler):
    pass


class ChoiceHandlerFactory(BaseHandler, PSChoiceHandler):
    pass


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
