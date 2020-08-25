from opengever.api.proxy_base import ProxyingEndpointBase
from opengever.base.exceptions import MalformedOguid
from opengever.base.exceptions import NonRemoteOguid
from opengever.base.exceptions import UnsupportedTypeForRemoteURL
from opengever.base.oguid import Oguid
from plone.restapi.deserializer import json_body
from zExceptions import BadRequest
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class RemoteWorkflowPost(ProxyingEndpointBase):
    """Proxies operations on the @workflow endpoint to a remote admin unit.

    POST /plone/@remote-workflow/some-transition

    {
      "remote_oguid": "fd:12345",
      "text": "I accept this task"
    }

    This endpoint will transparently proxy operations intended for the
    @workflow endpoint on a remote admin unit.

    Since the object in question is on a remote admin unit by definition, this
    endpoint is invoked on the Plone site root of the AU doing the proxying,
    instead of the actual context's path. The object in question is instead
    identified by a "remote_oguid" that must be supplied in the JSON body.
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ProxyingEndpointBase, self).__init__(context, request)
        self.path_params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@remote-workflow as parameters
        self.path_params.append(name)
        return self

    def _format_exception(self, exc):
        return '%s: %s' % (exc.__class__.__name__, str(exc))

    def reply(self):
        qs_params = self.extract_query_string_params()
        json_data = json_body(self.request)

        # Pop the remote_oguid from the JSON body, since it's not supposed to
        # be forwarded to the remote side.
        raw_remote_obj_oguid = json_data.pop('remote_oguid', None)
        if not raw_remote_obj_oguid:
            raise BadRequest(
                'Required parameter "remote_oguid" is missing in body')

        # Validate that Oguid is well-formed and refers to an object that is
        # actually remote, and of the supported type (tasks). Turn any Python
        # exceptions into proper 400 Bad Request responses with details in the
        # JSON body.

        try:
            remote_obj_oguid = Oguid.parse(raw_remote_obj_oguid)
        except MalformedOguid as exc:
            raise BadRequest(self._format_exception(exc))

        try:
            remote_obj_url = remote_obj_oguid.get_remote_url()
        except (UnsupportedTypeForRemoteURL, NonRemoteOguid) as exc:
            raise BadRequest(self._format_exception(exc))

        # Extract and forward path parameters (i.e., the transition)
        path_params = '/'.join(self.path_params)
        remote_url = '/'.join([remote_obj_url, '@workflow', path_params])

        # Detect and break proxying cycles
        self.detect_proxying_cycles(remote_url)

        # Set up authentication and proxy request to the remote admin unit
        headers = self.prepare_proxying_headers()

        self.request.response.setHeader('X-GEVER-RemoteRequest', remote_url)

        # Proxy the request
        response = self.remote_request(
            'POST',
            remote_url,
            json=json_data,
            params=qs_params,
            headers=headers)

        # Transparently proxy back response status line and body
        return self.stream_back(response)
