from opengever.document.behaviors.propertysheets import IPropertySheetField
from opengever.document.behaviors.propertysheets import IPropertySheets
from opengever.propertysheets.definition import PropertySheetSchemas
from plone.schema.browser.jsonfield import JSONDataConverter
from z3c.form import interfaces
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.schema import getFieldNamesInOrder
from zope.schema import getFieldsInOrder
import json


class IPropertySheetWiget(IWidget):
    pass


class PropertySheetWiget(Widget):
    """
    the data grid field can server as an inspiration, see
    https://github.com/collective/collective.z3cform.datagridfield
    """
    implementsOnly(IPropertySheetWiget)

    def __init__(self, request):
        super(PropertySheetWiget, self).__init__(request)
        self.widgets = []
        self._widgets_updated = False

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Ensure that updateWidgets is called.
        super(PropertySheetWiget, self).update()
        if not self._widgets_updated:
            self.updateWidgets()

    def updateWidgets(self):
        """Setup internal widgets based on the value_type for each value item.
        """
        document_type = self.context.document_type
        schema_class = PropertySheetSchemas.get(document_type)
        if schema_class is None:
            return

        self.widgets = []

        # this is most likely very incorrect and i somehow fucked up that the
        # correct value is set on the widget. for the POC however it is good
        # enough.
        obj = json.loads(self.value) if self.value else IPropertySheets(self.context).property_sheets
        sheet_for_type = obj.get(document_type, {})

        for name, field in getFieldsInOrder(schema_class):
            widget = getMultiAdapter((field, self.request), IFieldWidget)
            converter = IDataConverter(widget)
            sheet_value = sheet_for_type.get(name, None)
            widget.value = converter.toWidgetValue(sheet_value)
            widget.name = "{}-{}".format(schema_class.getName(), widget.name)
            widget.id = "{}-{}".format(schema_class.getName(), widget.id)

            self.widgets.append(widget)
        self._widgets_updated = True

    def extract(self, default=interfaces.NO_VALUE):
        self.updateWidgets()

        document_type = self.context.document_type
        schema_class = PropertySheetSchemas.get(document_type)
        if schema_class is None:
            return None

        obj = json.loads(self.value) if self.value else {}
        sheet_for_type = obj.setdefault(document_type, {})

        for name, widget in zip(getFieldNamesInOrder(schema_class), self.widgets):

            value = widget.extract(default=default)
            if value is default:
                continue

            converter = IDataConverter(widget)
            sheet_value = converter.toFieldValue(value)
            sheet_for_type[name] = sheet_value

        return json.dumps(obj)


@adapter(IPropertySheetField, IFormLayer)
@implementer(IFieldWidget)
def PropertySheetFieldWiget(field, request):
    return FieldWidget(field, PropertySheetWiget(request))


@implementer(IDataConverter)
class PropertySheetsDataConverter(JSONDataConverter):
    """A JSON data converter."""

    adapts(IPropertySheetField, IWidget)
