from ftw.testbrowser import browsing
from opengever.repository.interfaces import IRepositoryFolderRecords
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from opengever.testing.pages import tabbedview
from plone import api


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
            'Protected objects',
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


class TestRepositoryFolderDocumentsTab(SolrIntegrationTestCase):

    @browsing
    def test_visible_actions(self, browser):
        # Not all actions of the dossier-tab work on the repositoryfolder-tab.
        # We are testing as Manager so that we can make sure that actions are
        # actually removed on this tab.
        self.login(self.manager, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')

        expected_actions = [
            'Copy items',
            'Attach to email',
            'Check out',
            'Cancel',
            'Check in with comment',
            'Check in without comment',
            'Export selection',
            'Move items',
            ]

        self.assertEquals(expected_actions, tabbedview.minor_actions().text)

        self.assertEquals([], tabbedview.major_actions().text)

    @browsing
    def test_create_proposal_action_not_visible(self, browser):
        self.activate_feature('meeting')
        self.login(self.manager, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')
        self.assertEquals([], tabbedview.major_actions().text)

    @browsing
    def test_columns(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Documents')

        expected_column_data = {
            '': '',
            'Checked out by': '',
            'Creation date': '31.08.2016',
            'Sent date': '03.01.2010',
            'Author': 'test_user_1_',
            'Document date': '03.01.2010',
            'Dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            'File extension': '.docx',
            'Keywords': 'Wichtig',
            'Modification date': '31.08.2016',
            'Disclosure status': 'not assessed',
            'Received date': '03.01.2010',
            'Reference number': 'Client1 1.1 / 1 / 14',
            'Sequence number': '14',
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
            'Move items',
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
            'Completion date': '',
            'Deadline': 'Nov 1, 2016',
            'Dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            'Issued on': '31.08.2016',
            'Issuer': 'Ziegler Robert (robert.ziegler)',
            'Organisational Unit': u'Finanz\xe4mt',
            'Responsible': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
            'State': 'In progress',
            'Sequence number': '1',
            'Subdossier': '',
            'Task type': 'For your review',
            'Title': u'Vertragsentwurf \xdcberpr\xfcfen',
            }

        self.assertEqual(
            expected_column_data,
            tabbedview.row_for(self.task).dict(),
            )


class TestRepositoryFolderProposalsTabWithoutMeeting(IntegrationTestCase):

    @browsing
    def test_not_visible(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        expected_tabs = ['Dossiers', 'Documents', 'Tasks', 'Info']
        self.assertEqual(tabbedview.tabs().text, expected_tabs)


class TestRepositoryFolderProposalsTabDisabled(IntegrationTestCase):

    features = (
        'meeting',
        )

    @browsing
    def test_not_visible(self, browser):
        api.portal.set_registry_record('show_proposals_tab', False, IRepositoryFolderRecords)
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        expected_tabs = ['Dossiers', 'Documents', 'Tasks', 'Info']
        self.assertEqual(tabbedview.tabs().text, expected_tabs)


class TestRepositoryFolderProposalsTabWithMeeting(IntegrationTestCase):

    features = (
        'meeting',
        )

    @browsing
    def test_visible(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        expected_tabs = ['Dossiers', 'Documents', 'Tasks', 'Info', 'Proposals']
        self.assertEqual(tabbedview.tabs().text, expected_tabs)

    @browsing
    def test_visible_actions(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Proposals')
        self.assertEquals([], tabbedview.minor_actions().text)
        self.assertEquals([], tabbedview.major_actions().text)

    @browsing
    def test_columns(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        tabbedview.open('Proposals')
        # XXX - Should eventually figure out how to amend the columns helper for this
        expected_rows = [
            ['Decision number', 'Title', 'Description', 'State', 'Committee', 'Meeting', 'Date of submission', 'Issuer'],
            ['', u'Vertr\xe4ge', u'F\xfcr weitere Bearbeitung bewilligen', 'Submitted', 'Submitted', u'Rechnungspr\xfcfungskommission', '', '31.08.2016', 'Ziegler Robert (robert.ziegler)'],  # noqa
            ['', u'Antrag f\xfcr Kreiselbau', '', 'Pending', 'Pending', u'Kommission f\xfcr Verkehr', '', '', 'Ziegler Robert (robert.ziegler)'],  # noqa
        ]
        self.assertEqual(expected_rows, [row.css('td,span').text for row in browser.css('.listing tr')])


class TestRepositoryFolderProposalsTab(IntegrationTestCase):

    @browsing
    def test_not_visible(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        expected_tabs = ['Dossiers', 'Documents', 'Tasks', 'Info']
        self.assertEqual(tabbedview.tabs().text, expected_tabs)

    @browsing
    def test_not_visible_no_feature_enabled(self, browser):
        api.portal.set_registry_record('show_proposals_tab', False, IRepositoryFolderRecords)
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        expected_tabs = ['Dossiers', 'Documents', 'Tasks', 'Info']
        self.assertEqual(tabbedview.tabs().text, expected_tabs)

    @browsing
    def test_not_visible_when_deactivating_ris_and_deactivating_meeting(self, browser):
        self.deactivate_feature('ris')
        self.deactivate_feature('meeting')
        api.portal.set_registry_record('show_proposals_tab', True, IRepositoryFolderRecords)
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        expected_tabs = ['Dossiers', 'Documents', 'Tasks', 'Info', ]
        self.assertEqual(tabbedview.tabs().text, expected_tabs)

    @browsing
    def test_visible_when_activating_ris_and_deactivating_meeting(self, browser):
        self.activate_feature('ris')
        self.deactivate_feature('meeting')

        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        expected_tabs = ['Dossiers', 'Documents', 'Tasks', 'Info', 'Proposals']
        self.assertEqual(tabbedview.tabs().text, expected_tabs)
