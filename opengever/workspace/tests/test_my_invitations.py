from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.storage import IInvitationStorage
from plone.protect import createToken
from zope.component import getUtility


class TestMyInvitationsView(IntegrationTestCase):

    features = ('workspace',)

    def setUp(self):
        super(TestMyInvitationsView, self).setUp()
        self.login(self.workspace_admin)
        self.storage = getUtility(IInvitationStorage)

        self.workspace2 = create(Builder('workspace')
                                 .within(self.workspace_root)
                                 .titled(u'Second workspace'))

        self.storage.add_invitation(
            self.workspace, self.regular_user.getId(),
            self.workspace_admin.getId(), 'WorkspaceGuest')
        self.storage.add_invitation(
            self.workspace2, self.regular_user.getId(),
            self.workspace_admin.getId(), 'WorkspaceGuest')
        self.storage.add_invitation(
            self.workspace2, self.workspace_guest.getId(),
            self.workspace_admin.getId(), 'WorkspaceGuest')

        RoleAssignmentManager(self.workspace_root).add_assignment(
            SharingRoleAssignment(self.regular_user.getId(),
                                  ['WorkspacesUser']))

    @browsing
    def test_list_invitations_of_logged_in_user(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.workspace_root, view='my-invitations')
        self.assertItemsEqual(
            ['Hugentobler Fridolin (fridolin.hugentobler) Second workspace Accept Decline',
             'Hugentobler Fridolin (fridolin.hugentobler) A Workspace Accept Decline'],
            browser.css('table.listing').first.body_rows.text)

    @browsing
    def test_accept_invition(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.workspace_root, view='my-invitations')
        browser.css('a.AcceptInvitation').first.click()
        self.assertEquals(self.workspace, browser.context)
        self.assertEquals(1,
                          len(tuple(self.storage.iter_invitions_for_recipient(
                              self.regular_user.getId()))),
                          'Expect only one item')

    @browsing
    def test_cannot_accept_invitation_of_other_users(self, browser):
        self.login(self.workspace_admin, browser=browser)
        foreign_iid = tuple(self.storage.iter_invitions_for_context(
            self.workspace))[0]['iid']

        with browser.expect_http_error(400):
            browser.open(self.workspace_root.absolute_url() + '/my-invitations/accept',
                         data={'iid': foreign_iid,
                               '_authenticator': createToken()})

    @browsing
    def test_cannot_accept_invalid_invitation(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(503):
            browser.open(self.workspace_root.absolute_url() + '/my-invitations/accept',
                         data={'iid': 'someinvalidiid',
                               '_authenticator': createToken()})

    @browsing
    def test_decline_invitation(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.workspace_root, view='my-invitations')
        browser.css('a.DeclineInvitation').first.click()

        self.assertEquals(
            self.workspace_root.absolute_url() + '/my-invitations',
            browser.url,
            'Expect to be on the my-invitations view')
        self.assertEquals(
            1,
            len(browser.css('table.listing').first.body_rows.text),
            'There should be only one invitation left')

    @browsing
    def test_cannot_access_workspace_of_declined_invitation(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.workspace_root, view='my-invitations')
        browser.css('a.DeclineInvitation').first.click()

        with browser.expect_unauthorized():
            browser.visit(self.workspace2)

    @browsing
    def test_cannot_decline_invitation_from_other_users(self, browser):
        self.login(self.workspace_admin, browser=browser)
        foreign_iid = tuple(self.storage.iter_invitions_for_context(
            self.workspace2))[0]['iid']

        with browser.expect_http_error(400):
            browser.open(self.workspace_root.absolute_url() + '/my-invitations/decline',
                         data={'iid': foreign_iid,
                               '_authenticator': createToken()})

    @browsing
    def test_cannot_decline_invalid_invitation(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(503):
            browser.open(self.workspace_root.absolute_url() + '/my-invitations/decline',
                         data={'iid': 'someinvalidiid',
                               '_authenticator': createToken()})

    @browsing
    def test_my_invitation_link_personal_action(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.visit()
        self.assertTrue(browser.css('[href$="@@my-invitations"]'))

        self.deactivate_feature('workspace')
        browser.reload()
        self.assertFalse(browser.css('[href$="@@my-invitations"]'))
