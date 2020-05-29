from opengever.ogds.models.group import Group
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class OGDSGroupsGet(Service):
    """API Endpoint that returns a single group from ogds.

    GET /@ogds-groups/group.id HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(OGDSGroupsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    def reply(self):
        groupid = self.read_params()
        group = Group.query.get(groupid)
        serializer = queryMultiAdapter((group, self.request), ISerializeToJson)
        return serializer()

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply group ID as URL path parameter.")

        return self.params[0]
