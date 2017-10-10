from opengever.ogds.base.actor import Actor
from plone import api
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

    def prepare_model_tabs(self, viewlet):
        if api.user.has_permission('cmf.ManagePortal', obj=self.context):
            url = u'{}/team-{}/edit'.format(
                self.context.parent.absolute_url(), self.model.team_id)
            return viewlet.prepare_edit_tab(url)

        return tuple()

    def get_team_members(self):
        return [Actor.user(user.userid)
                for user in self.model.group.users]
