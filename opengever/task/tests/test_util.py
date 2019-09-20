from ftw.testing import MockTestCase
from opengever.base.response import IResponseContainer
from opengever.task.util import change_task_workflow_state
from opengever.task.util import get_documents_of_task
from opengever.testing import IntegrationTestCase
from plone import api


class TestGetDocumentsOfTask(MockTestCase):

    def setUp(self):
        super(TestGetDocumentsOfTask, self).setUp()
        self.catalog = self.stub()
        self.mock_tool(self.catalog, 'portal_catalog')

        self.membership = self.stub()
        self.mock_tool(self.membership, 'portal_membership')

    def _stub_catalog_obj(self):
        obj = self.stub()
        brain = self.stub()
        self.expect(brain.getObject()).result(obj)
        return brain, obj

    def _stub_related_obj(self, portal_type, allowed=True):
        obj = self.stub()
        rel = self.stub()
        self.expect(rel.to_object).result(obj)
        self.expect(obj.portal_type).result(portal_type)

        self.expect(self.membership.checkPermission(
                'View', obj)).result(allowed)
        return rel, obj

    def test_without_mails_is_default(self):
        task = self.mocker.mock()
        self.expect(task.getPhysicalPath()).result(
            ['', 'path', 'to', 'task'])

        rel1, obj1 = self._stub_related_obj('opengever.document.document')
        rel2, obj2 = self._stub_related_obj('opengever.document.document',
                                            allowed=False)
        rel3, obj3 = self._stub_related_obj('ftw.mail.mail')
        rel4, obj4 = self._stub_related_obj('Folder')
        self.expect(task.relatedItems).result([rel1, rel2, rel3, rel4])

        docbrain1, doc1 = self._stub_catalog_obj()
        expected_query = {'path': '/path/to/task',
                          'portal_type': ['opengever.document.document']}
        self.expect(self.catalog(expected_query)).result([docbrain1])

        self.replay()

        self.assertEqual(get_documents_of_task(task),
                         [doc1, obj1])

    def test_with_mails(self):
        task = self.mocker.mock()
        self.expect(task.getPhysicalPath()).result(
            ['', 'path', 'to', 'task'])

        rel1, obj1 = self._stub_related_obj('opengever.document.document')
        rel2, obj2 = self._stub_related_obj('opengever.document.document',
                                            allowed=False)
        rel3, obj3 = self._stub_related_obj('ftw.mail.mail')
        rel4, obj4 = self._stub_related_obj('Folder')
        self.expect(task.relatedItems).result([rel1, rel2, rel3, rel4])

        docbrain1, doc1 = self._stub_catalog_obj()
        mailbrain1, mail1 = self._stub_catalog_obj()
        expected_query = {'path': '/path/to/task',
                          'portal_type': ['opengever.document.document',
                                          'ftw.mail.mail']}
        self.expect(self.catalog(expected_query)).result(
            [docbrain1, mailbrain1])

        self.replay()

        self.assertEqual(get_documents_of_task(task, include_mails=True),
                         [doc1, mail1, obj1, obj3])


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
