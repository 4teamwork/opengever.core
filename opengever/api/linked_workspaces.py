from opengever.api.utils import create_proxy_request_error_handler
from opengever.document.behaviors import IBaseDocument
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.exceptions import CopyFromWorkspaceForbidden
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
import logging

logger = logging.getLogger('opengever.api: LinkedWorkspaces')

teamraum_request_error_handler = create_proxy_request_error_handler(
    logger, u'Error while communicating with the teamraum deployment')


class LinkedWorkspacesService(Service):
    def render(self):
        if not is_workspace_client_feature_available():
            raise NotFound

        if self.context.is_subdossier():
            raise BadRequest

        return super(LinkedWorkspacesService, self).render()


class ProxyHypermediaBatch(LinkedWorkspacesService):
    """When the remote workspace-client reply is batched, all
    batching URLS will contain the workspace-client URL. This
    is not what these proxy endpoints should send back, so that
    we need to replace the batching information before forwarding
    the reply.
    """

    def get_remote_client_reply(self):
        raise NotImplementedError()

    @teamraum_request_error_handler
    def reply(self):
        batch = self.get_remote_client_reply()
        proxy_batch = HypermediaBatch(self.request, [None for i in range(batch['items_total'])])
        batch['@id'] = proxy_batch.canonical_url
        batch['batching'] = proxy_batch.links
        return batch


class LinkedWorkspacesGet(ProxyHypermediaBatch):
    """API Endpoint to get all linked workspaces for a specific context
    """
    def get_remote_client_reply(self):
        response = ILinkedWorkspaces(self.context).list(**self.request.form)
        response['workspaces_without_view_permission'] = bool(ILinkedWorkspaces(
            self.context).number_of_linked_workspaces() - response['items_total'])
        return response


class LinkedWorkspacesPost(LinkedWorkspacesService):
    """API Endpoint to add a new linked workspace.
    """

    def render(self):
        if not self.context.is_open():
            raise Unauthorized
        return super(LinkedWorkspacesPost, self).render()

    @teamraum_request_error_handler
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        # Validation will be done on the remote system
        data = json_body(self.request)

        return ILinkedWorkspaces(self.context).create(**data)


class LinkToWorkspacePost(LinkedWorkspacesService):
    """API Endpoint to link a dossier to an existing workspace.
    """

    def render(self):
        if not self.context.is_open():
            raise Unauthorized
        return super(LinkToWorkspacePost, self).render()

    @teamraum_request_error_handler
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        data = json_body(self.request)
        workspace_uid = data.get('workspace_uid')
        if not workspace_uid:
            raise BadRequest("Property 'workspace_uid' is required")

        ILinkedWorkspaces(self.context).link_to_workspace(workspace_uid)
        return self.reply_no_content()


class UnlinkWorkspacePost(LinkedWorkspacesService):
    """API Endpoint to unlink a dossier from an existing workspace.
    """

    def render(self):
        if not api.user.has_permission('opengever.workspaceclient: Unlink Workspace',
                                       obj=self.context):
            raise Unauthorized
        return super(UnlinkWorkspacePost, self).render()

    @teamraum_request_error_handler
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        data = json_body(self.request)
        workspace_uid = data.get('workspace_uid')
        if not workspace_uid:
            raise BadRequest("Property 'workspace_uid' is required")

        ILinkedWorkspaces(self.context).unlink_workspace(workspace_uid)
        return self.reply_no_content()


class RemoveDossierReferencePost(Service):

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        user_agent = self.request.getHeader("User-Agent")
        if not user_agent.startswith('opengever.core/'):
            raise Unauthorized
        self.context.external_reference = u''
        self.context.reindexObject(idxs=["external_reference"])
        return self.reply_no_content()


