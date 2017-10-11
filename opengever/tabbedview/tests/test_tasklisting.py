from ftw.testbrowser import browsing
from opengever.globalindex.handlers.task import TaskSqlSyncer
from opengever.testing import IntegrationTestCase


class TestTaskListing(IntegrationTestCase):

    @browsing
    def test_shows_only_pending_tasks_by_default(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        browser.open(self.dossier, view='tabbedview_view-tasks')

        table = browser.css('.listing').first
        self.assertEquals([u'Vertragsentwurf \xdcberpr\xfcfen'],
                          [row.get('Title') for row in table.dicts()])

    @browsing
    def test_list_every_dossiers_with_the_all_filter(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        browser.open(self.dossier, view='tabbedview_view-tasks',
                     data={'task_state_filter': 'filter_all'})

        table = browser.css('.listing').first
        self.assertEquals(
            [u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
             u'Vertragsentwurf \xdcberpr\xfcfen'],
            [row.get('Title') for row in table.dicts()])

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
