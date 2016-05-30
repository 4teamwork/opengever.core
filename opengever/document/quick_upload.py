from Acquisition import aq_inner
from collective.quickupload.interfaces import IQuickUploadFileFactory
from five import grok
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
import os


class QuickUploadFileUpdater(grok.Adapter):
    """Specific quick_upload adapter for documents, which only replace the file
    with the uploaded one."""

    grok.context(IDocumentSchema)
    grok.implements(IQuickUploadFileFactory)

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, filename, title, description, content_type, data, portal_type):
        if not self.is_upload_allowed():
            raise Unauthorized

        self.context.update_file(
            self.get_file_name(filename), content_type, data)

        return {'success': self.context}

    def is_upload_allowed(self):
        manager = getMultiAdapter((self.context, self.context.REQUEST),
                                  ICheckinCheckoutManager)
        return manager.is_file_upload_allowed()

    def get_file_name(self, org_filename):
        filename, ext = os.path.splitext(org_filename)
        if self.context.file:
            filename = os.path.splitext(self.context.file.filename)[0]

        return ''.join([filename, ext])
