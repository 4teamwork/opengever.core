from opengever.base.security import elevated_privileges
from opengever.workspace import _
from opengever.workspace.participation.storage import IInvitationStorage
from plone import api
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest
from zope.component import getUtility


class MyWorkspaceInvitations(BrowserView):

    template = ViewPageTemplateFile('templates/my-invitations.pt')

    def __call__(self):

        return self.template()

    def get_invitations(self):
        storage = getUtility(IInvitationStorage)
        userid = api.user.get_current().getId()
        target_title = _(u'Deleted Workspace')

        entries = list(storage.iter_invitions_for_recipient(userid))
        entries.sort(key=lambda item: item['created'])

        for entry in storage.iter_invitions_for_recipient(userid):
            with elevated_privileges():
                target = uuidToObject(entry['target_uuid'])
                if target:
                    target_title = target.Title()

            if target:
                yield {'inviter': entry['inviter'],
                       'target_title': target_title,
                       'iid': entry['iid']}

    def accept(self):
        """Accept a invitation by setting the role and redirect the user
        to the workspace.
        """
        iid = self.request.get('iid', None)

        if iid is None:
            raise BadRequest('No iid given')

        storage = getUtility(IInvitationStorage)
        invitation = storage.get_invitation(iid)

        if api.user.get_current().getId() != invitation['recipient']:
            raise BadRequest('Wrong invitation')

        else:
            with elevated_privileges():
                target = uuidToObject(invitation['target_uuid'])
                target.manage_setLocalRoles(invitation['recipient'],
                                            [invitation['role']])
                target.reindexObjectSecurity()
                storage.remove_invitation(iid)

            return self.request.RESPONSE.redirect(target.absolute_url())
