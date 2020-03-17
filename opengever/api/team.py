from opengever.ogds.models.team import Team
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
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
        teamid = self.read_params()
        team = Team.query.get(teamid)

        data = {
            '@id': '{}/@team/{}'.format(
                self.context.absolute_url(), teamid),
            '@type': 'virtual.ogds.team',
            }

        # Add all the data from the team table
        serializer = queryMultiAdapter((team, self.request), ISerializeToJson)
        data.update(serializer())

        # We add the team members
        data['users'] = []
        for user in team.group.users:
            user_serializer = queryMultiAdapter(
                (user, self.request), ISerializeToJsonSummary)
            data['users'].append(user_serializer())

        return data

    def read_params(self):
        if len(self.params) != 1:
            raise BadRequest("Must supply team ID as URL path parameter.")

        return self.params[0]
