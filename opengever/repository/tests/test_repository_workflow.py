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
        self.assertNotIn('Download Excel', editbar.menu_options("Actions"))

        self.login(self.administrator, browser)
        browser.open(self.repository_root)
        self.assertIn('Download Excel', editbar.menu_options("Actions"))

    @browsing
    def test_repository_excel_export_is_available_for_managers(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.repository_root)
        self.assertNotIn('Download Excel', editbar.menu_options("Actions"))

        self.login(self.manager, browser)
        browser.open(self.repository_root)
        self.assertIn('Download Excel', editbar.menu_options("Actions"))
