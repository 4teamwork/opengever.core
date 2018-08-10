from Acquisition import aq_inner
from collective.quickupload.interfaces import IQuickUploadFileFactory
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
import os


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

        if self.is_proposal_upload():
            if not os.path.splitext(self.get_file_name(filename))[1].lower() == '.docx':
                return {
                    'error': translate(_(
                        u'error_proposal_document_type',
                        default=u"It's not possible to have non-.docx documents as proposal documents.",
                        ),
                    context=getRequest(),
                    ),
                    'success': None,
                    }

        self.context.update_file(data,
                                 content_type=content_type,
                                 filename=self.get_file_name(filename))

        return {'success': self.context}

    def is_upload_allowed(self):
        manager = getMultiAdapter((self.context, self.context.REQUEST),
                                  ICheckinCheckoutManager)
        return manager.is_file_upload_allowed()

    def is_proposal_upload(self):
        """The upload form context can be, for example, a Dossier."""
        return getattr(self.context, 'is_inside_a_proposal', lambda: False)()

    def get_file_name(self, org_filename):
        filename, ext = os.path.splitext(org_filename)
        if self.context.file:
            filename = os.path.splitext(self.context.file.filename)[0]

        return ''.join([filename, ext])
