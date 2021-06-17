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
