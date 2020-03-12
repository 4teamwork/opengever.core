from opengever.ogds.base.actor import Actor
from opengever.ogds.models.service import ogds_service
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest


class ListGroupMembers(BrowserView):
    """Fetch group members by group id."""

    template = ViewPageTemplateFile("list_groupmembers.pt")

    def __init__(self, context, request):
        super(ListGroupMembers, self).__init__(context, request)

        self.active = None
        self.members = None
        self.group_id = None

    def __call__(self):
        self.group_id = self.context.REQUEST.get('group', None)
        self.members = []

        if not self.group_id:
            BadRequest('no group id')

        group = ogds_service().fetch_group(self.group_id)
        self.active = getattr(group, 'active', None)

        actors = [Actor.user(user.userid)
                  for user in getattr(group, 'users', [])]
        actors.sort(key=lambda actor: actor.get_label())
        self.members = [each.get_link() for each in actors]

        return self.template()
