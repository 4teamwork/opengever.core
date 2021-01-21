from opengever.testing import SolrIntegrationTestCase
from ftw.testbrowser import browsing


class TestTaskTree(SolrIntegrationTestCase):

    @browsing
    def test_get_tasktree_for_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.task, view="@tasktree", method="GET", headers=self.api_headers)
        self.assertEqual(
            browser.json['children'],
            [
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1',
                    u'@type': u'opengever.task.task',
                    u'children': [
                        {
                            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1/task-2',
                            u'@type': u'opengever.task.task',
                            u'children': [],
                            u'review_state': u'task-state-resolved',
                            u'title': u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
                        },
                    ],
                    u'review_state': u'task-state-in-progress',
                    u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
                },
            ]
        )
        self.assertEqual(True, browser.json['is_task_addable_in_main_task'])

    @browsing
    def test_is_task_addable_in_main_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.seq_subtask_2, view="@tasktree", method="GET", headers=self.api_headers)
        self.assertTrue(browser.json['is_task_addable_in_main_task'])

        self.set_workflow_state('task-state-resolved', self.sequential_task)
        browser.open(self.seq_subtask_2, view="@tasktree", method="GET", headers=self.api_headers)
        self.assertFalse(browser.json['is_task_addable_in_main_task'])

    @browsing
    def test_is_task_addable_before(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.sequential_task, view="@tasktree", method="GET", headers=self.api_headers)
        self.assertFalse(browser.json['children'][0]['children'][0]['is_task_addable_before'])
        self.assertTrue(browser.json['children'][0]['children'][1]['is_task_addable_before'])

    @browsing
    def test_sequential_tasks_are_sorted_on_obj_position_in_parent(self, browser):
        self.login(self.regular_user, browser=browser)
        subtasks = [self.seq_subtask_3, self.seq_subtask_1, self.seq_subtask_2]
        self.sequential_task.set_tasktemplate_order(subtasks)
        self.commit_solr()

        browser.open(self.sequential_task, view='@tasktree', method='GET', headers=self.api_headers)
        self.assertEqual(
            [self.seq_subtask_3.absolute_url(),
             self.seq_subtask_1.absolute_url(),
             self.seq_subtask_2.absolute_url()],
            [item['@id'] for item in browser.json['children'][0]['children']])

    @browsing
    def test_get_task_with_tasktree_expansion(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(
            self.task, view="?expand=tasktree", method="GET",
            headers=self.api_headers)
        self.assertIn('tasktree', browser.json['@components'])
        self.assertEqual(
            browser.json['@components']['tasktree']['children'],
            [
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1',
                    u'@type': u'opengever.task.task',
                    u'children': [
                        {
                            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1/task-2',
                            u'@type': u'opengever.task.task',
                            u'children': [],
                            u'review_state': u'task-state-resolved',
                            u'title': u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
                        },
                    ],
                    u'review_state': u'task-state-in-progress',
                    u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
                },
            ]
        )
