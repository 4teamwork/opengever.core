from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrasher


class TestWorkspaceFolderSerializer(IntegrationTestCase):

    @browsing
    def test_workspace_folder_serialization_contains_trashed(self, browser):
        self.login(self.workspace_member, browser=browser)

        browser.open(self.workspace_folder, method="GET", headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertIn("trashed", browser.json)
        self.assertFalse(browser.json["trashed"])

        ITrasher(self.workspace_folder).trash()
        browser.open(self.workspace_folder, method="GET", headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertIn("trashed", browser.json)
        self.assertTrue(browser.json["trashed"])

    @browsing
    def test_workspace_folder_serialization_contains_email(self, browser):
        self.login(self.workspace_member, browser)
        browser.open(self.workspace_folder, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'1018033300@example.org', browser.json['email'])

    @browsing
    def test_workspace_folder_serialization_contains_can_access_members(self, browser):
        self.login(self.workspace_guest, browser)
        browser.open(self.workspace_folder, headers=self.api_headers)
        self.assertTrue(browser.json['can_access_members'])

        with self.login(self.workspace_admin, browser):
            self.workspace.hide_members_for_guests = True

        browser.open(self.workspace_folder, headers=self.api_headers)
        self.assertFalse(browser.json['can_access_members'])
