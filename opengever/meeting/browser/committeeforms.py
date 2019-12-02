from opengever.base import _ as bmf
from opengever.meeting import _
from opengever.meeting.committee import Committee
from opengever.meeting.form import ModelProxyAddForm
from opengever.meeting.form import ModelProxyEditForm
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.interfaces import IFolderish
from z3c.form import button
from z3c.form import field
from zope.component import adapter
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class AddForm(ModelProxyAddForm, add.DefaultAddForm):
    """Form to create a committee."""

    fields = field.Fields(Committee.model_schema)
    content_type = Committee
    label = _('Add committee')


@adapter(IFolderish, IDefaultBrowserLayer, IDexterityFTI)
class AddView(add.DefaultAddView):
    form = AddForm


class EditForm(ModelProxyEditForm, edit.DefaultEditForm):

    fields = field.Fields(Committee.model_schema, ignoreContext=True)
    content_type = Committee

    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()

        if len(errors) and any([
                True for error in errors
                if error.message == u'error_default_template_is_in_allowed_templates']):
            self.widgets['allowed_ad_hoc_agenda_item_templates'].error = True
            self.widgets['ad_hoc_template'].error = True

        return super(EditForm, self).handleApply(self, action)

    @button.buttonAndHandler(bmf(u'label_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())
