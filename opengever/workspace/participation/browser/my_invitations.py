from opengever.base.role_assignments import InvitationRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.security import elevated_privileges
from opengever.ogds.base.actor import PloneUserActor
from opengever.workspace import _
from opengever.workspace import is_workspace_feature_enabled
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

    def is_feature_enabled(self):
        return is_workspace_feature_enabled()

    def storage(self):
        return getUtility(IInvitationStorage)

    def get_invitations(self):
        userid = api.user.get_current().getId()
        target_title = _(u'Deleted Workspace')

        entries = list(self.storage().iter_invitions_for_recipient(userid))
        entries.sort(key=lambda item: item['created'])

        for entry in entries:
            with elevated_privileges():
                target = uuidToObject(entry['target_uuid'])
                if target:
                    target_title = target.Title()

            if target:
                inviter = PloneUserActor(entry['inviter'],
                                         user=api.user.get(entry['inviter']))
                yield {'inviter': inviter.get_label(),
                       'target_title': target_title,
                       'iid': entry['iid']}

    def get_invitation_and_validate_payload(self):
        iid = self.request.get('iid', None)

        if iid is None:
            raise BadRequest('No iid given')

        invitation = self.storage().get_invitation(iid)
        if api.user.get_current().getId() != invitation['recipient']:
            raise BadRequest('Wrong invitation')

        return invitation

    def accept(self):
        """Accept a invitation by setting the role and redirect the user
        to the workspace.
        """
        invitation = self.get_invitation_and_validate_payload()
        with elevated_privileges():
            target = uuidToObject(invitation['target_uuid'])

            assignment = InvitationRoleAssignment(
                invitation['recipient'], [invitation['role']], target)
            RoleAssignmentManager(target).add_assignment(assignment)
            self.storage().remove_invitation(invitation['iid'])

        return self.request.RESPONSE.redirect(target.absolute_url())

    def decline(self):
        """Decline invitaion by deleting the invitation from the storage.
        """
        invitation = self.get_invitation_and_validate_payload()
        self.storage().remove_invitation(invitation['iid'])
        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '/' + self.__name__)
