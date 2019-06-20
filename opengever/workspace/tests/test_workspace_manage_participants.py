from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.ogds.base.utils import get_current_org_unit
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.storage import IInvitationStorage
from plone.protect import createToken
from zope.component import getUtility


def get_entry_by_token(entries, token):
    for entry in entries:
        if entry['token'] == token:
            return entry
    return None


class TestWorkspaceManageParticipants(IntegrationTestCase):

    def setUp(self):
        super(TestWorkspaceManageParticipants, self).setUp()
        self.login(self.workspace_admin)
        self.storage = getUtility(IInvitationStorage)

    @browsing
    def test_list_all_current_participants(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.visit(self.workspace, view='manage-participants')

        self.assertItemsEqual(
            [
                {u'can_manage': True,
                 u'name': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)',
                 u'roles': [u'WorkspaceMember'],
                 u'type_': u'user',
                 u'token': u'beatrice.schrodinger',
                 u'userid': u'beatrice.schrodinger'},
                {u'can_manage': False,
                 u'name': u'Hugentobler Fridolin (fridolin.hugentobler)',
                 u'roles': [u'WorkspaceAdmin'],
                 u'type_': u'user',
                 u'token': u'fridolin.hugentobler',
                 u'userid': u'fridolin.hugentobler'},
                {u'can_manage': False,
                 u'name': u'Fr\xf6hlich G\xfcnther (gunther.frohlich)',
                 u'roles': [u'WorkspaceOwner'],
                 u'type_': u'user',
                 u'token': u'gunther.frohlich',
                 u'userid': u'gunther.frohlich'},
                {u'can_manage': True,
                 u'name': u'Peter Hans (hans.peter)',
                 u'roles': [u'WorkspaceGuest'],
                 u'type_': u'user',
                 u'token': u'hans.peter',
                 u'userid': u'hans.peter'},
            ],
            browser.json
        )

    @browsing
    def test_current_logged_in_admin_cannot_manage_himself(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.visit(self.workspace, view='manage-participants')
        self.assertFalse(
            get_entry_by_token(browser.json, 'fridolin.hugentobler')[
                'can_manage'],
            'The admin should not be able to manage himself')
        self.assertTrue(
            get_entry_by_token(browser.json, 'hans.peter')['can_manage'],
            'The admin should be able to manage hans.peter')

    @browsing
    def test_user_without_sharing_permission_cannot_manage(self, browser):
        self.login(self.workspace_member, browser=browser)
        browser.visit(self.workspace, view='manage-participants')
        self.assertFalse(
            get_entry_by_token(browser.json, 'gunther.frohlich')[
                'can_manage'],
            'The admin should not be able to manage himself')

    @browsing
    def test_list_all_pending_invitations(self, browser):
        self.login(self.workspace_admin, browser=browser)
        workspace2 = create(Builder('workspace')
                            .within(self.workspace_root)
                            .titled(u'Second workspace'))
        iid = self.storage.add_invitation(
            workspace2, self.regular_user.getId(),
            self.workspace_admin.getId(), 'WorkspacesGuest')

        browser.visit(workspace2, view='manage-participants')
        self.assertEquals(
            [
                {u'can_manage': False,
                 u'token': u'fridolin.hugentobler',
                 u'type_': u'user',
                 u'roles': [u'WorkspaceOwner'],
                 u'name': u'Hugentobler Fridolin (fridolin.hugentobler)',
                 u'userid': u'fridolin.hugentobler'},
                {u'name': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                 u'roles': [u'WorkspacesGuest'],
                 u'can_manage': True,
                 u'token': iid,
                 u'type_': u'invitation',
                 u'inviter': u'Hugentobler Fridolin (fridolin.hugentobler)',
                 u'userid': u'kathi.barfuss'}
            ],
            browser.json)

    @browsing
    def test_add_invitiation(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.open(self.workspace.absolute_url() + '/manage-participants/add',
                     data={'userid': self.regular_user.getId(),
                           'role': 'WorkspaceGuest',
                           '_authenticator': createToken()})

        invitations = tuple(self.storage.iter_invitions_for_context(self.workspace))
        self.assertEquals(1, len(tuple(invitations)), 'Expect one invitation.')

        invitations_in_response = filter(
            lambda entry: entry['type_'] == 'invitation',
            browser.json)

        self.assertEquals(1, len(invitations_in_response),
                          'Expect one invitation in response')

        self.assertDictEqual(
            {u'can_manage': True,
             u'token': invitations[0]['iid'],
             u'inviter': u'Hugentobler Fridolin (fridolin.hugentobler)',
             u'name': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
             u'roles': [u'WorkspaceGuest'],
             u'type_': u'invitation',
             u'userid': u'kathi.barfuss'},
            invitations_in_response[0])

    @browsing
    def test_can_only_add_invitations_with_Workspace_related_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)
        with browser.expect_http_error(403):
            browser.open(self.workspace.absolute_url() + '/manage-participants/add',
                         data={'userid': self.regular_user.getId(),
                               'role': 'Reader',
                               '_authenticator': createToken()})

        with browser.expect_http_error(500):
            browser.open(self.workspace.absolute_url() + '/manage-participants/add',
                         data={'userid': self.regular_user.getId(),
                               'role': 'Site Administrator',
                               '_authenticator': createToken()})

    @browsing
    def test_can_only_add_invitations_with_the_right_permission(self, browser):
        self.login(self.workspace_member, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.workspace.absolute_url() + '/manage-participants/add',
                         data={'userid': self.regular_user.getId(),
                               'role': 'WorkspaceAdmin',
                               '_authenticator': createToken()})

    @browsing
    def test_delete_invitation(self, browser):
        self.login(self.workspace_admin, browser=browser)
        iid = self.storage.add_invitation(
            self.workspace, self.regular_user.getId(),
            self.workspace_admin.getId(), 'WorkspacesGuest')

        browser.open(self.workspace.absolute_url() + '/manage-participants/delete',
                     data={'token': iid,
                           'type': 'invitation',
                           '_authenticator': createToken()})

        invitations = self.storage.iter_invitions_for_context(self.workspace)
        self.assertEquals(0, len(tuple(invitations)),
                          'Expect no invitation anymore.')

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
            get_entry_by_token(browser.json, self.workspace_guest.getId()),
            'Expect to have no local roles anymore for the user')

    @browsing
    def test_current_user_cannot_remove_its_local_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.workspace.absolute_url() + '/manage-participants/delete',
                         data={'token': self.workspace_admin.getId(),
                               'type': 'user',
                               '_authenticator': createToken()})

    @browsing
    def test_modify_a_users_loca_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.open(self.workspace.absolute_url() + '/manage-participants/modify',
                     data={'token': self.workspace_guest.getId(),
                           'role': 'WorkspaceMember',
                           'type': 'user',
                           '_authenticator': createToken()})

        browser.visit(self.workspace, view='manage-participants')
        self.assertEquals(
            ['WorkspaceMember'],
            get_entry_by_token(browser.json,
                               self.workspace_guest.getId())['roles'])

    @browsing
    def test_cannot_modify_inexisting_user(self, browser):
        self.login(self.workspace_admin, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.workspace.absolute_url() + '/manage-participants/modify',
                         data={'token': self.regular_user.getId(),
                               'role': 'WorkspaceMember',
                               'type': 'user',
                               '_authenticator': createToken()})

    @browsing
    def test_can_only_modify_workspace_roles(self, browser):
        self.login(self.workspace_admin, browser=browser)

        with browser.expect_http_error(403):
            browser.open(self.workspace.absolute_url() + '/manage-participants/modify',
                         data={'token': self.regular_user.getId(),
                               'role': 'Contributor',
                               'type': 'user',
                               '_authenticator': createToken()})

    @browsing
    def test_modify_role_of_invitation(self, browser):
        self.login(self.workspace_admin, browser=browser)

        iid = self.storage.add_invitation(
            self.workspace, self.regular_user.getId(),
            self.workspace_admin.getId(), 'WorkspacesGuest')

        browser.open(self.workspace.absolute_url() + '/manage-participants/modify',
                     data={'token': iid,
                           'role': 'WorkspaceAdmin',
                           'type': 'invitation',
                           '_authenticator': createToken()})

        browser.visit(self.workspace, view='manage-participants')
        self.assertEquals(
            ['WorkspaceAdmin'],
            get_entry_by_token(browser.json, iid)['roles'])

    @browsing
    def test_do_not_allow_modifying_the_WorkspaceOwnerRole(self, browser):
        self.login(self.workspace_admin, browser=browser)

        with browser.expect_http_error(400):
            browser.open(self.workspace.absolute_url() + '/manage-participants/modify',
                         data={'token': self.workspace_owner.getId(),
                               'type': 'user',
                               'role': 'WorkspaceAdmin',
                               '_authenticator': createToken()})

    @browsing
    def test_search_for_users(self, browser):
        self.login(self.workspace_admin, browser=browser)

        for number in range(20):
            create(Builder('ogds_user')
                   .assign_to_org_units([get_current_org_unit()])
                   .having(firstname='Hans-{}'.format(str(number)),
                           lastname='Muster')
                   .id('hans.muster{}'.format(str(number))))

        browser.open(self.workspace.absolute_url() + '/manage-participants/search',
                     data={'q': 'beatrice'})

        self.assertEquals(
            {u'total_count': 1,
             u'pagination': {u'more': False},
             u'page': 1,
             u'results': [
                 {u'text': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger)',
                  u'_resultId': u'beatrice.schrodinger',
                  u'id': u'beatrice.schrodinger'}]},
            browser.json)

        browser.open(self.workspace.absolute_url() + '/manage-participants/search',
                     data={'q': 'hans'})

        self.assertEquals(21, browser.json['total_count'])
        self.assertEquals({u'more': True}, browser.json['pagination'])
        self.assertEquals(1, browser.json['page'])
        self.assertEquals(20, len(browser.json['results']))
