from opengever.webactions import _
from opengever.webactions.schema import IWebActionSchema
from opengever.webactions.storage import get_storage
from plone import api
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import IDataConverter
from zope.globalrequest import getRequest


class WebactionForm(Form):

    ignoreContext = True
    fields = Fields(IWebActionSchema)

    def update(self):
        self.request.set('disable_border', True)
        super(WebactionForm, self).update()

    @property
    def main_url(self):
        return self.context.absolute_url() + '/@@manage-webactions'


class AddWebactionForm(WebactionForm):

    label = _(u'Add webaction')
    description = _(u'Add new webaction')

    def updateWidgets(self, *args, **kwargs):
        super(AddWebactionForm, self).updateWidgets(*args, **kwargs)

        saving = 'form.buttons.save' in self.request
        # Prefill other widgets only upon initial rendering of the form,
        # not when trying to save - this is so we don't override
        # actual user provided inputs with missing values
        if saving:
            return

        # Prefill form widgets with missing values
        for widget in self.widgets.values():
            missing_value = widget.field.missing_value
            if not missing_value:
                continue
            converter = IDataConverter(widget)
            widget.value = converter.toWidgetValue(missing_value)

    @button.buttonAndHandler(_(u'Add webaction'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Any field that is set to the missing value was not set by the user
        # and does not have to be saved.
        data = {key: value for key, value in data.items() if value != self.fields.get(key).field.missing_value}

        storage = get_storage()
        action_id = storage.add(data)

        msg = _('Webaction added: ${action_id}',
                mapping={'action_id': action_id})
        api.portal.show_message(msg, getRequest())
        return self.request.RESPONSE.redirect(self.main_url)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        api.portal.show_message(
            _(u'Webaction creation cancelled.'), getRequest())
        return self.request.RESPONSE.redirect(self.main_url)
