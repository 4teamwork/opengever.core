from opengever.base.form import WizzardWrappedAddForm
from opengever.base.formutils import hide_field_by_name
from opengever.base.interfaces import IRedirector
from opengever.officeatwork import _
from plone import api
from plone.dexterity.i18n import MessageFactory as pd_mf
from z3c.form.button import buttonAndHandler


class DocumentFromOfficeatwork(WizzardWrappedAddForm):
    """Initialize creation of a document with officeatwork.

    Creates a document with the default add form, but hides the file-field.
    Then redirects to a view that initiates creation with officeatwork.

    """
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
                hide_field_by_name(self, 'file')

            @buttonAndHandler(_(u'Create with officeatwork'), name='save')
            def handleAdd(self, action):
                data, errors = self.extractData()
                if errors:
                    self.status = self.formErrorsMessage
                    return

                document = self.createAndAdd(data)
                if document is None:
                    return

                self._finishedAdd = True
                api.portal.show_message(
                    _(u'Creation with officeatwork initiated successfully'),
                    request=self.request,
                    type='info')

                # temporarily aq-wrap the document to be able to get an url
                aq_wrapped_doc = document.__of__(self.context)
                target_url = '{}/create_with_officeatwork'.format(
                    aq_wrapped_doc.absolute_url())
                redirector = IRedirector(self.request)
                redirector.redirect(target_url)

                return self.request.RESPONSE.redirect(
                    '{}#documents'.format(self.context.absolute_url()))

            def create(self, data):
                document = super(WrappedForm, self).create(data)
                self.initialize_in_shadow_state(document)
                return document

            def initialize_in_shadow_state(self, document):
                """Force the initial state to be document-state-shadow."""

                document.as_shadow_document()

            @buttonAndHandler(pd_mf(u'Cancel'), name='cancel')
            def handleCancel(self, action):
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

        return WrappedForm
