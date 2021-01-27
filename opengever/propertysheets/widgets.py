from opengever.propertysheets import _
from opengever.propertysheets.field import IPropertySheetField
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.restapi.serializer.converters import json_compatible
from z3c.form import interfaces
from z3c.form.error import MultipleErrors
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.interface import Invalid
from zope.schema import getFieldNamesInOrder
from zope.schema import getFieldsInOrder


class IPropertySheetWiget(IWidget):
    pass


class PropertySheetWiget(Widget):
    """Composite widget rendering all fields for the active assignment slot.

    Extra care has to be taken when extracting values as `extract` will be
    called on various occasions. We only want to raise errors when the instance
    variable `setErrors` has ben set to `True` externally by the manager.

    Implementation has been inspired by existing widget managers that already
    render a list of widgets:
    - `z3c.form.field.FieldWidgets`
    - `z3c.form.contentprovider.FieldWidgetsAndProviders`
    """
    implementsOnly(IPropertySheetWiget)

    def __init__(self, request):
        super(PropertySheetWiget, self).__init__(request)
        self.widgets = []

    def _make_widget_identifier(self, slot_name, name):
        slot_name = slot_name.replace(".", "_")
        return "custom_property-{}-{}".format(slot_name, name)

    def initialize_widgets(self):
        self.widgets = []

        slot_name = self.field.get_active_assignment_slot(context=self.context)
        definition = PropertySheetSchemaStorage().query(slot_name)
        if definition is None:
            return

        schema_class = definition.schema_class

        for name, field in getFieldsInOrder(schema_class):
            widget = getMultiAdapter((field, self.request), IFieldWidget)
            identifier = self._make_widget_identifier(slot_name, name)
            widget.name = identifier
            widget.id = identifier
            widget.update()  # update is required to set up terms for sequences
            self.widgets.append(widget)

    def update(self):
        super(PropertySheetWiget, self).update()
        self.initialize_widgets()

        slot_name = self.field.get_active_assignment_slot(context=self.context)
        definition = PropertySheetSchemaStorage().query(slot_name)
        if definition is None:
            return

        schema_class = definition.schema_class
        obj = self.value or dict()
        sheet_values = obj.get(slot_name, {})

        for name, widget in zip(
            getFieldNamesInOrder(schema_class), self.widgets
        ):
            converter = IDataConverter(widget)
            sheet_value = sheet_values.get(name, None)
            widget.value = converter.toWidgetValue(sheet_value)
            widget.update()

    def extract(self, default=interfaces.NO_VALUE):
        self.initialize_widgets()

        slot_name = self.field.get_active_assignment_slot(context=self.context)
        definition = PropertySheetSchemaStorage().query(slot_name)
        if definition is None:
            return default

        schema_class = definition.schema_class
        errors = ()
        sheet_values = {}
        found_request_value = False

        for name, widget in zip(
            getFieldNamesInOrder(schema_class), self.widgets
        ):
            value = widget.field.missing_value
            try:
                widget.setErrors = self.setErrors
                raw = widget.extract(default=default)
                if raw is not default:
                    found_request_value = True
                    value = IDataConverter(widget).toFieldValue(raw)
                validator = getMultiAdapter(
                    (
                        self.context,
                        self.request,
                        self.form,
                        getattr(widget, "field", None),
                        widget,
                    ),
                    interfaces.IValidator,
                )
                validator.validate(value)
            except (Invalid, ValueError, MultipleErrors) as error:
                view = getMultiAdapter(
                    (
                        error,
                        self.request,
                        widget,
                        widget.field,
                        self.form,
                        self.context,
                    ),
                    interfaces.IErrorViewSnippet,
                )
                view.update()
                if self.setErrors:
                    widget.error = view
                errors += (view,)
            else:
                sheet_values[name] = value

        if self.setErrors and errors:
            # raise an error if one of our contained widgets has found an
            # error. No details are necessary, they will be rendered next
            # to the failing widget.
            raise Invalid(_(u"Custom properties contain some errors."))

        # Be careful not to return the dict we have created in case of no
        # actual request value. We only want to return the nested data
        # structure when data is in the request.
        if not found_request_value:
            return default

        return {slot_name: sheet_values}


@adapter(IPropertySheetField, IFormLayer)
@implementer(IFieldWidget)
def PropertySheetFieldWiget(field, request):
    return FieldWidget(field, PropertySheetWiget(request))


@adapter(IPropertySheetField, IWidget)
@implementer(IDataConverter)
class PropertySheetFieldDataConverter(object):
    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        """Make sure to convert Persistent to json compatible data."""
        return json_compatible(value)

    def toFieldValue(self, value):
        self.field.validate(value)
        return value
