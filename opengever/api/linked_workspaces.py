from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.api import _
from opengever.api.utils import create_proxy_request_error_handler
from opengever.base.solr import OGSolrDocument
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.utils import find_parent_dossier
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.exceptions import CopyFromWorkspaceForbidden
from opengever.workspaceclient.exceptions import GeverDocumentCantBeChanged
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
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
import logging


logger = logging.getLogger('opengever.api: LinkedWorkspaces')

teamraum_request_error_handler = create_proxy_request_error_handler(
    logger, u'Error while communicating with the teamraum deployment')


class LinkedWorkspacesService(Service):

    forbidden_on_subdossiers = True

    def render(self):
        if not is_workspace_client_feature_available():
            raise NotFound

        if self.forbidden_on_subdossiers and self.context.is_subdossier():
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
    forbidden_on_subdossiers = False

    def get_remote_client_reply(self):
        main_dossier = self.context.get_main_dossier()
        response = ILinkedWorkspaces(main_dossier).list(**self.request.form)
        response['workspaces_without_view_permission'] = bool(ILinkedWorkspaces(
            main_dossier).number_of_linked_workspaces() - response['items_total'])
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
            raise BadRequest(_(u"workspace_uid_required",
                               default=u"Property 'workspace_uid' is required"))

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
            raise BadRequest(_(u"workspace_uid_required",
                               default=u"Property 'workspace_uid' is required"))
        deactivate_workspace = data.get('deactivate_workspace', False)
        ILinkedWorkspaces(self.context).unlink_workspace(workspace_uid, deactivate_workspace)
        return self.reply_no_content()


class RemoveDossierReferencePost(Service):

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        user_agent = self.request.getHeader("User-Agent")
        if not user_agent.startswith('opengever.core/'):
            raise Unauthorized
        self.context.external_reference = u''
        self.context.gever_url = u''
        self.context.reindexObject(idxs=["external_reference"])
        return self.reply_no_content()


class CopyDocumentToWorkspacePost(LinkedWorkspacesService):
    """API Endpoint to copy a document to a linked workspace.
    """
    @teamraum_request_error_handler
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        workspace_uid, folder_uid, document, lock = self.validate_data(json_body(self.request))

        return ILinkedWorkspaces(self.context).copy_document_to_workspace(
            document, workspace_uid, lock, folder_uid)

    def validate_data(self, data):
        workspace_uid = data.get('workspace_uid')
        if not workspace_uid:
            raise BadRequest(_(u"workspace_uid_required",
                               default=u"Property 'workspace_uid' is required"))

        folder_uid = data.get('folder_uid')

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
        return workspace_uid, folder_uid, document, lock

    def obj_contained_in(self, obj, container):
        catalog = api.portal.get_tool('portal_catalog')
        results = catalog.searchResults(
            path={'query': '/'.join(container.getPhysicalPath())},
            UID=obj.UID())

        return len(results)


