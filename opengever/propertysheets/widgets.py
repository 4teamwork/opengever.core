from opengever.propertysheets.field import IPropertySheetField
from plone.restapi.serializer.converters import json_compatible
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IWidget
from zope.component import adapter
from zope.interface import implementer


@adapter(IPropertySheetField, IWidget)
@implementer(IDataConverter)
class PropertySheetFieldDataConverter(object):

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        """Make sure to convert persistent dicts to json compatible data."""

        return json_compatible(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""

        if not value:
            return self.field.missing_value

        self.field.validate(value)
        return value