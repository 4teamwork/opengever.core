from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import tabbedview


class TestRepositoryFolderTabs(IntegrationTestCase):

    @browsing
    def test_visible_tabs_for_regular_users(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)

        expected_tabs = [
            'Dossiers',
            'Documents',
            'Tasks',
            'Info',
            ]

        self.assertEquals(expected_tabs, tabbedview.tabs().text)

    @browsing
    def test_visible_tabs_for_administrator(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.branch_repofolder)

        expected_tabs = [
            'Dossiers',
            'Documents',
            'Tasks',
            'Info',
            'Protected Objects',
            ]

        self.assertEquals(expected_tabs, tabbedview.tabs().text)

    @browsing
    def test_documents_tab_can_be_disabled_by_feature_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)

        self.assertIn('Documents', tabbedview.tabs().text)

        self.deactivate_feature('repositoryfolder-documents-tab')
        browser.reload()

        self.assertNotIn('Documents', tabbedview.tabs().text)

    @browsing
    def test_tasks_tab_can_be_disabled_by_feature_flag(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)

        self.assertIn('Tasks', tabbedview.tabs().text)

        self.deactivate_feature('repositoryfolder-tasks-tab')
        browser.reload()

        self.assertNotIn('Tasks', tabbedview.tabs().text)


class TestRepositoryFolderDocumentsTab(IntegrationTestCase):

    @browsing
    def test_visible_actions(self, browser):
        # Not all actions of the dossier-tab work on the repositoryfolder-tab.
        # We are testing as Manager so that we can make sure that actions are
        # actually removed on this tab.
        self.login(self.manager, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')

        expected_actions = [
            'Copy Items',
            'Checkout',
            'Cancel',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Move Items',
            ]

        self.assertEquals(expected_actions, tabbedview.minor_actions().text)

        self.assertEquals([], tabbedview.major_actions().text)

    @browsing
    def test_create_proposal_visible_when_meeting_feature_enabled(self, browser):
        self.activate_feature('meeting')
        self.login(self.manager, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')
        self.assertEquals(['Create Proposal'], tabbedview.major_actions().text)

    @browsing
    def test_columns(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')

        expected_column_data = {
            '': '',
            'Checked out by': '',
            'Creation Date': '31.08.2016',
            'Delivery Date': '03.01.2010',
            'Document Author': 'test_user_1_',
            'Document Date': '03.01.2010',
            'Dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            'Modification Date': '31.08.2016',
            'Public Trial': 'unchecked',
            'Receipt Date': '03.01.2010',
            'Reference Number': 'Client1 1.1 / 1 / 12',
            'Sequence Number': '12',
            'Subdossier': '',
            'Title': u'Vertr\xe4gsentwurf',
            }

        self.assertEqual(
            expected_column_data,
            tabbedview.row_for(self.document).dict(),
            )

    @browsing
    def test_dossier_column_linked(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')

        link = tabbedview.cell_for(self.document, 'Dossier').css('a').first

        self.assertEquals(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            link.text,
            )

        link.click()

        self.assertEquals(self.dossier, browser.context)


class TestRepositoryFolderTasksTab(IntegrationTestCase):

    @browsing
    def test_visible_actions(self, browser):
        self.login(self.manager, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Tasks')

        expected_actions = [
            'Export selection',
            'Move Items',
            'Print selection (PDF)',
            ]

        self.assertEquals(expected_actions, tabbedview.minor_actions().text)

        self.assertEquals([], tabbedview.major_actions().text)

    @browsing
    def test_columns(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Tasks')

        expected_column_data = {
            '': '',
            'Date of completion': '',
            'Deadline': 'Nov 1, 2016',
            'Dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            'Issued at': '31.08.2016',
            'Issuer': 'Ziegler Robert (robert.ziegler)',
            'Responsible': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
            'Review state': 'task-state-in-progress',
            'Sequence number': '1',
            'Subdossier': '',
            'Task type': 'For confirmation / correction',
            'Title': u'Vertragsentwurf \xdcberpr\xfcfen',
            }

        self.assertEqual(
            expected_column_data,
            tabbedview.row_for(self.task).dict(),
            )
