from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import ogds_service
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ListGroupMembers(BrowserView):
    template = ViewPageTemplateFile("list_groupmembers.pt")

    def __call__(self):
        self.group_id = self.context.REQUEST.get('group', None)
        self.members = []

        if not self.group_id:
            return 'no group id'

        for user in ogds_service().fetch_group(self.group_id).users:
            self.members.append(
                Actor.user(user.userid).get_link)
        return self.template()
