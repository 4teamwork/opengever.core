from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import tabbedview


class TestRepositoryFolderTabs(IntegrationTestCase):

    @browsing
    def test_visible_tabs_for_regular_users(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        self.assertEquals(['Dossiers', 'Documents', 'Info'],
                          tabbedview.tabs().text)

    @browsing
    def test_visible_tabs_for_administrator(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.branch_repofolder)
        self.assertEquals(['Dossiers', 'Documents', 'Info', 'Protected Objects'],
                          tabbedview.tabs().text)

    @browsing
    def test_documents_tab_can_be_disabled_by_feature_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        self.assertIn('Documents', tabbedview.tabs().text)

        self.deactivate_feature('repositoryfolder-documents-tab')
        browser.reload()
        self.assertNotIn('Documents', tabbedview.tabs().text)


class TestRepositoryFolderDocumentsTab(IntegrationTestCase):

    @browsing
    def test_visible_actions(self, browser):
        # Not all actions of the dossier-tab work on the repositoryfolder-tab.
        # We are testing as Manager so that we can make sure that actions are
        # actually removed on this tab.
        self.login(self.manager, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')
        self.assertEquals(
            [
                'Copy Items',
                'Checkout',
                'Cancel',
                'Checkin with comment',
                'Checkin without comment',
                'Export selection',
                'Move Items',
            ],
            tabbedview.minor_actions().text)
        self.assertEquals([], tabbedview.major_actions().text)

    @browsing
    def test_columns(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')
        self.assertEqual(
            {'': '',
             'Checked out by': '',
             'Delivery Date': '03.01.2010',
             'Document Author': 'test_user_1_',
             'Document Date': '03.01.2010',
             'Dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             'Public Trial': 'unchecked',
             'Receipt Date': '03.01.2010',
             'Reference Number': 'Client1 1.1 / 1 / 4',
             'Sequence Number': '4',
             'Subdossier': '',
             'Title': u'Vertr\xe4gsentwurf'},
            tabbedview.row_for(self.document).dict())

    @browsing
    def test_dossier_column_linked(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')
        link = tabbedview.cell_for(self.document, 'Dossier').css('a').first
        self.assertEquals(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung', link.text)
        link.click()
        self.assertEquals(self.dossier, browser.context)
