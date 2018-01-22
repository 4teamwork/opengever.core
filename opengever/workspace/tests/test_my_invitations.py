from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.storage import IInvitationStorage
from zope.component import getUtility


class TestMyInvitationsView(IntegrationTestCase):

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

        self.workspace_root.manage_setLocalRoles(self.regular_user.getId(),
                                                 ['WorkspacesUser'])

    @browsing
    def test_list_invitations_of_logged_in_user(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.workspace_root, view='my-invitations')
        self.assertItemsEqual(
            ['fridolin.hugentobler Second workspace Accept Decline',
             'fridolin.hugentobler A Workspace Accept Decline'],
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
        self.login(self.regular_user, browser=browser)
        foreign_iid = tuple(self.storage.iter_invitions_for_context(
            self.workspace2))[0]['iid']

        with browser.expect_http_error(400):
            browser.open(self.workspace_root.absolute_url() + '/my-invitations/accept',
                         data={'iid': foreign_iid})

    @browsing
    def test_cannot_accept_invalid_invitation(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(503):
            browser.open(self.workspace_root.absolute_url() + '/my-invitations/accept',
                         data={'iid': 'someinvalidiid'})
