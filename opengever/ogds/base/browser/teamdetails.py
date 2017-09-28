from opengever.ogds.base.actor import Actor
from Products.Five import BrowserView
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class TeamDetails(BrowserView):
    """Displays infos about a team.
    """

    implements(IBrowserView, IPublishTraverse)

    def __init__(self, context, request):
        super(TeamDetails, self).__init__(context, request)
        self.model = self.context.model
        self.request = request

    def get_team_members(self):
        return [Actor.user(user.userid)
                for user in self.model.group.users]
