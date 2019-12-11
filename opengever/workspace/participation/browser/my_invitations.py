from opengever.base.role_assignments import InvitationRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.security import elevated_privileges
from opengever.ogds.base.actor import PloneUserActor
from opengever.workspace import _
from opengever.workspace import is_workspace_feature_enabled
from opengever.workspace.activities import WorkspaceWatcherManager
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
        email = api.user.get_current().getProperty('email')
        target_title = _(u'Deleted Workspace')

        entries = list(self.storage().iter_invitations_for_recipient_email(email))
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
                       'iid': entry['iid'],
                       'created': entry['created'],
                       }

    def get_invitation_and_validate_payload(self):
        iid = self.request.get('iid', None)

        if iid is None:
            raise BadRequest('No iid given')

        invitation = self._get_invitation(iid)
        if not invitation:
            raise BadRequest('Wrong invitation')

        return self._get_invitation(iid)

    def _get_invitation(self, iid):
        try:
            invitation = self.storage().get_invitation(iid)
        except KeyError:
            return None

        if api.user.get_current().getId() != invitation['recipient']:
            return None
        return invitation

    def accept(self):
        """Accept a invitation by setting the role and redirect the user
        to the workspace.
        """
        invitation = self.get_invitation_and_validate_payload()
        target = self._accept(invitation)
        return self.request.RESPONSE.redirect(target.absolute_url())

    def _accept(self, invitation):
        with elevated_privileges():
            target = uuidToObject(invitation['target_uuid'])

            assignment = InvitationRoleAssignment(
                invitation['recipient'], [invitation['role']], target)
            RoleAssignmentManager(target).add_or_update_assignment(assignment)
            self.storage().remove_invitation(invitation['iid'])

            manager = WorkspaceWatcherManager(self.context)
            manager.new_participant_added(invitation['recipient'], invitation['role'])

        return target

    def decline(self):
        """Decline invitaion by deleting the invitation from the storage.
        """
        invitation = self.get_invitation_and_validate_payload()
        self._decline(invitation)
        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '/' + self.__name__)

    def _decline(self, invitation):
        self.storage().remove_invitation(invitation.get('iid'))
