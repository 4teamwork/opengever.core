from Acquisition import aq_inner
from collective.quickupload.interfaces import IQuickUploadFileFactory
from opengever.document.behaviors import IBaseDocument
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Invalid
from zope.lifecycleevent import ObjectModifiedEvent
import os
import transaction


@implementer(IQuickUploadFileFactory)
@adapter(IDocumentSchema)
class QuickUploadFileUpdater(object):
    """Specific quick_upload adapter for documents, which only replace the file
    with the uploaded one.

    Disallows non-.docx files for proposal documents.
    """

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, filename, title, description, content_type, data, portal_type):
        if not self.is_upload_allowed():
            raise Unauthorized

        try:
            self.context.update_file(
                data,
                content_type=content_type,
                filename=self.get_file_name(filename),
            )
            if IBaseDocument.providedBy(self.context):
                notify(ObjectModifiedEvent(self.context))
        except Invalid as exc:
            # This is an error, we abort the transaction
            transaction.abort()
            msg = translate(exc.message, context=self.context.REQUEST)
            return {'error': msg, 'success': None}

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
