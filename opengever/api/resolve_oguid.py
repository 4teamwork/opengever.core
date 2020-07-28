from opengever.base.exceptions import InvalidOguidIntIdPart
from opengever.base.exceptions import MalformedOguid
from opengever.base.oguid import Oguid
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import Unauthorized
from zope.component import queryMultiAdapter
import requests


class ResolveOguidGet(Service):
    """Return serialized content for an object identified by an Oguid.

    GET /@resolve-oguid?oguid=foo:1234 HTTP/1.1
    """

    def reply(self):
        params = self.request.form.copy()
        raw_oguid = params.get('oguid', '').strip()

        if not raw_oguid:
            return self.request.response.setStatus(
                400, reason='Missing oguid query string parameter.')

        try:
            oguid = Oguid.parse(raw_oguid)
        except MalformedOguid:
            return self.request.response.setStatus(
                400, reason='Malformed oguid "{}".'.format(str(raw_oguid)))

        if oguid.is_on_current_admin_unit:
            return self._serialize_object(oguid)
        else:
            return self._get_remote_serialized_object(oguid, params)

    def _serialize_object(self, oguid):
        try:
            obj = oguid.resolve_object()
        except InvalidOguidIntIdPart:
            obj = None
        # obj could be `None` due to exception or as returned by resolve
        if not obj:
            return self.request.response.setStatus(
                400, reason='No object found for oguid "{}".'.format(
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

    def _get_remote_serialized_object(self, oguid, params):
        target_unit = ogds_service().fetch_admin_unit(oguid.admin_unit_id)
        if not target_unit:
            return self.request.response.setStatus(
                400, reason='Invalid admin unit id "{}".'.format(
                    oguid.admin_unit_id))

        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'X-OGDS-AC': api.user.get_current().getId(),
                   'X-OGDS-AUID': get_current_admin_unit().id()}
        url = '/'.join([target_unit.site_url, '@resolve-oguid'])

        # we pass all query string parameters to the remote request
        response = requests.get(url, params=params, headers=headers)
        if not response.ok:
            # transparently return non-ok responses
            return self.request.response.setStatus(
                response.status_code, reason=response.reason)
        return response.json()
