from datetime import datetime
from plone.uuid.interfaces import IUUID
from opengever.document.approvals import ApprovalStorage
from opengever.document.approvals import IApprovalList
from opengever.testing import IntegrationTestCase
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation import IAnnotations
from ftw.testing import freeze


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
