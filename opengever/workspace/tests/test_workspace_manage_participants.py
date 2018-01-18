from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.invitation import Invitation
from opengever.workspace.participation.storage import IInvitationStorage
from plone.protect import createToken


def get_entry_by_userid(entries, userid):
    for entry in entries:
        if entry['userid'] == userid:
            return entry
    return None


class TestWorkspaceManageParticipants(IntegrationTestCase):

    def setUp(self):
        super(TestWorkspaceManageParticipants, self).setUp()
        self.login(self.workspace_admin)
        self.storage = IInvitationStorage(self.workspace)

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
        workspace2 = create(Builder('workspace')
                            .within(self.workspace_root)
                            .titled(u'Second workspace'))
        invitation = Invitation(workspace2, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')
        self.storage.add_invitation(invitation)

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

    @browsing
    def test_add_invitiation(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.open(self.workspace.absolute_url() + '/manage-participants/add',
                     data={'userid': self.regular_user.getId(),
                           'role': 'WorkspaceGuest',
                           '_authenticator': createToken()})

        invitations = self.storage.get_invitations_for_context(self.workspace)
        self.assertEquals(1, len(invitations), 'Expect one invitation.')

        invitations_in_response = filter(
            lambda entry: entry['type_'] == 'invitation',
            browser.json)

        self.assertEquals(1, len(invitations_in_response),
                          'Expect one invitation in response')

        self.assertDictEqual(
            {u'can_manage': True,
             u'iid': invitations[0].iid,
             u'inviter': u'Hugentobler Fridolin (fridolin.hugentobler@gever.local)',
             u'name': u'B\xe4rfuss K\xe4thi (kathi.barfuss@gever.local)',
             u'roles': u'WorkspaceGuest',
             u'type_': u'invitation'},
            invitations_in_response[0])

    @browsing
    def test_delete_invitation(self, browser):
        self.login(self.workspace_admin, browser=browser)
        invitation = Invitation(self.workspace, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')
        self.storage.add_invitation(invitation)

        browser.open(self.workspace.absolute_url() + '/manage-participants/delete',
                     data={'token': invitation.iid,
                           'type': 'invitation',
                           '_authenticator': createToken()})

        invitations = self.storage.get_invitations_for_context(self.workspace)
        self.assertEquals(0, len(invitations), 'Expect no invitation anymore.')

        invitations_in_response = filter(
            lambda entry: entry['type_'] == 'invitation',
            browser.json)

        self.assertEquals(0, len(invitations_in_response),
                          'Expect no invitation in response')

    @browsing
    def test_delete_local_role(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.open(self.workspace.absolute_url() + '/manage-participants/delete',
                     data={'token': self.workspace_guest.getId(),
                           'type': 'user',
                           '_authenticator': createToken()})

        self.assertIsNone(
            get_entry_by_userid(browser.json, self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user')

    @browsing
    def test_modify_a_users_loca_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.open(self.workspace.absolute_url() + '/manage-participants/modify',
                     data={'userid': self.workspace_guest.getId(),
                           'role': 'WorkspaceMember',
                           '_authenticator': createToken()})

        browser.visit(self.workspace, view='manage-participants')
        self.assertEquals(
            ['WorkspaceMember'],
            get_entry_by_userid(browser.json,
                                self.workspace_guest.getId())['roles'])

    @browsing
    def test_cannot_modify_inexisting_user(self, browser):
        self.login(self.workspace_admin, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.workspace.absolute_url() + '/manage-participants/modify',
                         data={'userid': self.regular_user.getId(),
                               'role': 'WorkspaceMember',
                               '_authenticator': createToken()})
