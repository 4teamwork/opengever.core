from ftw import bumblebee
from ftw.bumblebee.mimetypes import is_mimetype_supported
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee.events import PDFDownloadedEvent
from opengever.workspace.utils import is_restricted_workspace_and_guest
from Products.Five import BrowserView
from zExceptions import Forbidden
from zExceptions import NotFound
from zope.event import notify


class OpenMailPDFView(BrowserView):
    """Redirect to bumblebee pdf for mails and fire downloaded event."""

    def __call__(self):
        if not is_bumblebee_feature_enabled():
            raise NotFound

        if is_restricted_workspace_and_guest(self.context):
            raise Forbidden()

        filename = self.request.get('filename')
        if not filename:
            raise NotFound

        notify(PDFDownloadedEvent(self.context))

        url = bumblebee.get_service_v3().get_representation_url(
            self.context, 'pdf', filename=filename)
        return self.request.RESPONSE.redirect(url)


class OpenDocumentPDFView(OpenMailPDFView):
    """Redirect to bumblebee pdf for documents."""

    def __call__(self):
        mimetypeitem = self.context.get_mimetype()
        if not mimetypeitem or not is_mimetype_supported(mimetypeitem[0]):
            raise NotFound

        return super(OpenDocumentPDFView, self).__call__()
