from functools import wraps
from opengever.base.sentry import maybe_report_exception
from requests import HTTPError
from requests import Timeout
from zope.publisher.http import status_reasons
import json
import sys
import traceback


def raise_for_api_request(request, exc):
    if not request.get("error_as_message"):
        raise exc


def get_obj_by_path(portal, path):
    """restrictedTraverse checks all of the objects along the path are
    validated with the security machinery. But we only need to know if the
    user is able to access the given object.

    Used by RelationChoiceFieldDeserializer and Copy service customization.
    """

    path = path.rstrip('/').split('/')
    parent = portal.unrestrictedTraverse(path[:-1], None)
    if not parent:
        return None

    return parent.restrictedTraverse(path[-1], None)


REQUEST_TIMEOUT = 408
GATEWAY_TIMEOUT = 504
BAD_GATEWAY = 502

default_http_error_code_mapping = {
    REQUEST_TIMEOUT: {"return_code": GATEWAY_TIMEOUT},
    GATEWAY_TIMEOUT: {"return_code": GATEWAY_TIMEOUT}
}


def create_proxy_request_error_handler(
        logger, default_http_error_message,
        http_error_code_mappings=default_http_error_code_mapping):
    """Creates a Decorator function to handle requests to a service or external
    aplication.

    We handle HTTP and timeout-errors in a special way. All other request
    errors are handled by the rest-api with a 500 Internal Server Error.

    additional_http_error_code_mappings should be a dictionary mapping error
    codes from service to endpoint.
    """

    def request_error_handler(func):

        def handle_http_error(obj, exception):
            """Handles general http errors.

            We group these errors in a 502 Bad Gateway error.

            HTTP timeout errors will map to a 504 gateway timeout.
            """
            service_status_code = exception.response.status_code
            service_error = {'status_code': service_status_code}

            if service_status_code in http_error_code_mappings:
                mapping = http_error_code_mappings[service_status_code]
                status_code = mapping.get("return_code", BAD_GATEWAY)
                message = mapping.get("return_message", default_http_error_message)
                service_error['message'] = str(exception).decode('utf-8')
            else:
                status_code = BAD_GATEWAY
                message = default_http_error_message

            try:
                service_error.update(json.loads(exception.response.text))
            except ValueError:
                # No response body
                pass

            obj.request.response.setStatus(status_code)
            response = {
                u'message': message,
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

    return request_error_handler
