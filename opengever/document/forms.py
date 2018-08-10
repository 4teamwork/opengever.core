from AccessControl import getSecurityManager
from opengever.base.formutils import field_by_name
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import NO_DOWNLOAD_DISPLAY_MODE
from opengever.document.interfaces import NO_DOWNLOAD_INPUT_MODE
from plone.autoform import directives as form
from plone.dexterity.browser import add
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.events import EditFinishedEvent
from plone.z3cform import layout
from z3c.form import button
from zope.component import queryMultiAdapter
from zope.event import notify


class DocumentAddForm(add.DefaultAddForm):
    """Provide a file upload form for Documents.

    Nullifies uploaded file on a validation error.
    """

    # hackishly tell validator to nullify uploaded file on validation
    # errors for this add form.
    _nullify_file_on_error = True


class DocumentAddView(add.DefaultAddView):
    """Provide a registerable view for the Document file upload form."""

    form = DocumentAddForm


class DocumentEditForm(DefaultEditForm):
    """Custom edit form for documents, which displays some
    different and customized edit modes.
    """

    def updateWidgets(self):
        """Using document specific formwidget.namedfile modes.
        """
        super(DocumentEditForm, self).updateWidgets()

        # get the checkin checkout manager
        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)
        if not manager:
            return

        # XXX: Maybe use IPrimaryFieldInfo here instead?
        # file_field = field_by_name(self, 'file')

        # if file_field:
        #     current_user_id = getSecurityManager().getUser().getId()
        #     if self.context.digitally_available:
        #         if manager.get_checked_out_by() == current_user_id:
        #             file_field.mode = NO_DOWNLOAD_INPUT_MODE
        #         else:
        #             file_field.mode = NO_DOWNLOAD_DISPLAY_MODE
        #     else:
        #         file_field.mode = NO_DOWNLOAD_INPUT_MODE


DocumentEditView = layout.wrap_form(DocumentEditForm)


class IDocumentFileUploadForm(IDocumentSchema):
    """Schema for the file upload form."""

    form.omitted('title')


class DocumentFileUploadForm(DefaultEditForm):
    """A form for just uploading the file of a document without any metadata
    fields. Used by Office Connector.
    """

    schema = IDocumentFileUploadForm
    additionalSchemata = ()
    render_form = True

    @button.buttonAndHandler(u'oc-file-upload', name='upload')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            self.request.response.setStatus(400)
            return

        manager = queryMultiAdapter((self.context, self.request),
                                    ICheckinCheckoutManager)
        if not manager.is_checked_out_by_current_user():
            self.request.response.setStatus(412)
            return

        self.applyChanges(data)
        self.request.response.setStatus(204)
        notify(EditFinishedEvent(self.context))
        self.render_form = False

    def render(self):
        if self.render_form:
            return super(DocumentFileUploadForm, self).render()
        self.request.response.setHeader('content-type', 'text/plain')
        return None
