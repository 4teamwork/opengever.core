from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone.app.testing import SITE_OWNER_NAME


class TestRepositoryWorkflow(IntegrationTestCase):

    @browsing
    def test_list_folder_contents_on_repofolder_is_not_available_for_adminstrators(self, browser):
        self.login(self.administrator, browser)
        with browser.expect_unauthorized():
            browser.open(self.branch_repofolder, view='folder_contents')

    @browsing
    def test_list_folder_contents_on_repofolder_is_available_for_managers(self, browser):
        self.login(SITE_OWNER_NAME, browser)
        browser.open(self.branch_repofolder, view='folder_contents')

    @browsing
    def test_list_folder_contents_on_repositoryroot_is_not_available_for_adminstrators(self, browser):
        self.login(self.administrator, browser)
        with browser.expect_unauthorized():
            browser.open(self.repository_root, view='folder_contents')

    @browsing
    def test_list_folder_contents_on_repositoryroot_is_available_for_managers(self, browser):
        self.login(SITE_OWNER_NAME, browser)
        browser.open(self.repository_root, view='folder_contents')
