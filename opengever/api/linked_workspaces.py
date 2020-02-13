from functools import wraps
from opengever.base.sentry import maybe_report_exception
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from requests import HTTPError
from requests import Timeout
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.interface import alsoProvides
from zope.publisher.http import status_reasons
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

        return super(LinkedWorkspacesService, self).render()


class LinkedWorkspacesGet(LinkedWorkspacesService):
    """API Endpoint to get all linked workspaces for a specific context
    """
    @request_error_handler
    def reply(self):
        if self.context.is_subdossier():
            raise BadRequest

        response = ILinkedWorkspaces(self.context).list()

        # The response id contains the url of the workspace-client request.
        # We don't want to send it back to the client. We replace it with the
        # actual client request url.
        response['@id'] = self.request.getURL()

        return response


class LinkedWorkspacesPost(LinkedWorkspacesService):
    """API Endpoint to add a new linked workspace.
    """

    @request_error_handler
    def reply(self):
        if self.context.is_subdossier():
            raise BadRequest

        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        # Validation will be done on the remote system
        data = json_body(self.request)

        return ILinkedWorkspaces(self.context).create(**data)
