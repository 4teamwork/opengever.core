from z3c.form.browser import widget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementsOnly


class IPropertySheetWiget(IWidget):
    pass


class PropertySheetWiget(widget.HTMLInputWidget, Widget):
    implementsOnly(IPropertySheetWiget)


@adapter(IPropertySheetWiget, IFormLayer)
@implementer(IFieldWidget)
def PropertySheetFieldWiget(field, request):
    return FieldWidget(field, PropertySheetWiget(request))
