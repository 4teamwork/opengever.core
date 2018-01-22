from opengever.base.security import elevated_privileges
from opengever.workspace.participation.storage import IInvitationStorage
from plone import api
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility


class MyWorkspaceInvitations(BrowserView):

    template = ViewPageTemplateFile('templates/my-invitations.pt')

    def __call__(self):

        return self.template()

    def get_invitations(self):
        storage = getUtility(IInvitationStorage)
        userid = api.user.get_current().getId()
        for entry in storage.iter_invitions_for_recipient(userid):
            with elevated_privileges():
                target = uuidToObject(entry['target_uuid'])

            if target:
                yield {'inviter': entry['inviter'],
                       'target_title': target.Title()}
