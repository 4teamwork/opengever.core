from z3c.form.browser import widget
from z3c.form.widget import FieldWidget, Widget
from z3c.form.interfaces import IFieldWidget, IFormLayer, ITextWidget, IAddForm
from zope.interface import implementsOnly, implementer
from zope.component import adapter

from opengever.dossier import _
from opengever.base.interfaces import IReferenceNumber


class IReferenceNumberWidget(ITextWidget):
    """ The ReferenceNumber Widget. """


class ReferenceNumberWidget(widget.HTMLTextInputWidget, Widget):
    """show the reference number as readonly, but only in the edit From"""

    implementsOnly(IReferenceNumberWidget)

    def update(self):
        super(ReferenceNumberWidget, self).update()
        self.mode = 'display'
        #check if is a add- or a editForm
        if IAddForm.providedBy(self.form.parentForm):
            self.value = _(
                u'label_no_reference_number',
                default="Reference Number will be generated \
                after content creation")
        else:
            self.value = IReferenceNumber(self.context).get_number()


@adapter(IReferenceNumberWidget, IFormLayer)
@implementer(IFieldWidget)
def referenceNumberWidgetFactory(field, request):
    """IFieldWidget factory for ReferenceNumberWidget."""

    return FieldWidget(field, ReferenceNumberWidget(request))
