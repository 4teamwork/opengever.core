from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from opengever.testing import IntegrationTestCase


class TestRepositoryWorkflow(IntegrationTestCase):

    @browsing
    def test_list_folder_contents_on_repofolder_is_not_available_for_adminstrators(self, browser):
        self.login(self.administrator, browser)
        with browser.expect_unauthorized():
            browser.open(self.branch_repofolder, view='folder_contents')

    @browsing
    def test_list_folder_contents_on_repofolder_is_available_for_managers(self, browser):
        self.login(self.manager, browser)
        browser.open(self.branch_repofolder, view='folder_contents')

    @browsing
    def test_list_folder_contents_on_repositoryroot_is_not_available_for_adminstrators(self, browser):
        self.login(self.administrator, browser)
        with browser.expect_unauthorized():
            browser.open(self.repository_root, view='folder_contents')

    @browsing
    def test_list_folder_contents_on_repositoryroot_is_available_for_managers(self, browser):
        self.login(self.manager, browser)
        browser.open(self.repository_root, view='folder_contents')

    @browsing
    def test_repository_excel_export_is_available_for_adminstrators(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.repository_root)
        self.assertNotIn('Export as Excel file', editbar.menu_options("Actions"))
        with browser.expect_unauthorized():
            browser.open(self.repository_root, view="download_excel")

        self.login(self.limited_admin, browser)
        browser.open(self.repository_root)
        self.assertIn('Export as Excel file', editbar.menu_options("Actions"))
        browser.open(self.repository_root, view="download_excel")
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            browser.mimetype)

        self.login(self.administrator, browser)
        browser.open(self.repository_root)
        self.assertIn('Export as Excel file', editbar.menu_options("Actions"))
        browser.open(self.repository_root, view="download_excel")
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            browser.mimetype)

    @browsing
    def test_repository_excel_export_is_available_for_managers(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.repository_root)
        self.assertNotIn('Export as Excel file', editbar.menu_options("Actions"))

        self.login(self.manager, browser)
        browser.open(self.repository_root)
        self.assertIn('Export as Excel file', editbar.menu_options("Actions"))
        browser.open(self.repository_root, view="download_excel")
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            browser.mimetype)
