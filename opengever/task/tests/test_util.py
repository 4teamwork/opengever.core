from opengever.base.response import IResponseContainer
from opengever.task.util import change_task_workflow_state
from opengever.task.util import get_documents_of_task
from opengever.testing import IntegrationTestCase
from plone import api


class TestGetDocumentsOfTask(IntegrationTestCase):

    def test_without_mails_is_default(self):
        self.login(self.regular_user)
        self.set_related_items(
            self.task,
            [self.document, self.mail_eml, self.mail_msg])

        self.assertItemsEqual([self.document, self.taskdocument],
                              get_documents_of_task(self.task))

    def test_with_mails(self):
        self.login(self.regular_user)
        self.set_related_items(
            self.task,
            [self.document, self.mail_eml, self.mail_msg])

        self.assertItemsEqual(
            [self.document, self.taskdocument, self.mail_eml, self.mail_msg],
            get_documents_of_task(self.task, include_mails=True))


class TestChangeTaskWorklowState(IntegrationTestCase):

    def test_adds_corresponding_answer(self):
        self.login(self.dossier_responsible)
        change_task_workflow_state(
            self.subtask, 'task-transition-resolved-tested-and-closed')

        self.assertEqual('task-transition-resolved-tested-and-closed',
                         IResponseContainer(self.subtask).list()[-1].transition)

    def test_changes_workflow_state(self):
        self.login(self.dossier_responsible)
        change_task_workflow_state(
            self.subtask, 'task-transition-resolved-tested-and-closed')

        self.assertEqual('task-state-tested-and-closed',
                         api.content.get_state(self.subtask))

    def test_state_change_is_synced_to_globalindex(self):
        self.login(self.dossier_responsible)
        change_task_workflow_state(
            self.subtask, 'task-transition-resolved-tested-and-closed')

        self.assertEqual('task-state-tested-and-closed',
                         self.subtask.get_sql_object().review_state)
