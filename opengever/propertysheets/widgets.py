from opengever.propertysheets import _
from opengever.propertysheets.field import IPropertySheetField
from opengever.propertysheets.storage import PropertySheetSchemaStorage
from z3c.form import interfaces
from z3c.form.error import MultipleErrors
from z3c.form.interfaces import IContextAware
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
        dynamic_definition = PropertySheetSchemaStorage().query(slot_name)
        default_definition = PropertySheetSchemaStorage().query(self.field.default_slot)

        if dynamic_definition is not None:
            self._append_widgets(dynamic_definition, slot_name)

        if default_definition is not None:
            self._append_widgets(default_definition, self.field.default_slot)

    def _append_widgets(self, definition, slot):
        for name, field in definition.get_fields():
            widget = getMultiAdapter((field, self.request), IFieldWidget)
            identifier = self._make_widget_identifier(slot, name)
            widget.name = identifier
            widget.id = identifier
            widget.mode = self.mode

            widget.update()  # update is required to set up terms for sequences
            self.widgets.append(widget)

    def update(self):
        if '/++widget++' in self.request.URL:
            # z3c.form ++widget++ traversal requests try to update the entire
            # form (for example for autocomplete searches in the 'responsible'
            # field). This causes issues because of the 'special' way the
            # propertysheet widgets work, and we therefore prevent them from
            # updating themselves.
            return

        super(PropertySheetWiget, self).update()
        self.initialize_widgets()

        slot_name = self.field.get_active_assignment_slot(context=self.context)
        definitions = [
            (slot_name, PropertySheetSchemaStorage().query(slot_name)),
            (self.field.default_slot,
             PropertySheetSchemaStorage().query(self.field.default_slot))]

        if not any(definitions):
            return

        obj = self.value or dict()

        for (slot, definition) in definitions:
            if not definition:
                continue

            sheet_values = obj.get(slot, {})

            for name in definition.get_fieldnames():
                widget = self._get_widget(name)
                converter = IDataConverter(widget)
                sheet_value = sheet_values.get(name, None)
                widget.value = converter.toWidgetValue(sheet_value)
                widget.update()

                # XXX: Re-set the actual widget value after calling .update()
                #
                # This is necessary because these widgets aren't context aware,
                # and so in z3c.form Widget.update(), or our patched variant of
                # it respectively, an actual value for the widget never gets
                # extracted.
                #
                # That then leads to widget.value being overwritten with any
                # kind of default value that mess of a method is able to find.
                if sheet_value is not None:
                    widget.value = converter.toWidgetValue(sheet_value)

    def _get_widget(self, name):
        return [widget for widget in self.widgets if widget.field.getName() == name][0]

    def extract(self, default=interfaces.NO_VALUE):
        self.initialize_widgets()

        slot_name = self.field.get_active_assignment_slot(context=self.context)
        definitions = [
            (slot_name, PropertySheetSchemaStorage().query(slot_name)),
            (self.field.default_slot,
             PropertySheetSchemaStorage().query(self.field.default_slot))]

        if not any(definitions):
            return default

        errors = ()
        sheet_values = {}
        obj = self.value or dict()
        all_sheet_values = {}
        context_values = {}

        if IContextAware.providedBy(self) and not self.ignoreContext:
            context_values = getMultiAdapter((self.context, self.field),
                                             interfaces.IDataManager).query()

        for slot, definition in definitions:
            if not definition:
                continue

            found_request_value = False

            sheet_values = obj.get(slot, {})

            for name in definition.get_fieldnames():
                widget = self._get_widget(name)

                value = widget.field.missing_value
                try:
                    widget.setErrors = self.setErrors
                    raw = widget.extract(default=default)
                    if raw is not default:
                        found_request_value = True
                        value = IDataConverter(widget).toFieldValue(raw)
                    else:
                        # if there is no request value try falling back to the
                        # existing value or then the default missing value
                        value = sheet_values.get(name, widget.field.missing_value)

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
                    widget.value = IDataConverter(widget).toWidgetValue(value)
                    sheet_values[name] = value

            # When changing the slot-field value for example `document_type`,
            # we need to fetch the data directly from the context.
            if not found_request_value and context_values:
                sheet_values = context_values.get(slot)

            if sheet_values:
                all_sheet_values[slot] = sheet_values

        if self.setErrors and errors:
            # raise an error if one of our contained widgets has found an
            # error. No details are necessary, they will be rendered next
            # to the failing widget.
            raise Invalid(_(u"Custom properties contain some errors."))

        if not all_sheet_values:
            return default

        return all_sheet_values


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
        return value

    def toFieldValue(self, value):
        self.field.validate(value)
        return value
