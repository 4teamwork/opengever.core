from opengever.ogds.base.actor import Actor
from opengever.ogds.models.team import Team
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from sqlalchemy.orm.exc import NoResultFound
from zExceptions import BadRequest


class ListTeamMembers(BrowserView):
    """Fetch team group and group members by team id."""

    template = ViewPageTemplateFile("list_groupmembers.pt")

    def __init__(self, context, request):
        super(ListTeamMembers, self).__init__(context, request)

        self.active = None
        self.members = None
        self.team_id = None
        self.group_id = None

    def __call__(self):
        self.team_id = self.context.REQUEST.get('team', None)
        self.members = []

        if not self.team_id:
            raise BadRequest('no team id')

        try:
            team = Team.query.filter_by(team_id=self.team_id).one()
            group = getattr(team, 'group', None)
            self.group_id = getattr(group, 'groupid', None)
        except NoResultFound:
            self.group_id = None

        if not self.group_id:
            raise BadRequest('no group id')

        self.active = getattr(group, 'active', None)

        actors = [Actor.user(user.userid) for user in getattr(group, 'users', [])]
        actors.sort(key=lambda actor: actor.get_label())
        self.members = [each.get_link() for each in actors]

        return self.template()
