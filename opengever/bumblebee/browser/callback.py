from ftw.bumblebee.browser.callback import BaseConvertCallbackView
from ftw.bumblebee.browser.callback import BaseDemandCallbackView
from opengever.base.security import elevated_privileges
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_TOKEN_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_STATUS_KEY
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
        if not IAnnotations(self.context)[PDF_SAVE_TOKEN_KEY] == self.request.form.get("pdf_save_under_token"):
            raise Unauthorized
        return super(ReceiveDocumentPDF, self).__call__()

    def disable_csrf(self):
        """Do not disable csrf for this POST request."""
        return False

    def handle_success(self, mimetype, file_upload):
        # filename will then be reset by the sync_title_and_filename_handler
        self.get_document().update_file(file_upload, mimetype, filename=u"temp.pdf")
        # This will notably call the sync_title_and_filename_handler
        notify(ObjectModifiedEvent(self.context))
        IAnnotations(self.context)[PDF_SAVE_STATUS_KEY] = 'conversion-successful'
        IAnnotations(self.context).pop(PDF_SAVE_TOKEN_KEY)

        with elevated_privileges():
            self.context.leave_shadow_state()

    def handle_skipped(self):
        IAnnotations(self.context)[PDF_SAVE_STATUS_KEY] = 'conversion-skipped'

    def handle_error(self):
        IAnnotations(self.context)[PDF_SAVE_STATUS_KEY] = 'conversion-failed'
