from opengever.document import _
from opengever.document.interfaces import ICheckinCheckoutManager
from plone.restapi.services.content.tus import UploadPatch
from opengever.meeting.proposaltemplate import IProposalTemplate
from zExceptions import BadRequest
from zExceptions import Forbidden
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import implementer


@implementer(IPublishTraverse)
class UploadPatch(UploadPatch):
    """TUS upload endpoint for handling PATCH requests"""

    # In addition to checking permissions we perform additional checks:
    # - The document must be checked out
    # - If locked, the lock token must be provided in the request
    # - If it's a proposal, the file must have a .docx extension
    def check_add_modify_permission(self, mode):
        super(UploadPatch, self).check_add_modify_permission(mode)

        if mode == 'create':
            return

        manager = getMultiAdapter((self.context, self.context.REQUEST),
                                  ICheckinCheckoutManager)
        if not manager.is_checked_out_by_current_user():
            raise Forbidden("Document not checked out.")

        # XXX: Currently not supported by the latest Office Connector 1.10.0
        # Enable this after a grace period when OC > 1.10.0 has been rolled out
        # to customers.
        # if manager.is_locked_by_other():
        #     raise Forbidden("Document is locked.")

        if self.is_proposal_upload() or self.is_proposal_template_upload():
            tus_upload = self.tus_upload()
            metadata = tus_upload.metadata()
            filename = metadata.get("filename", "")
            if not filename.endswith('.docx'):
                msg = translate(_(
                    u'error_proposal_document_type',
                    default=u"It's not possible to have non-.docx documents as"
                            " proposal documents.",
                ), context=self.request),
                raise BadRequest(msg)

    def is_proposal_upload(self):
        """The upload form context can be, for example, a Dossier."""
        return getattr(self.context, 'is_inside_a_proposal', lambda: False)()

    def is_proposal_template_upload(self):
        return IProposalTemplate.providedBy(self.context)
