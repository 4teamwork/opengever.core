from five import grok
from opengever.base.behaviors.utils import hide_fields_from_behavior
from opengever.base.form import WizzardWrappedAddForm
from opengever.base.interfaces import IRedirector
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.officeatwork import _
from plone import api
from plone.dexterity.i18n import MessageFactory as pd_mf
from z3c.form.button import buttonAndHandler


class DocumentFromOfficeatwork(WizzardWrappedAddForm):
    """Initialize creation of a document with officeatwork.

    Creates a document with the default add form, but hides the file-field.
    Then redirects to a view that initiates creation with officeatwork.

    """
    grok.context(IDossierMarker)
    grok.name('document_from_officeatwork')

    typename = 'opengever.document.document'

    def _create_form_class(self, parent_form_class, steptitle):

        class WrappedForm(parent_form_class):

            skip_validate_file_field = True
            label = _(u'Add document from officeatwork')

            def updateFields(self):
                """Hide the file-field.

                OfficeConnector creates a file with officeatwork on the
                desktop and adds it in a later step.

                """
                super(WrappedForm, self).updateFields()
                hide_fields_from_behavior(self, ['file'])

            @buttonAndHandler(_(u'Create with officeatwork'), name='save')
            def handleAdd(self, action):
                data, errors = self.extractData()
                if errors:
                    self.status = self.formErrorsMessage
                    return

                obj = self.createAndAdd(data)
                if obj is None:
                    return

                self._finishedAdd = True

                api.portal.show_message(
                    _(u'Creation with officeatwork initiated successfully'),
                    request=self.request,
                    type='info')

                target_url = '{}/create_with_officeatwork'.format(
                    self.context.absolute_url())

                redirector = IRedirector(self.request)
                redirector.redirect(target_url)

                return self.request.RESPONSE.redirect(
                    '{}#documents'.format(self.context.absolute_url()))

            @buttonAndHandler(pd_mf(u'Cancel'), name='cancel')
            def handleCancel(self, action):
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

        return WrappedForm
