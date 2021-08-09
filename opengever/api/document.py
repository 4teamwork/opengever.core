from ftw import bumblebee
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
from opengever.workspaceclient.interfaces import ILinkedDocuments
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.content.update import ContentPatch
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


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
        result[u'thumbnail_url'] = bumblebee_service.get_representation_url(
            obj, 'thumbnail')
        result[u'preview_url'] = bumblebee_service.get_representation_url(
            obj, 'preview')
        result[u'pdf_url'] = bumblebee_service.get_representation_url(
            obj, 'pdf')
        result[u'file_extension'] = self.context.get_file_extension()

        extend_with_backreferences(
            result, self.context, self.request, 'relatedItems')

        checked_out_by = obj.checked_out_by()
        checked_out_by_fullname = display_name(checked_out_by) if checked_out_by else None

        additional_metadata = {
            'checked_out': checked_out_by,
            'checked_out_fullname': checked_out_by_fullname,
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
            'creator': serialize_actor_id_to_json_summary(obj.Creator()),
        }

        result.update(additional_metadata)
        return result

    def getVersion(self, version):
        """Return context when no lazy initial version exists."""

        if not Versioner(self.context).has_initial_version():
            return self.context

        return super(SerializeDocumentToJson, self).getVersion(version)


class DocumentPatch(ContentPatch):

    def reply(self):

        # Only allow updating a documents file if the document is checked-out
        # by the current user.
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        if not manager.is_checked_out_by_current_user():
            data = json_body(self.request)
            if 'file' in data:
                self.request.response.setStatus(403)
                return dict(error=dict(
                    type='Forbidden',
                    message='Document not checked-out by current user.'))

        return super(DocumentPatch, self).reply()


@implementer(IExpandableElement)
@adapter(IBaseDocument, IOpengeverBaseLayer)
class Approvals(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=True):
        approvals = IApprovalList(self.context)
        return {'approvals': IJsonCompatible(approvals.get())}