class PrepareCopyDossierToWorkspacePost(Service):
    """API Endpoint to prepare copying a dossier to a linked workspace.

    This endpoints operates in two modes: Validation, or preparing an empty
    folder structure on the teamraum side to upload documents to.

    In validation mode, it checks that the given structure (subdossier(s) and
    documents) satisfies all the constraints to be copied to a workspace. If
    not, a detailed list of errors by object is returned.

    In "prepare structure" mode, it will mirror the structure of the given
    subdossier to teamraum by creating empty folders in the workspace, and
    returning a list of documents, including their target folders that the
    client should then upload them to.

    The second stage ("prepare structure") does not perform validation again.
    It assumes that the client validated the structure beforehand, and either
    everything is ok, or the user selected "copy anyway", in which case some
    individual document uploads will fail.
    """
    @teamraum_request_error_handler
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        if not is_workspace_client_feature_available():
            raise NotFound

        workspace_uid, validate_only, lock = self.validate_data(
            json_body(self.request))

        dossier = self.context
        self.client = ILinkedWorkspaces(dossier).client

        if validate_only:
            return self.validate_objects(workspace_uid, dossier)
        else:
            created_structure = self.create_structure(dossier, workspace_uid)
            response = {'docs_to_upload': []}
            for dossier_path, dossier_info in sorted(created_structure.items()):
                for doc in dossier_info['docs']:
                    response['docs_to_upload'].append({
                        'title': doc.title,
                        'target_folder_uid': dossier_info['uid'],
                        'source_document_uid': doc.UID(),
                    })
            return response

    def validate_data(self, data):
        workspace_uid = data.get('workspace_uid')
        if not workspace_uid:
            raise BadRequest(_(u"workspace_uid_required",
                               default=u"Property 'workspace_uid' is required"))

        validate_only = data.get('validate_only', False)

        lock = data.get('lock', False)
        return workspace_uid, validate_only, lock

    def validate_objects(self, workspace_uid, dossier):
        errors = []

        dossier_error = self.validate_dossier(workspace_uid, dossier)
        if dossier_error:
            errors.append(dossier_error)

        for doc in self.collect_documents(dossier):
            doc_error = self.validate_document(doc)
            if doc_error:
                errors.append(doc_error)

        if not errors:
            validation_result = {'ok': True}
        else:
            self.request.RESPONSE.setStatus(400)
            validation_result = {
                'ok': False,
                'errors': errors,
            }
        return validation_result

    def validate_dossier(self, workspace_uid, dossier):
        # Main dossier must be linked to given workspace
        main_dossier = dossier.get_main_dossier()
        if workspace_uid not in ILinkedWorkspaces(main_dossier).storage:
            uid = dossier.UID()
            msg = _(u'main_dossier_not_linked_to_workspace')
            return {
                'translated_message': translate(msg, context=self.request),
                'message': unicode(msg),
                'additional_metadata': {
                    'obj_uid': uid,
                    'obj_title': dossier.title,
                    'obj_url': dossier.absolute_url(),
                    'obj_type': dossier.portal_type,
                },
            }

    def validate_document(self, doc):
        # Document must not be checked out
        if doc.is_checked_out():
            msg = _(u'document_is_checked_out')
            return {
                'translated_message': translate(msg, context=self.request),
                'message': unicode(msg),
                'additional_metadata': {
                    'obj_uid': doc.UID(),
                    'obj_title': doc.title,
                    'obj_url': doc.absolute_url(),
                    'obj_type': doc.portal_type,
                },
            }

    def collect_documents(self, dossier_to_copy):
        return self._collect_objects(dossier_to_copy, IBaseDocument, trashed=False)

    def collect_dossiers(self, dossier_to_copy):
        return self._collect_objects(dossier_to_copy, IDossierMarker)

    def _collect_objects(self, dossier_to_copy, iface, trashed=None):
        solr = getUtility(ISolrSearch)
        query = {
            'path': {
                'query': '/'.join(dossier_to_copy.getPhysicalPath()),
                'depth': -1,
            },
            'object_provides': iface.__identifier__,
        }

        if trashed is not None:
            query['trashed'] = trashed

        response = solr.search(
            filters=make_filters(**query),
            sort='path asc',
        )
        objs = [OGSolrDocument(item).getObject() for item in response.docs]
        return objs

    def create_folder(self, parent_url, title):
        response = self.client.post(parent_url, json={
            '@type': 'opengever.workspace.folder',
            'title': title,
        })
        folder_url, folder_uid = response['@id'], response['UID']
        return folder_url, folder_uid

    def create_structure(self, dossier_to_copy, workspace_uid):
        workspace = self.client.get_by_uid(uid=workspace_uid)
        workspace_url = workspace['@id']

        def get_path(obj):
            return '/'.join(obj.getPhysicalPath())

        # Gather all subdossiers to mirror (including empty ones)
        dossiers_to_mirror = {}
        for subdossier in self.collect_dossiers(dossier_to_copy):
            dossier_path = get_path(subdossier)
            dossiers_to_mirror[dossier_path] = {'title': subdossier.title}

        # Gather all documents to mirror, and attach them to the correct
        # dossier-to-mirror node (we track them so we can tell what teamraum
        # folder a document goes into in the final response).
        for doc in self.collect_documents(dossier_to_copy):
            # If a doc is contained in a non-dossier container (task, proposal,
            # ...), we mirror it into the closest containing subdossier.
            parent_dossier = find_parent_dossier(doc)
            parent_path = get_path(parent_dossier)

            dossier_info = dossiers_to_mirror[parent_path]
            docs_in_dossier = dossier_info.setdefault('docs', [])
            docs_in_dossier.append(doc)

        # Now mirror the dossier structure to teamraum by creating empty
        # folders, and track the folder's URLs, uids and docs that should be
        # uploaded to them.
        created_dossiers = {}

        # Iterating over sorted paths ensures we create parents before children
        for dossier_path, dossier_info in sorted(dossiers_to_mirror.items()):
            # The parent_url for the folder we're about to create is either
            # one we just created before, and tracked, or the URL of the
            # workspace (which is linked to the main dossier).
            parent_path = dossier_path.rsplit('/', 1)[0]
            parent_url = created_dossiers.get(parent_path, {}).get('url')
            if not parent_url:
                parent_url = workspace_url

            title = dossier_info['title']
            folder_url, folder_uid = self.create_folder(parent_url, title)
            created_dossiers[dossier_path] = {
                'url': folder_url,
                'uid': folder_uid,
                'docs': dossier_info.pop('docs', []),
            }
        return created_dossiers


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

        workspace_uid, document_uid, as_new_version, trash_tr_document = self.validate_data(
            json_body(self.request))
        try:
            destination_document, retrieval_mode = ILinkedWorkspaces(
                self.context).copy_document_from_workspace(
                    workspace_uid, document_uid, as_new_version, trash_tr_document)
        except CopyFromWorkspaceForbidden:
            raise BadRequest(
                _("Document can't be copied from workspace because it's "
                  "currently checked out"))
        except LookupError:
            raise BadRequest(
                _("Document not in linked workspace"))
        except GeverDocumentCantBeChanged:
            raise BadRequest(
                _("Document can't be copied from workspace because GEVER "
                  "Document is finalized"))

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
            raise BadRequest(_(u"workspace_uid_required",
                               default=u"Property 'workspace_uid' is required"))
        document_uid = data.get('document_uid')
        if not document_uid:
            raise BadRequest("Property 'document_uid' is required")
        as_new_version = bool(data.get('as_new_version', False))
        trash_tr_document = bool(data.get("trash_tr_document", False))
        return workspace_uid, document_uid, as_new_version, trash_tr_document


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
            raise BadRequest(_(u"workspace_uid_required",
                               default=u"Property 'workspace_uid' is required"))

        participants = data.get('participants')
        if not participants:
            raise BadRequest(_(u"participant_required",
                               default=u"Property 'participants' is required"))

        items = ILinkedWorkspaces(self.context).add_participations(
            workspace_uid, participants).get("items", [])

        return {
            "@id": "{}/@linked-workspace-participations".format(self.context.absolute_url()),
            "items": items
        }


class AddInvitationOnWorkspacePost(LinkedWorkspacesService):
    """API Endpoint to add invitations on a linked workspace.
    """

    @teamraum_request_error_handler
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        data = json_body(self.request)
        workspace_uid = data.get('workspace_uid')
        if not workspace_uid:
            raise BadRequest(_(u"workspace_uid_required",
                               default=u"Property 'workspace_uid' is required"))

        recipient_email = data.get('recipient_email')
        if not recipient_email:
            raise BadRequest(_(u"recipient_email_required",
                               default=u"Property 'recipient_email' is required"))

        role = data.get('role')
        if not role:
            raise BadRequest(_(u"role_required",
                               default=u"Property 'role' is required"))

        ILinkedWorkspaces(self.context).add_invitation(workspace_uid, data)

        self.request.response.setStatus(204)
        return super(AddInvitationOnWorkspacePost, self).reply()
