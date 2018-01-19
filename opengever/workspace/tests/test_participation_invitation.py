from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.invitation import IInvitation
from opengever.workspace.participation.invitation import Invitation
from opengever.workspace.participation.storage import IInvitationStorage
from zope.interface.verify import verifyClass


class TestParticipationInvitation(IntegrationTestCase):

    def test_implements_interface(self):
        verifyClass(IInvitation, Invitation)

    def test_store_and_retrieve(self):
        self.login(self.workspace_owner)
        invitation = Invitation(target=self.workspace,
                                userid=self.workspace_admin.getId(),
                                inviter=self.workspace_guest.getId(),
                                role='WorkspaceGuest')
        iid = invitation.iid
        IInvitationStorage(self.portal).add_invitation(invitation)

        invitation = IInvitationStorage(self.portal).get_invitation_by_iid(iid)
        self.assertEquals(self.workspace, invitation.get_target())
        self.assertEquals(self.workspace_admin.getId(), invitation.userid)
        self.assertEquals(self.workspace_guest.getId(), invitation.inviter)
        self.assertEquals('WorkspaceGuest', invitation.role)
        self.assertEquals(iid, invitation.iid)
