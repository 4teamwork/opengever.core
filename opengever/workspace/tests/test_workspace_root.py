from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase


class TestWorkspaceRoot(IntegrationTestCase):

    @browsing
    def test_can_be_added_as_manager(self, browser):
        self.login(self.manager, browser)
        browser.open(view='folder_contents')
        factoriesmenu.add('WorkspaceRoot')
        browser.fill({'Title (German)': u'Teamr\xe4ume',
                      'Title (French)': u'Ateliers'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals(u'Teamr\xe4ume', plone.first_heading())

    @browsing
    def test_workspaces_user_is_required_to_see_root(self, browser):
        """The role WorkspacesUser is required for accessing the workspaces root.
        """
        with self.login(self.manager):
            workspace_user = create(Builder('user').with_roles('WorkspacesUser'))

        workspace_root_title = 'workspaces'
        with self.login(workspace_user, browser):
            browser.open()
            self.assertIn(workspace_root_title, browser.css('#portal-globalnav li').text)

        with self.login(self.regular_user, browser):
            browser.open()
            self.assertNotIn(workspace_root_title, browser.css('#portal-globalnav li').text)

    @browsing
    def test_workspaces_creator_is_required_to_add_workspaces(self, browser):
        """The role WorkspacesCreator is required for adding new workspaces in the root.
        """
        with self.login(self.manager):
            workspace_user = create(
                Builder('user').named('Workspaces', 'User')
                .with_roles('WorkspacesUser', on=self.workspace_root))
            workspace_creator = create(
                Builder('user').named('Workspaces', 'Creator')
                .with_roles('WorkspacesUser', 'WorkspacesCreator', on=self.workspace_root))

        with self.login(workspace_creator, browser):
            browser.open(self.workspace_root)
            self.assertTrue(factoriesmenu.visible())
            self.assertIn('Workspace', factoriesmenu.addable_types())

        with self.login(workspace_user, browser):
            browser.open(self.workspace_root)
            self.assertFalse(factoriesmenu.visible())
