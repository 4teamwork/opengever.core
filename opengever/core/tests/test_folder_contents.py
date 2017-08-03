from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone.app.testing import setRoles


class TestFolderContents(IntegrationTestCase):

    @browsing
    def test_manager_can_sort_portal_root(self, browser):
        self.login(self.manager, browser)
        browser.visit(view='@@folder_contents')
        self.assertTrue(browser.css('#foldercontents-order-column'),
                        'Expect the order column as manager on plone root')

    @browsing
    def test_others_cannot_sort_on_portal_root(self, browser):
        setRoles(self.portal, self.administrator.getId(),
                 ['Administrator', 'Reviewer', 'Editor', 'Contributor'])
        self.login(self.administrator, browser)

        with browser.expect_unauthorized():
            browser.visit(view='@@folder_contents')
