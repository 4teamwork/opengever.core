from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import globalnav
from zExceptions import Unauthorized


class TestWorkspaceRoot(IntegrationTestCase):

    @browsing
    def test_can_be_added_as_manager(self, browser):
        self.login(self.manager, browser)
        self.enable_languages()
        browser.open(view='folder_contents')
        factoriesmenu.add('Workspace Root')
        browser.fill({'Title (German)': u'Teamr\xe4ume',
                      'Title (French)': u'Ateliers',
                      'Title (English)': u'Worksp\xe4ces'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals(u'Worksp\xe4ces', plone.first_heading())

    @browsing
    def test_workspace_admin_permissions(self, browser):
        self.login(self.workspace_admin, browser)
        self.assert_root_access(True)
        self.assert_workspace_addable(True)

    @browsing
    def test_workspace_owner_permissions(self, browser):
        self.login(self.workspace_owner, browser)
        self.assert_root_access(True)
        self.assert_workspace_addable(True)

    @browsing
    def test_workspace_member_permissions(self, browser):
        self.login(self.workspace_member, browser)
        self.assert_root_access(True)
        self.assert_workspace_addable(False)

    @browsing
    def test_workspace_guest_permissions(self, browser):
        self.login(self.workspace_guest, browser)
        self.assert_root_access(True)
        self.assert_workspace_addable(False)

    @browsing
    def test_regular_user_permissions(self, browser):
        self.login(self.regular_user, browser)
        self.assert_root_access(False)

    @browsing
    def test_dossier_responsible_permissions(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assert_root_access(False)

    def assert_root_access(self, expect_has_access, browser=default_browser):
        root_id = u'Teamr\xe4ume'
        browser.open()
        if expect_has_access:
            self.assertIn(root_id, globalnav.portaltabs().text)
            browser.open(self.workspace_root)
            self.assertEquals(u'Teamr\xe4ume', plone.first_heading())
        else:
            self.assertNotIn(root_id, globalnav.portaltabs().text)
            with self.assertRaises(Unauthorized):
                self.workspace_root

    def assert_workspace_addable(self, expect_is_addable, browser=default_browser):
        # Requires access to workspace root.
        browser.open(self.workspace_root)
        if expect_is_addable:
            self.assertTrue(factoriesmenu.visible())
            self.assertIn('Workspace', factoriesmenu.addable_types())
        else:
            self.assertFalse(factoriesmenu.visible())
