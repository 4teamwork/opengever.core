from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import tabbedview


class TestRepositoryFolderTabs(IntegrationTestCase):

    @browsing
    def test_visible_tabs_for_regular_users(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        self.assertEquals(['Dossiers', 'Info'],
                          tabbedview.tabs().text)

    @browsing
    def test_visible_tabs_for_administrator(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.branch_repofolder)
        self.assertEquals(['Dossiers', 'Info', 'Protected Objects'],
                          tabbedview.tabs().text)
