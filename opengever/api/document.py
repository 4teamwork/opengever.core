from ftw import bumblebee
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.api import _
from opengever.api.actors import serialize_actor_id_to_json_summary
from opengever.api.serializer import extend_with_backreferences
from opengever.api.serializer import GeverSerializeToJson
from opengever.base.helpers import display_name
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.interfaces import IReferenceNumber
from opengever.document.approvals import IApprovalList
from opengever.document.behaviors import IBaseDocument
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.model import SubmittedDocument
from opengever.workspace.utils import is_restricted_workspace_and_guest
from opengever.workspace.utils import is_within_workspace
from opengever.workspaceclient import is_workspace_client_feature_enabled
from opengever.workspaceclient.interfaces import ILinkedDocuments
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.content.update import ContentPatch
from Products.CMFPlone.CatalogTool import getObjPositionInParent
from zExceptions import Forbidden
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
import os.path


MIME_DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


@implementer(ISerializeToJson)
@adapter(IBaseDocument, Interface)
class SerializeDocumentToJson(GeverSerializeToJson):

    def __call__(self, *args, **kwargs):
        result = super(SerializeDocumentToJson, self).__call__(*args, **kwargs)

        ref_num = IReferenceNumber(self.context)
        result[u'reference_number'] = ref_num.get_number()

        version = "current" if kwargs.get('version') is None else kwargs.get('version')
        obj = self.getVersion(version)
        bumblebee_service = bumblebee.get_service_v3()
        result['bumblebee_checksum'] = IBumblebeeDocument(obj).get_checksum()
        result[u'thumbnail_url'] = bumblebee_service.get_representation_url(
            obj, 'thumbnail')
        result[u'preview_url'] = bumblebee_service.get_representation_url(
            obj, 'preview')
        result[u'pdf_url'] = bumblebee_service.get_representation_url(
            obj, 'pdf')
        result[u'file_extension'] = obj.get_file_extension()

        extend_with_backreferences(
            result, self.context, self.request, 'relatedItems',
            documents_only=True)

        checked_out_by = obj.checked_out_by()
        checked_out_by_fullname = display_name(checked_out_by) if checked_out_by else None

        if is_meeting_feature_enabled():
            self.extend_with_meeting_metadata(result)

        if is_workspace_client_feature_enabled():
            result['is_locked_by_copy_to_workspace'] = obj.is_locked_by_copy_to_workspace()

        if is_within_workspace(self.context):
            result[u'restrict_downloading_document'] = is_restricted_workspace_and_guest(self.context)

        additional_metadata = {
            'checked_out': checked_out_by,
            'checked_out_fullname': checked_out_by_fullname,
            'checkout_collaborators': list(obj.get_collaborators()),
            'file_mtime': obj.get_file_mtime(),
            'getObjPositionInParent': getObjPositionInParent(obj)(),
            'is_collaborative_checkout': obj.is_collaborative_checkout(),
            'is_locked': obj.is_locked(),
            'containing_dossier': obj.containing_dossier_title(),
            'containing_subdossier': obj.containing_subdossier_title(),
            'containing_subdossier_url': obj.containing_subdossier_url(),
            'trashed': obj.is_trashed,
            'is_shadow_document': obj.is_shadow_document(),
            'current_version_id': obj.get_current_version_id(
                missing_as_zero=True),
            'teamraum_connect_links': ILinkedDocuments(obj).serialize(),
            'workspace_document_urls': ILinkedDocuments(obj).get_workspace_document_urls(),
            'creator': serialize_actor_id_to_json_summary(obj.Creator()),
        }

        result.update(additional_metadata)
        return result

    def getVersion(self, version):
        """Return context when no lazy initial version exists."""

        if not Versioner(self.context).has_initial_version():
            return self.context

        return super(SerializeDocumentToJson, self).getVersion(version)

    def extend_with_meeting_metadata(self, result):
        submitted_documents = SubmittedDocument.query.by_source(self.context).all()
        result['submitted_with'] = [{'title': doc.proposal.title,
                                     '@id': doc.proposal.get_url()} for doc in submitted_documents]

        proposal = self.context.get_proposal()
        if proposal:
            result['proposal'] = {'title': proposal.Title(), '@id': proposal.absolute_url()}
        else:
            result['proposal'] = None

        result['meeting'] = None
        submitted_proposal = self.context.get_submitted_proposal()
        if submitted_proposal:
            result['submitted_proposal'] = {
                'title': submitted_proposal.Title(), '@id': submitted_proposal.absolute_url()}
            meeting = submitted_proposal.load_model().get_meeting()
            if meeting:
                result['meeting'] = {'title': meeting.title, '@id': meeting.get_url()}
        else:
            result['submitted_proposal'] = None


class DocumentPatch(ContentPatch):

    def reply(self):
        data = json_body(self.request)

        self._validate_checked_out(data)
        self._validate_proposal_document(data)

        return super(DocumentPatch, self).reply()

    def _validate_checked_out(self, data):
        """Only allow updating a documents file if the document is checked-out
        by the current user.
        """
        if 'file' not in data:
            return

        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        if not manager.is_checked_out_by_current_user():
            raise Forbidden(
                _(u'msg_not_checked_out_by_current_user',
                  default=u'Document not checked-out by current user.'))

    def _validate_proposal_document(self, data):
        """Prevent a proposals document being replaced by non-docx file.
        """
        if not self.context.is_inside_a_proposal():
            return

        if 'file' not in data:
            return

        value = data['file']
        if not value:
            raise Forbidden(
                _(u'msg_needs_file_in_proposal_document',
                  default=u"It's not possible to have no file in proposal documents."))

        content_type = value.get('content-type')
        filename = value.get('filename')

        if content_type and content_type != MIME_DOCX:
            raise Forbidden(
                _(u'msg_docx_mime_type_for_proposal',
                  default=u'Mime type must be ${docx_mimetype} for proposal documents.',
                  mapping={'docx_mimetype': MIME_DOCX}))

        if not os.path.splitext(filename)[1].lower() == '.docx':
            raise Forbidden(
                _(u'msg_docx_file_extension_for_proposal',
                  default=u'File extension must be .docx for proposal documents.'))


@implementer(IExpandableElement)
@adapter(IBaseDocument, IOpengeverBaseLayer)
class Approvals(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=True):
        approvals = IApprovalList(self.context)
        return {'approvals': IJsonCompatible(approvals.get())}
