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

    @browsing
    def test_list_invitations_of_logged_in_user(self, browser):
        self.login(self.workspace_admin, browser=browser)
        workspace2 = create(Builder('workspace')
                            .within(self.workspace_root)
                            .titled(u'Second workspace'))

        self.storage.add_invitation(
            self.workspace, self.regular_user.getId(),
            self.workspace_admin.getId(), 'WorkspaceGuest')

        self.storage.add_invitation(
            workspace2, self.regular_user.getId(),
            self.workspace_admin.getId(), 'WorkspaceGuest')

        self.storage.add_invitation(
            workspace2, self.workspace_guest.getId(),
            self.workspace_admin.getId(), 'WorkspaceGuest')

        self.workspace_root.manage_setLocalRoles(self.regular_user.getId(),
                                                 ['WorkspacesUser'])

        self.login(self.regular_user, browser=browser)
        browser.visit(self.workspace_root, view='my-invitations')

        self.assertItemsEqual(
            ['fridolin.hugentobler Second workspace Accept Decline',
             'fridolin.hugentobler A Workspace Accept Decline'],
            browser.css('table.listing').first.body_rows.text)
