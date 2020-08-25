from opengever.api.proxy_base import ProxyingEndpointBase
from opengever.base.exceptions import InvalidOguidIntIdPart
from opengever.base.exceptions import MalformedOguid
from opengever.base.oguid import Oguid
from opengever.ogds.models.service import ogds_service
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import queryMultiAdapter


class ResolveOguidGet(ProxyingEndpointBase):
    """Return serialized content for an object identified by an Oguid.

    GET /@resolve-oguid?oguid=foo:1234 HTTP/1.1
    """

    def reply(self):
        qs_params = self.extract_query_string_params()
        raw_oguid = qs_params.get('oguid', '').strip()

        if not raw_oguid:
            raise BadRequest('Missing oguid query string parameter.')

        try:
            oguid = Oguid.parse(raw_oguid)
        except MalformedOguid:
            raise BadRequest('Malformed oguid "{}".'.format(str(raw_oguid)))

        if oguid.is_on_current_admin_unit:
            return self._serialize_object(oguid)
        else:
            return self._get_remote_serialized_object(oguid, qs_params)

    def _serialize_object(self, oguid):
        try:
            obj = oguid.resolve_object()
        except InvalidOguidIntIdPart:
            obj = None
        # obj could be `None` due to exception or as returned by resolve
        if not obj:
            raise BadRequest('No object found for oguid "{}".'.format(
                str(oguid)))

        if not api.user.has_permission('View', obj=obj):
            raise Unauthorized()

        serializer = queryMultiAdapter((obj, self.request), ISerializeToJson)
        if serializer is None:
            return self.request.response.setStatus(501)

        json = serializer()
        # as we just proxy to the object make sure we use correct @id
        json['@id'] = obj.absolute_url()
        return json

    def _get_remote_serialized_object(self, oguid, qs_params):
        target_unit = ogds_service().fetch_admin_unit(oguid.admin_unit_id)
        if not target_unit:
            raise BadRequest('Invalid admin unit id "{}".'.format(
                oguid.admin_unit_id))

        remote_url = '/'.join([target_unit.site_url, '@resolve-oguid'])

        # Detect and break proxying cycles
        self.detect_proxying_cycles(remote_url)

        # Set up authentication and proxy request to the remote admin unit
        headers = self.prepare_proxying_headers()

        # Proxy the request
        response = self.remote_request(
            'GET',
            remote_url,
            params=qs_params,
            headers=headers)

        # Transparently proxy back response status line and body
        return self.stream_back(response)
