from opengever.propertysheets.field import IPropertySheetField
from plone.restapi.serializer.converters import json_compatible
from plone.schema.browser.jsonfield import JSONDataConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IWidget
from zope.component import adapter
from zope.interface import implementer


@adapter(IPropertySheetField, IWidget)
@implementer(IDataConverter)
class PropertySheetFieldDataConverter(JSONDataConverter):

    def toWidgetValue(self, value):
        """Make sure to convert persistent dicts to json compatible data."""

        value = json_compatible(value)
        return super(PropertySheetFieldDataConverter, self).toWidgetValue(value)
