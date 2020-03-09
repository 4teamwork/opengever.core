from functools import wraps
from opengever.base.sentry import maybe_report_exception
from opengever.document.behaviors import IBaseDocument
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from requests import HTTPError
from requests import Timeout
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.http import status_reasons
from zope.publisher.interfaces import IPublishTraverse
import json
import logging
import sys
import traceback

REQUEST_TIMEOUT = 408
GATEWAY_TIMEOUT = 504
BAD_GATEWAY = 502

logger = logging.getLogger('opengever.api: LinkedWorkspaces')


def request_error_handler(func):
    """Decorator function to handle request errors to the teamraum deployment.

    We handle HTTP and timeout-errors in a special way. All other request errors
    are handled by the rest-api with a 500 Internal Server Error.
    """
    def handle_http_error(obj, exception):
        """Handles general http errors.

        We group these errors in a 502 Bad Gateway error.

        HTTP timeout errors will map to a 504 gateway timeout.
        """
        service_status_code = exception.response.status_code
        service_error = {'status_code': service_status_code}

        if service_status_code in [REQUEST_TIMEOUT, GATEWAY_TIMEOUT]:
            status_code = GATEWAY_TIMEOUT
            service_error['message'] = str(exception).decode('utf-8')
        else:
            status_code = BAD_GATEWAY

        try:
            service_error.update(json.loads(exception.response.text))
        except ValueError:
            # No response body
            pass

        obj.request.response.setStatus(status_code)
        response = {
            u'message': u'Error while communicating with the teamraum deployment',
            u'type': status_reasons.get(status_code),
            u'service_error': service_error
        }
        return response

    def handle_timeout_error(obj, exception):
        """Handles all timeout errors. This can be:

        - ReadTimeout
        - ConnectTimeout

        We group these errors in a 504 Gateway Timeout error.
        """
        obj.request.response.setStatus(GATEWAY_TIMEOUT)
        return {
            u'message': str(exception).decode('utf-8'),
            u'type': type(exception).__name__.decode('utf-8'),
        }

    def log_exception_to_sentry(obj):
        e_type, e_value, tb = sys.exc_info()
        maybe_report_exception(obj, obj.request, e_type, e_value, tb)
        formatted_traceback = ''.join(traceback.format_exception(e_type, e_value, tb))
        logger.error('Exception while requesting teamraum deployment:\n%s', formatted_traceback)

    @wraps(func)
    def handler(obj, *args, **kwargs):
        try:
            return func(obj, *args, **kwargs)
        except HTTPError as exception:
            log_exception_to_sentry(obj)
            return handle_http_error(obj, exception)
        except Timeout as exception:
            log_exception_to_sentry(obj)
            return handle_timeout_error(obj, exception)

    return handler


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

    @request_error_handler
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
        return response


class LinkedWorkspacesPost(LinkedWorkspacesService):
    """API Endpoint to add a new linked workspace.
    """

    @request_error_handler
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Validation will be done on the remote system
        data = json_body(self.request)

        return ILinkedWorkspaces(self.context).create(**data)


class CopyDocumentToWorkspacePost(LinkedWorkspacesService):
    """API Endpoint to copy a document to a linked workspace.
    """
    @request_error_handler
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        workspace_uid, document = self.validate_data(json_body(self.request))

        return ILinkedWorkspaces(self.context).copy_document_to_workspace(
            document, workspace_uid)

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

        if not self.obj_contained_in(document, self.context):
            raise BadRequest(
                "Only documents within the current main dossier are allowed")

        return workspace_uid, document

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
    @request_error_handler
    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        workspace_uid, document_uid = self.validate_data(json_body(self.request))
        document = ILinkedWorkspaces(self.context).copy_document_from_workspace(
            workspace_uid, document_uid)
        return self.serialize_object(document)

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
        return workspace_uid, document_uid
