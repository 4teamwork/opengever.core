from opengever.base.visible_users_and_groups_filter import visible_users_and_groups_filter
from opengever.ogds.base.utils import ogds_service
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class OGDSUserGet(Service):
    """API Endpoint that returns a single user from ogds.

    GET /@ogds-users/user.id HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(OGDSUserGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    def reply(self):
        userid = self.read_params().decode('utf-8')
        if not visible_users_and_groups_filter.can_access_principal(userid):
            self.request.response.setStatus(404)
            return

        service = ogds_service()
        user = service.fetch_user(userid, username_as_fallback=True)
        serializer = queryMultiAdapter((user, self.request), ISerializeToJson)
        return serializer()

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply user ID as URL path parameter.")

        return self.params[0]
