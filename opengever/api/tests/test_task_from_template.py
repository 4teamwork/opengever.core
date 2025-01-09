from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.task.task import ITask
from opengever.testing import IntegrationTestCase
from plone import api
from z3c.relationfield.relation import RelationValue
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import json


class TestSequentialTaskPassDocumentsToNextTask(IntegrationTestCase):

    maxDiff = None

    def setUp(self):
        super(TestSequentialTaskPassDocumentsToNextTask, self).setUp()
        self.login(self.secretariat_user)
        self.seq_subtask_1_document = create(
            Builder('document')
            .within(self.seq_subtask_1)
            .titled('Letter to Peter')
        )

        intids = getUtility(IIntIds)
        ITask(self.seq_subtask_1).relatedItems = [
            RelationValue(intids.getId(self.document))]

        self.seq_subtask_1.reindexObject()
        self.assertItemsEqual([self.document, self.seq_subtask_1_document],
                              self.seq_subtask_1.task_documents())
        self.assertItemsEqual([], self.seq_subtask_2.task_documents())

    @browsing
    def test_can_pass_documents_to_next_task_with_open_tested_and_closed_transition(self, browser):
        self.login(self.secretariat_user, browser=browser)

        url = '{}/@workflow/task-transition-open-tested-and-closed'.format(
            self.seq_subtask_1.absolute_url())
        data = {'pass_documents_to_next_task': True}

        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertItemsEqual(
            [self.document, self.seq_subtask_1_document],
            [item.to_object for item in ITask(self.seq_subtask_2).relatedItems])

    @browsing
    def test_can_pass_documents_to_next_task_with_in_progress_tested_and_closed_transition(self, browser):
        self.login(self.secretariat_user, browser=browser)

        api.content.transition(obj=self.seq_subtask_1, transition='task-transition-open-in-progress')

        url = '{}/@workflow/task-transition-in-progress-tested-and-closed'.format(
            self.seq_subtask_1.absolute_url())
        data = {'pass_documents_to_next_task': True}

        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertItemsEqual(
            [self.document, self.seq_subtask_1_document],
            [item.to_object for item in ITask(self.seq_subtask_2).relatedItems])

    @browsing
    def test_can_pass_documents_to_next_task_with_task_transition_open_rejected_transition(self, browser):
        self.login(self.secretariat_user, browser=browser)

        api.content.transition(obj=self.seq_subtask_1, transition='task-transition-open-rejected')

        url = '{}/@workflow/task-transition-rejected-skipped'.format(
            self.seq_subtask_1.absolute_url())
        data = {'pass_documents_to_next_task': True}

        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertItemsEqual(
            [self.document, self.seq_subtask_1_document],
            [item.to_object for item in ITask(self.seq_subtask_2).relatedItems])

    @browsing
    def test_do_not_pass_documents_to_next_task_if_property_is_set_to_false(self, browser):
        self.login(self.secretariat_user, browser=browser)

        ITask(self.seq_subtask_1).task_type = 'correction'
        url = '{}/@workflow/task-transition-open-resolved'.format(
            self.seq_subtask_1.absolute_url())
        data = {'pass_documents_to_next_task': False}

        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertItemsEqual(
            [], [item.to_object for item in ITask(self.seq_subtask_2).relatedItems])
