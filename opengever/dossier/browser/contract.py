from five import grok
from opengever.dossier import _
from opengever.dossier.behaviors.contract import IContract
from opengever.dossier.browser.overview import DossierOverview
from opengever.dossier.contract import IContracDossierSchema
from z3c.form.field import Field
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IContextAware
from z3c.form.interfaces import IFieldWidget
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder


class ContractDossierOverview(DossierOverview):

    grok.context(IContracDossierSchema)
    grok.name('tabbedview_view-overview')

    def boxes(self):
        boxes = super(ContractDossierOverview, self).boxes()
        boxes[1].append(self.make_contract_data_box())
        return boxes

    def make_contract_data_box(self):
        return dict(id='contract', content=self.contract_meta_data(),
                    href='tasks', label=_("Contract meta data"))

    def contract_meta_data(self):
        items = []
        for id, field in getFieldsInOrder(IContract):
            value = field.get(IContract(self.context))
            if value and value != field.missing_value:
                # we need the form-field, not the schema-field we
                # already have..
                form_field = Field(field, interface=field.interface,
                       prefix='')
                items.append(self.get_widget(form_field))
        return items

    def get_widget(self, field):
        widget = getMultiAdapter((field.field, self.request), IFieldWidget)

        widget.name = '' + field.__name__  # prefix not needed
        widget.id = widget.name.replace('.', '-')
        widget.context = self.context
        alsoProvides(widget, IContextAware)
        widget.mode = DISPLAY_MODE
        widget.ignoreRequest = True
        widget.update()

        return widget
