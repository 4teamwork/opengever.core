from ftw.bumblebee.browser.callback import BaseConvertCallbackView
from ftw.bumblebee.browser.callback import BaseDemandCallbackView
from opengever.base.security import elevated_privileges
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_OWNER_ID_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_TOKEN_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_STATUS_KEY
from plone import api
from zExceptions import MethodNotAllowed
from zExceptions import Unauthorized
from zope.annotation import IAnnotations
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify


class StoreArchivalFile(BaseConvertCallbackView):
    """Callback endpoint for the Bumblebee archival file conversion.
    The ArchivalFileConverter triggers the conversion and defines this view
    as callback. Therefore this view will be called by the Bumblebee app.
    """

    def handle_success(self, mimetype, file_data):
        ArchivalFileConverter(self.context).store_file(file_data, mimetype)

    def handle_error(self):
        ArchivalFileConverter(
            self.context).handle_temporary_conversion_failure()

    def handle_skipped(self):
        ArchivalFileConverter(
            self.context).handle_permanent_conversion_failure()


class ReceiveDocumentPDF(BaseDemandCallbackView):

    def __call__(self):
        if self.request.method != 'POST':
            raise MethodNotAllowed()
        if not IAnnotations(self.context)[PDF_SAVE_TOKEN_KEY] == self.get_opaque_id():
            raise Unauthorized
        return super(ReceiveDocumentPDF, self).__call__()

    def disable_csrf(self):
        """Do not disable csrf for this POST request."""
        return False

    def handle_success(self, mimetype, file_upload):
        # this view is called by bumblebee and hence the current user
        # is anonymous. This has side effects such as the preview not being
        # generated for the document. Hence we login as the owner of the document.
        document_owner_id = IAnnotations(self.context)[PDF_SAVE_OWNER_ID_KEY]
        user = api.user.get(userid=document_owner_id)
        with api.env.adopt_user(user=user):
            # filename will be reset by the sync_title_and_filename
            self.get_document().update_file(file_upload, mimetype, filename=u"temp.pdf")
            # Make sure all handlers are executed properly
            notify(ObjectModifiedEvent(self.context))
            IAnnotations(self.context)[PDF_SAVE_STATUS_KEY] = 'conversion-successful'
            IAnnotations(self.context).pop(PDF_SAVE_TOKEN_KEY)
            IAnnotations(self.context).pop(PDF_SAVE_OWNER_ID_KEY)

        with elevated_privileges():
            self.context.leave_shadow_state()

    def handle_skipped(self):
        IAnnotations(self.context)[PDF_SAVE_STATUS_KEY] = 'conversion-skipped'

    def handle_error(self):
        IAnnotations(self.context)[PDF_SAVE_STATUS_KEY] = 'conversion-failed'
