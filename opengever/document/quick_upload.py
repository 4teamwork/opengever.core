from Acquisition import aq_inner
from collective.quickupload.interfaces import IQuickUploadFileFactory
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
import os


@implementer(IQuickUploadFileFactory)
@adapter(IDocumentSchema)
class QuickUploadFileUpdater(object):
    """Specific quick_upload adapter for documents, which only replace the file
    with the uploaded one."""

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, filename, title, description, content_type, data, portal_type):
        if not self.is_upload_allowed():
            raise Unauthorized

        self.context.update_file(data,
                                 content_type=content_type,
                                 filename=self.get_file_name(filename))

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
