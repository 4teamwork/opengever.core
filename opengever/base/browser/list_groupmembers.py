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
        groups_tool = self.context.portal_groups
        group = groups_tool.getGroupById(group_id)
        self.group_name = group.title or group.id
        members = [(info.describe(member.id), info.render_link(member.id))
                      for member in group.getAllGroupMembers()]
        members.sort()
        self.members = [member[1] for member in members]
        return self.template()