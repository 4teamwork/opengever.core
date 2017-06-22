from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestTaskListing(FunctionalTestCase):

    def setUp(self):
        super(TestTaskListing, self).setUp()

        self.dossier = create(Builder('dossier')
                              .titled(u'<b>Bold title</b>'))
        self.task1 = create(Builder('task')
                            .within(self.dossier)
                            .in_state('task-state-open')
                            .titled('Task 1'))
        self.task2 = create(Builder('task')
                            .within(self.dossier)
                            .in_state('task-state-tested-and-closed')
                            .titled('Task 2'))
        self.task3 = create(Builder('task')
                            .within(self.dossier)
                            .in_state('task-state-in-progress')
                            .titled('Task 3'))

    @browsing
    def test_shows_only_pending_tasks_by_default(self, browser):
        browser.login().open(
            self.dossier, view='tabbedview_view-tasks')

        table = browser.css('.listing').first
        self.assertEquals(['Task 1', 'Task 3'],
                          [row.get('Title') for row in table.dicts()])

    @browsing
    def test_list_every_dossiers_with_the_all_filter(self, browser):
        browser.login().open(
            self.dossier, view='tabbedview_view-tasks',
            data={'task_state_filter': 'filter_all'})

        table = browser.css('.listing').first
        self.assertEquals(['Task 1', 'Task 2', 'Task 3'],
                          [row.get('Title') for row in table.dicts()])

    @browsing
    def test_escape_dossier_title_to_prevent_xss(self, browser):
        browser.login().open(
            self.dossier, view='tabbedview_view-tasks')
        table = browser.css('.listing').first
        second_row_dossier_cell = table.rows[1].css('td:nth-child(10) .maindossierLink').first
        self.assertEquals(
            '&lt;b&gt;Bold title&lt;/b&gt;',
            second_row_dossier_cell.innerHTML.strip().strip('\n'))
