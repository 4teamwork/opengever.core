from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class TeamGet(Service):
    """API Endpoint that returns a single team from ogds.

    GET /@team/team.id HTTP/1.1
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(TeamGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after service name as parameters
        self.params.append(name)
        return self

    def reply(self):
        team_id = self.read_params()
        return {
            '@id': '{}/@team/{}'.format(
                self.context.absolute_url(), team_id),
            '@type': 'virtual.ogds.team',
        }

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply team ID as URL path parameter.")

        return self.params[0]
