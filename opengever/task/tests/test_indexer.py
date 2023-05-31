from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.roles import WATCHER_ROLE
from opengever.task.task import ITask
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from plone import api
from plone.app.relationfield.event import update_behavior_relations
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid import IIntIds


class TestTaskIndexers(IntegrationTestCase):

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

    @browsing
    def test_related_items_is_updated_when_forward_relations_are_modified(self, browser):
        self.login(self.administrator, browser)
        api.content.transition(
            obj=self.task, transition='task-transition-in-progress-cancelled')
        api.content.transition(
            obj=self.task, transition='task-transition-cancelled-open')

        self.assertItemsEqual(
            [self.document],
            [rel.to_object for rel in ITask(self.task).relatedItems])
        self.assertItemsEqual(
            [self.document.UID()],
            solr_data_for(self.task, 'related_items'))

        browser.open(self.task, view='edit')
        browser.fill({'Related items': [self.document.absolute_url_path(),
                                        self.subdocument.absolute_url_path()]})
        browser.find('Save').click()

        self.commit_solr()
        self.assertItemsEqual(
            [self.document, self.subdocument],
            [rel.to_object for rel in ITask(self.task).relatedItems])
        self.assertItemsEqual(
            [self.document.UID(), self.subdocument.UID()],
            solr_data_for(self.task, 'related_items'))

    @browsing
    def test_related_items_is_updated_when_related_item_is_deleted(self, browser):
        self.login(self.regular_user, browser)

        self.assertEqual(
            [self.document],
            [rel.to_object for rel in ITask(self.task).relatedItems])
        self.assertEqual([self.document.UID()],
                         solr_data_for(self.task, 'related_items'))

        with self.login(self.manager):
            api.content.delete(self.document)

        self.commit_solr()
        # Deletion is handled in an event handler.
        relations = ITask(self.task).relatedItems
        self.assertEqual(0, len(relations))
        self.assertEqual(None, solr_data_for(self.task, 'related_items'))
