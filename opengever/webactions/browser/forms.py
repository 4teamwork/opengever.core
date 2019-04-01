from opengever.webactions import _
from opengever.webactions.schema import IWebActionSchema
from opengever.webactions.storage import get_storage
from plone import api
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.i18n import MessageFactory as Z3CFormMF
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import NOT_CHANGED
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


class EditWebactionForm(WebactionForm):

    label = _(u'Edit Webaction')

    successMessage = Z3CFormMF('Data successfully updated.')
    noChangesMessage = Z3CFormMF('No changes were applied.')

    def updateWidgets(self, *args, **kwargs):
        super(EditWebactionForm, self).updateWidgets(*args, **kwargs)

        saving = 'form.buttons.save' in self.request

        # Prefill form widgets with persisted values from DB or
        # with missing value if needed
        webaction = self.get_webaction()
        for widget in self.widgets.values():
            # Always prefill readonly widgets.
            #
            # Prefill other widgets only upon initial rendering of the form,
            # not when trying to save - this is so we don't override
            # actual user provided inputs with persisted values from the
            # DB when rendering the form in the case of validation errors.
            if widget.field.readonly or not saving:
                name = widget.field.getName()
                value = webaction.get(name, widget.field.missing_value)
                if value is None:
                    continue
                converter = IDataConverter(widget)
                widget.value = converter.toWidgetValue(value)

    def get_action_id(self):
        return int(self.request.form['action_id'])

    def get_webaction(self):
        storage = get_storage()
        webaction = storage.get(self.get_action_id())
        return webaction

    def action(self):
        """Redefine <form action=''> attribute.
        """
        return self.request.getURL() + '?action_id=%s' % self.get_action_id()

    def field_value_has_changed(self, field, new_value, webaction):
        name = field.getName()
        no_value_marker = object()
        old_value = webaction.get(name, no_value_marker)
        # if a field is not set, its missing_value ss prefilled in the form
        # so that if the new value is the missing_value, the field was not
        # changed by the user.
        if old_value is no_value_marker:
            old_value = field.missing_value
        return old_value != new_value

    def applyChanges(self, data):
        # Based on z3c.form.form.applyChanges, but without firing events
        # and modifying the webaction in its storage.
        webaction = self.get_webaction()
        changes = {}
        webaction_data = {}
        for name, field in self.fields.items():
            # If the field is not in the data, then go on to the next one
            try:
                new_value = data[name]
            except KeyError:
                continue
            # If the value is NOT_CHANGED, ignore it, since the
            # widget/converter sent a strong message not to do so.
            if new_value is NOT_CHANGED:
                continue
            if self.field_value_has_changed(field.field, new_value, webaction):
                # Only update the data if it changed
                # TODO: Should we possibly be using toFieldValue here?
                webaction_data[name] = new_value

                # Record the change using information required later
                changes.setdefault(field.interface, []).append(name)
        if changes:
            storage = get_storage()
            storage.update(self.get_action_id(), webaction_data)
        return changes

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            api.portal.show_message(self.successMessage, getRequest())
        else:
            api.portal.show_message(self.noChangesMessage, getRequest())
        return self.request.RESPONSE.redirect(self.main_url)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        api.portal.show_message(_('Edit cancelled'), getRequest())
        return self.request.RESPONSE.redirect(self.main_url)
