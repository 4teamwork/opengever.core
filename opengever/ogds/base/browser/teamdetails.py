from opengever.ogds.base.actor import Actor
from opengever.ogds.models.team import Team
from Products.Five import BrowserView
from zExceptions import NotFound
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class TeamDetails(BrowserView):
    """Displays infos about a team.
    """

    @classmethod
    def url_for(cls, team_id):
        portal = getSite()
        return '/'.join((portal.portal_url(), '@@team-details', str(team_id)))

    def get_team(self):
        team = Team.get(int(self.team_id))
        if not team:
            raise NotFound

        return team

    def get_team_members(self):
        return [Actor.user(user.userid)
                for user in self.get_team().group.users]

    def publishTraverse(self, request, name):  # noqa
        """The name is the teamid of the team who should be displayed.
        """
        self.team_id = name
        return self
