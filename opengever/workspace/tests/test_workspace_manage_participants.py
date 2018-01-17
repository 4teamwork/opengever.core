from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.invitation import Invitation
from opengever.workspace.participation.storage import IInvitationStorage


def get_entry_by_userid(entries, userid):
    for entry in entries:
        if entry['userid'] == userid:
            return entry
    return None


class TestWorkspaceManageParticipants(IntegrationTestCase):

    def setUp(self):
        super(TestWorkspaceManageParticipants, self).setUp()

    @browsing
    def test_list_all_current_participants(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.visit(self.workspace, view='manage-participants')

        self.assertItemsEqual(
            [
                {u'can_manage': True,
                 u'name': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger@gever.local)',
                 u'roles': [u'WorkspaceMember'],
                 u'type_': u'user',
                 u'userid': u'beatrice.schrodinger'},
                {u'can_manage': False,
                 u'name': u'Hugentobler Fridolin (fridolin.hugentobler@gever.local)',
                 u'roles': [u'WorkspaceAdmin'],
                 u'type_': u'user',
                 u'userid': u'fridolin.hugentobler'},
                {u'can_manage': True,
                 u'name': u'Fr\xf6hlich G\xfcnther (gunther.frohlich@gever.local)',
                 u'roles': [u'WorkspaceOwner'],
                 u'type_': u'user',
                 u'userid': u'gunther.frohlich'},
                {u'can_manage': True,
                 u'name': u'Peter Hans (hans.peter@gever.local)',
                 u'roles': [u'WorkspaceGuest'],
                 u'type_': u'user',
                 u'userid': u'hans.peter'},
            ],
            browser.json
        )

    @browsing
    def test_current_logged_in_admin_cannot_manage_himself(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.visit(self.workspace, view='manage-participants')
        self.assertFalse(
            get_entry_by_userid(browser.json, 'fridolin.hugentobler')[
                'can_manage'],
            'The admin should not be able to manage himself')
        self.assertTrue(
            get_entry_by_userid(browser.json, 'hans.peter')['can_manage'],
            'The admin should be able to manage hans.peter')

    @browsing
    def test_user_without_sharing_permission_cannot_manage(self, browser):
        self.login(self.workspace_member, browser=browser)
        browser.visit(self.workspace, view='manage-participants')
        self.assertFalse(
            get_entry_by_userid(browser.json, 'gunther.frohlich')[
                'can_manage'],
            'The admin should not be able to manage himself')

    @browsing
    def test_list_all_pending_invitations(self, browser):
        self.login(self.workspace_admin, browser=browser)
        storage = IInvitationStorage(self.workspace)
        workspace2 = create(Builder('workspace')
                            .within(self.workspace_root)
                            .titled(u'Second workspace'))
        invitation = Invitation(workspace2, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')
        storage.add_invitation(invitation)

        browser.visit(workspace2, view='manage-participants')
        self.assertEquals(
            [
                {u'can_manage': False,
                 u'userid': u'fridolin.hugentobler',
                 u'type_': u'user',
                 u'roles': [u'WorkspaceOwner'],
                 u'name': u'Hugentobler Fridolin (fridolin.hugentobler@gever.local)'},
                {u'name': u'B\xe4rfuss K\xe4thi (kathi.barfuss@gever.local)',
                 u'roles': u'WorkspacesUser',
                 u'can_manage': True,
                 u'iid': invitation.iid,
                 u'type_': u'invitation',
                 u'inviter': u'Hugentobler Fridolin (fridolin.hugentobler@gever.local)'}
            ],
            browser.json)