class CopyDocumentToWorkspacePost(LinkedWorkspacesService):
    """API Endpoint to copy a document to a linked workspace.
    """
    @teamraum_request_error_handler
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        workspace_uid, document, lock = self.validate_data(json_body(self.request))

        return ILinkedWorkspaces(self.context).copy_document_to_workspace(
            document, workspace_uid, lock)

    def validate_data(self, data):
        workspace_uid = data.get('workspace_uid')
        if not workspace_uid:
            raise BadRequest("Property 'workspace_uid' is required")

        document_uid = data.get('document_uid')
        if not document_uid:
            raise BadRequest("Property 'document_uid' is required")

        document = uuidToObject(document_uid)
        if not document or not IBaseDocument.providedBy(document):
            raise BadRequest("The document does not exist")

        if document.is_checked_out():
            raise BadRequest(
                "Document can't be copied to a workspace because it's "
                "currently checked out")

        if not self.obj_contained_in(document, self.context):
            raise BadRequest(
                "Only documents within the current main dossier are allowed")

        lock = data.get('lock', False)
        return workspace_uid, document, lock

    def obj_contained_in(self, obj, container):
        catalog = api.portal.get_tool('portal_catalog')
        results = catalog.searchResults(
            path={'query': '/'.join(container.getPhysicalPath())},
            UID=obj.UID())

        return len(results)


class ListDocumentsInLinkedWorkspaceGet(ProxyHypermediaBatch):
    """API Endpoint to list the documents in a linked workspace.
    The workspace UID has to be passed as a path segment:
    /@list-documents-in-linked-workspace/workspace_uid
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ListDocumentsInLinkedWorkspaceGet, self).__init__(context, request)
        self.path_segments = []

    def publishTraverse(self, request, name):
        """Consume any path segments after /@list-documents-in-linked-workspace
        as parameters"""
        self.path_segments.append(name)
        return self

    def validate_path_segments(self):
        if len(self.path_segments) == 1:
            return self.path_segments[0]
        elif len(self.path_segments) == 0:
            raise BadRequest("Missing path segment 'workspace_uid'")
        raise BadRequest("Spurious path segments, only workspace_uid is allowed.")

    def get_remote_client_reply(self):
        workspace_uid = self.validate_path_segments()
        documents = ILinkedWorkspaces(self.context).list_documents_in_linked_workspace(workspace_uid, **self.request.form)
        return documents


class CopyDocumentFromWorkspacePost(LinkedWorkspacesService):
    """API Endpoint to copy a document form a linked workspace
    into the context (a dossier).
    """
    @teamraum_request_error_handler
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        workspace_uid, document_uid, as_new_version = self.validate_data(
            json_body(self.request))
        try:
            destination_document, retrieval_mode = ILinkedWorkspaces(
                self.context).copy_document_from_workspace(
                    workspace_uid, document_uid, as_new_version)
        except CopyFromWorkspaceForbidden:
            raise BadRequest(
                "Document can't be copied from workspace because it's "
                "currently checked out")

        serialized = self.serialize_object(destination_document)
        serialized['teamraum_connect_retrieval_mode'] = retrieval_mode
        return serialized

    def serialize_object(self, obj):
        serializer = queryMultiAdapter((obj, self.request), ISerializeToJson)
        serialized_obj = serializer()
        return serialized_obj

    def validate_data(self, data):
        workspace_uid = data.get('workspace_uid')
        if not workspace_uid:
            raise BadRequest("Property 'workspace_uid' is required")
        document_uid = data.get('document_uid')
        if not document_uid:
            raise BadRequest("Property 'document_uid' is required")
        as_new_version = bool(data.get('as_new_version', False))
        return workspace_uid, document_uid, as_new_version


class ListLinkedDocumentUIDsFromWorkspace(Service):

    def reply(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            path='/'.join(self.context.getPhysicalPath()),
            object_provides=IBaseDocument.__identifier__)

        uids = [brain.gever_doc_uid for brain in brains
                if brain.gever_doc_uid]

        return {'gever_doc_uids': uids}


class AddParticipationsOnWorkspacePost(LinkedWorkspacesService):
    """API Endpoint to add participations on a linked workspace.
    """

    @teamraum_request_error_handler
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        data = json_body(self.request)
        workspace_uid = data.get('workspace_uid')
        if not workspace_uid:
            raise BadRequest("Property 'workspace_uid' is required")

        participants = data.get('participants')
        if not participants:
            raise BadRequest("Property 'participants' is required")

        items = ILinkedWorkspaces(self.context).add_participations(
                workspace_uid, participants).get("items", [])

        return {
            "@id": "{}/@linked-workspace-participations".format(self.context.absolute_url()),
            "items": items
        }
