from opengever.ogds.auth.admin_unit import create_auth_token
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from plone.restapi.services import Service
from urlparse import parse_qs
from zExceptions import InternalError
import requests


class ProxyingEndpointBase(Service):
    """Base class for endpoints that proxy request to remote admin units.
    """

    def extract_query_string_params(self):
        parsed = parse_qs(self.request['QUERY_STRING'])
        qs_params = dict((k, v if len(v) > 1 else v[0])
                         for k, v in parsed.iteritems())
        return qs_params

    def detect_proxying_cycles(self, remote_url):
        proxied_from = self.request.getHeader('X-GEVER-RemoteRequestFrom')
        if proxied_from:
            err_msg = (
                "Trying to proxy a request to {}, although the request was "
                "already proxied from {}".format(remote_url, proxied_from))
            raise InternalError(err_msg)

    def prepare_proxying_headers(self):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-OGDS-AC': create_auth_token(
                get_current_admin_unit().id(), api.user.get_current().getId()),
            'X-GEVER-RemoteRequestFrom': self.request.URL,
        }
        return headers

    def remote_request(self, method, remote_url, **kwargs):
        self.request.response.setHeader('X-GEVER-RemoteRequest', remote_url)
        return requests.request(method, remote_url, **kwargs)

    def stream_back(self, response):
        # Transparently proxy back response status line and body
        self.request.response.setStatus(
            response.status_code, reason=response.reason)

        try:
            response_json = response.json()
        except ValueError:
            response_json = {
                u'type': u'ValueError',
                u'message': u'Remote side returned a non-JSON response',
                u'remote_response_body': response.text,
            }
        return response_json
