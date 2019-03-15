from ftw.testbrowser import browsing
from opengever.globalindex.handlers.task import TaskSqlSyncer
from opengever.testing import IntegrationTestCase
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab


class TestTaskListing(IntegrationTestCase):

    @browsing
    def test_shows_only_pending_tasks_by_default(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        browser.open(self.dossier, view='tabbedview_view-tasks')
        table = browser.css('.listing').first
        expected_tasks = [
            u'Vertragsentwurf \xdcberpr\xfcfen',
            u'Mitarbeiter Dossier generieren',
            u'Personaleintritt',
            u'Vertragsentw\xfcrfe 2018',
            u'Diskr\xe4te Dinge',
        ]
        self.assertEquals(expected_tasks, [row.get('Title') for row in table.dicts()])

    @browsing
    def test_list_every_dossiers_with_the_all_filter(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        browser.open(self.dossier, view='tabbedview_view-tasks', data={'task_state_filter': 'filter_all'})
        table = browser.css('.listing').first
        expected_tasks = [
            u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
            u'Vertragsentwurf \xdcberpr\xfcfen',
            'Mitarbeiter Dossier generieren',
            'Arbeitsplatz vorbereiten',
            'Personaleintritt',
            'Vorstellungsrunde bei anderen Mitarbeitern',
            u'Vertragsentw\xfcrfe 2018',
            u'Diskr\xe4te Dinge',
        ]
        self.assertEqual(expected_tasks, [row.get('Title') for row in table.dicts()])

    @browsing
    def test_escape_dossier_title_to_prevent_xss(self, browser):
        self.login(self.regular_user, browser=browser)

        self.dossier.title = u'<b>B\xf6ld title</b>'
        TaskSqlSyncer(self.subtask, None).sync()
        TaskSqlSyncer(self.task, None).sync()

        browser.open(self.dossier, view='tabbedview_view-tasks')

        table = browser.css('.listing').first
        second_row_dossier_cell = table.rows[1].css(
            'td:nth-child(10) .maindossierLink').first
        self.assertEquals(
            u'&lt;b&gt;B\xf6ld title&lt;/b&gt;',
            second_row_dossier_cell.innerHTML.strip().strip('\n'))

    @browsing
    def test_responsible_is_linked_and_prefixed_with_icon(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view='tabbedview_view-tasks')

        self.assertEquals(
            u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
            browser.css('.listing').first.dicts()[0].get('Responsible'))

        link = browser.find(u'B\xe4rfuss K\xe4thi (kathi.barfuss)')
        self.assertEquals(
            'http://nohost/plone/@@user-details/kathi.barfuss',
            link.get('href'))
        self.assertEquals('actor-label actor-user', link.get('class'))

    @browsing
    def test_issuer_is_linked_and_prefixed_with_icon(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view='tabbedview_view-tasks')

        self.assertEquals(
            u'Ziegler Robert (robert.ziegler)',
            browser.css('.listing').first.dicts()[0].get('Issuer'))

        link = browser.find(u'Ziegler Robert (robert.ziegler)')
        self.assertEquals(
            'http://nohost/plone/@@user-details/robert.ziegler',
            link.get('href'))
        self.assertEquals('actor-label actor-user', link.get('class'))

    def test_cannot_group_tasks_by_checkbox_column(self):
        expected_column = {'groupable': False}
        checkbox_column = GlobalTaskListingTab.columns[0]
        self.assertDictContainsSubset(expected_column, checkbox_column)
