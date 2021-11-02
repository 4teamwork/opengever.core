from datetime import datetime
from opengever.activity import notification_center
from opengever.activity.roles import WATCHER_ROLE
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase


class TestTaskIndexers(IntegrationTestCase):

    def test_date_of_completion(self):
        self.login(self.regular_user)

        self.assertEquals(
            datetime(1970, 1, 1),
            obj2brain(self.subtask).date_of_completion)

        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.subtask.date_of_completion = datetime(2021, 11, 3, 12, 3)
        self.subtask.reindexObject()

        self.assertEquals(
            datetime(2021, 11, 3, 12, 3),
            obj2brain(self.subtask).date_of_completion)

    def test_is_subtask(self):
        self.login(self.regular_user)

        self.assertFalse(obj2brain(self.task).is_subtask)
        self.assertTrue(obj2brain(self.subtask).is_subtask)


class TestTaskSolrIndexer(SolrIntegrationTestCase):

    def test_searchable_text(self):
        self.login(self.regular_user)

        self.task.title = u'Test Aufgabe'
        self.task.text = u'Lorem ipsum'
        self.task.task_type = u'comment'
        self.task.responsible = self.regular_user.getId()

        self.task.reindexObject()
        self.commit_solr()

        indexed_value = solr_data_for(self.task, 'SearchableText')

        self.assertIn(u'Test Aufgabe', indexed_value)
        self.assertIn(u'comment', indexed_value)
        self.assertIn(u'B\xe4rfuss K\xe4thi (kathi.barfuss)', indexed_value)

    def test_task_watchers_are_indexed_in_solr(self):
        self.activate_feature('activity')
        self.login(self.regular_user)

        center = notification_center()
        center.add_watcher_to_resource(
            self.task, self.regular_user.getId(), WATCHER_ROLE)
        self.commit_solr()

        indexed_value = solr_data_for(self.task, 'watchers')
        self.assertEqual([self.regular_user.getId()], indexed_value)

    def test_is_completed_indexer(self):
        self.login(self.regular_user)

        self.assertFalse(solr_data_for(self.task, 'is_completed'))

        # closed
        self.set_workflow_state('task-state-tested-and-closed', self.task)
        self.task.reindexObject()
        self.commit_solr()
        self.assertTrue(solr_data_for(self.task, 'is_completed'))

        # cancelled
        self.set_workflow_state('task-state-cancelled', self.task)
        self.task.reindexObject()
        self.commit_solr()
        self.assertTrue(solr_data_for(self.task, 'is_completed'))

        # skipped
        self.set_workflow_state('task-state-skipped', self.task)
        self.task.reindexObject()
        self.commit_solr()
        self.assertTrue(solr_data_for(self.task, 'is_completed'))
