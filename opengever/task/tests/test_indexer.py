from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase


class TestTaskIndexers(FunctionalTestCase):

    def setUp(self):
        super(TestTaskIndexers, self).setUp()

        create(Builder('org_unit')
               .with_default_groups()
               .id('org-unit-2')
               .having(title='Org Unit 2', admin_unit=self.admin_unit))

        self.task = create(Builder("task")
                           .titled("Test task 1")
                           .having(task_type='comment'))

    def test_date_of_completion(self):
        self.assertEquals(
            obj2brain(self.task).date_of_completion,
            datetime(1970, 1, 1))

        self.task.date_of_completion = datetime(2012, 2, 2)
        self.task.reindexObject()

        self.assertEquals(
            obj2brain(self.task).date_of_completion,
            datetime(2012, 2, 2))

    def test_is_subtask(self):
        self.subtask = create(Builder("task").within(self.task)
                                             .titled("Test task 1")
                                             .having(task_type='comment'))

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
