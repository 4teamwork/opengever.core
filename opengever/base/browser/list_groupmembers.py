from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility


class ListGroupMembers(BrowserView):
    template = ViewPageTemplateFile("list_groupmembers.pt")

    def __call__(self):
        group_id = self.context.REQUEST.get('group', None)
        info = getUtility(IContactInformation)
        if not group_id:
            return 'no group id'
        self.group_name = group_id
        members = info.list_group_users(group_id)
        self.members = [info.render_link(member) for member in members]
        return self.template()
