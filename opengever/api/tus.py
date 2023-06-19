from collective.quickupload.browser.quick_upload import get_content_type
from opengever.api.not_reported_exceptions import BadRequest as NotReportedBadRequest
from opengever.base.interfaces import IDuringContentCreation
from opengever.document import _
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.meeting.proposaltemplate import IProposalTemplate
from opengever.propertysheets.creation_defaults import initialize_customproperties_defaults
from opengever.quota.exceptions import ForbiddenByQuota
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.services.content.tus import UploadPatch
from zExceptions import Forbidden
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces import IPublishTraverse
import logging
import transaction


logger = logging.getLogger('opengever.api')


@implementer(IPublishTraverse)
class GeverUploadPatch(UploadPatch):
    """TUS upload endpoint for handling PATCH requests"""

    def reply(self):
        try:
            alsoProvides(self.request, IDuringContentCreation)
            data = super(GeverUploadPatch, self).reply()
            noLongerProvides(self.request, IDuringContentCreation)
        except ForbiddenByQuota as exc:
            transaction.abort()
            raise Forbidden(exc.message)
        return data

    def create_or_modify_content(self, tus_upload):
        """Initialize default values for custom properties.
        """
        # We can't trust the content type provided in the request, so we use
        # get_content_type from quickupload instead.
        self.fix_content_type(tus_upload)
        result = super(GeverUploadPatch, self).create_or_modify_content(tus_upload)

        # Ugh. create_or_modify_content doesn't return the created object, so
        # we need to get it using the Location header that gets set.
        try:
            location = self.request.response.getHeader('Location')
            doc_id = location.replace(self.context.absolute_url(), '').lstrip('/')
            created_doc = self.context.restrictedTraverse(doc_id)
        except Exception as exc:
            created_doc = None
            logger.warn(
                'Failed to determine created document after TUS upload '
                'for %r. Got: %r' % (self.request, exc))

        if created_doc:
            initialize_customproperties_defaults(created_doc)
            self.add_additional_metadata(tus_upload.metadata(), created_doc)
        return result

    def fix_content_type(self, tus_upload):
        metadata = tus_upload.metadata()
        content_type = get_content_type(self.context, None, metadata.get("filename", ""))
        metadata["content-type"] = content_type

    def add_additional_metadata(self, metadata, obj):
        if not metadata.get("mode", "create") == 'create':
            return

        data = {}
        document_date = metadata.get('document_date')
        if document_date:
            data['document_date'] = document_date

        if data:
            deserializer = queryMultiAdapter((obj, self.request), IDeserializeFromJson)
            deserializer(data=data)


@implementer(IPublishTraverse)
class UploadPatch(GeverUploadPatch):
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
        if self.context.has_file() and not manager.is_checked_out_by_current_user():
            raise Forbidden("Document not checked out.")

        # Check will be fixed with https://4teamwork.atlassian.net/browse/CA-5107
        # if manager.is_locked_by_other():
        #     raise Forbidden("Document is locked.")

        if self.is_proposal_document_upload() or self.is_proposal_template_upload():
            tus_upload = self.tus_upload()
            metadata = tus_upload.metadata()
            filename = metadata.get("filename", "")
            if not filename.endswith('.docx'):
                msg = translate(_(
                    u'error_proposal_document_type',
                    default=u"It's not possible to have non-.docx documents as"
                            " proposal documents.",
                ), context=self.request),
                raise NotReportedBadRequest(msg)

    def is_proposal_document_upload(self):
        """The upload form context can be, for example, a Dossier."""
        return getattr(self.context, 'is_proposal_document', lambda: False)()

    def is_proposal_template_upload(self):
        return IProposalTemplate.providedBy(self.context)
