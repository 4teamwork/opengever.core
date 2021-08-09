from datetime import datetime
from ftw.testing import freeze
from opengever.document.approvals import ApprovalStorage
from opengever.document.approvals import IApprovalList
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import create_document_version
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations


class TestApprovalList(IntegrationTestCase):

    def test_approvals_are_persisted_in_document_annotations(self):
        self.login(self.regular_user)

        approvals = IApprovalList(self.document)
        approvals.add(1, self.task)

        storage = IAnnotations(self.document)[ApprovalStorage.ANNOTATIONS_KEY]
        self.assertTrue(isinstance(storage, PersistentList))
        self.assertTrue(isinstance(storage[0], PersistentMapping))

    def test_approvals_data_stored_on_document(self):
        self.login(self.regular_user)

        approvals = IApprovalList(self.document)

        approvals.add(
            0, self.subtask, self.regular_user.id, datetime(2021, 7, 2))
        approvals.add(
            1, self.task, self.administrator.id, datetime(2021, 8, 2))

        self.assertEqual(
            [{'task_uid': IUUID(self.subtask),
              'approver': self.regular_user.id,
              'approved': datetime(2021, 7, 2),
              'version_id': 0},
             {'task_uid': IUUID(self.task),
              'approver': self.administrator.id,
              'approved': datetime(2021, 8, 2),
              'version_id': 1}],
            IApprovalList(self.document).storage.list())

    def test_current_user_is_default_approver(self):
        self.login(self.regular_user)

        approvals = IApprovalList(self.document)
        approvals.add(1, self.task)

        self.assertEqual(self.regular_user.id, approvals.get()[0].approver)

    def test_current_datetime_is_default_approval_time(self):
        self.login(self.regular_user)

        with freeze(datetime(2016, 8, 12)):
            approvals = IApprovalList(self.document)
            approvals.add(1, self.task)

            self.assertEqual(datetime(2016, 8, 12), approvals.get()[0].approved)

    def test_cleanup_when_copying_a_document(self):
        self.login(self.regular_user)

        create_document_version(self.document, version_id=0)
        create_document_version(self.document, version_id=1)
        create_document_version(self.document, version_id=2)

        approvals = IApprovalList(self.document)
        approvals.add(0, self.sequential_task, approved=datetime(2021, 7, 2))
        approvals.add(1, self.sequential_task, approved=datetime(2021, 7, 2))
        approvals.add(2, self.task, approved=datetime(2021, 7, 2))
        approvals.add(2, self.subtask, approved=datetime(2021, 7, 2))

        self.assertEqual(4, len(approvals.get()))

        copy = api.content.copy(self.document, target=self.subdossier)

        self.assertEqual(2, len(IApprovalList(copy).get()))
        self.assertEqual(
            [{'task_uid': IUUID(self.task),
              'approver': self.regular_user.id,
              'approved': datetime(2021, 7, 2),
              'version_id': 0},
             {'task_uid': IUUID(self.subtask),
              'approver': self.regular_user.id,
              'approved': datetime(2021, 7, 2),
              'version_id': 0}],
            IApprovalList(copy).storage.list())

    def test_handling_with_documents_without_a_version(self):
        self.login(self.regular_user)

        self.assertFalse(Versioner(self.document).has_initial_version())

        with freeze(datetime(2016, 8, 12)):
            approvals = IApprovalList(self.document)
            approvals.add(0, self.task, self.regular_user.id)

        approvals = IApprovalList(self.document).get()
        self.assertEqual(1, len(approvals))
        self.assertEqual(0, approvals[0].version_id)

        copy = api.content.copy(self.document, target=self.subdossier)

        self.assertEqual(
            [{'task_uid': IUUID(self.task),
              'approver': self.regular_user.id,
              'approved': datetime(2016, 8, 12),
              'version_id': 0}],
            IApprovalList(copy).storage.list())
