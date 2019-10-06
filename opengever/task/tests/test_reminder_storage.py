from opengever.task.reminder import TASK_REMINDER_ONE_WEEK_BEFORE
from opengever.task.reminder import TASK_REMINDER_SAME_DAY
from opengever.task.reminder.interfaces import IReminderStorage
from opengever.task.reminder.storage import ReminderAnnotationStorage
from opengever.testing import IntegrationTestCase
from zope.interface.verify import verifyClass


class TestTaskReminderStorage(IntegrationTestCase):

    features = ('activity', )

    def test_storage_implements_interface(self):
        verifyClass(IReminderStorage, ReminderAnnotationStorage)

    @property
    def storage(self):
        return IReminderStorage(self.task)

    def test_storage_set_for_current_user(self):
        self.login(self.regular_user)
        self.storage.set(TASK_REMINDER_SAME_DAY.option_type)

        self.assertEqual({self.regular_user.id: {'option_type': 'same_day'}},
                         self.storage.list())

    def test_storage_set_for_other_user(self):
        self.login(self.regular_user)
        self.storage.set(TASK_REMINDER_SAME_DAY.option_type,
                         user_id=self.dossier_responsible.id)

        self.assertEqual({self.dossier_responsible.id: {'option_type': 'same_day'}},
                         self.storage.list())

    def test_storage_set_rejects_invalid_option_type(self):
        self.login(self.regular_user)
        with self.assertRaises(AssertionError):
            self.storage.set('unknown_option_type')

    def test_storage_set_only_accepts_bytestring_user_ids(self):
        self.login(self.regular_user)

        with self.assertRaises(AssertionError):
            self.storage.set(TASK_REMINDER_SAME_DAY.option_type,
                             user_id=self.dossier_responsible)

        with self.assertRaises(AssertionError):
            self.storage.set(TASK_REMINDER_SAME_DAY.option_type,
                             user_id=u'unicode')

    def test_storage_get_for_current_user(self):
        self.login(self.regular_user)
        self.storage.set(TASK_REMINDER_SAME_DAY.option_type)

        self.assertEqual({'option_type': 'same_day'},
                         self.storage.get())

    def test_storage_get_for_other_user(self):
        self.login(self.regular_user)
        self.storage.set(TASK_REMINDER_SAME_DAY.option_type,
                         user_id=self.dossier_responsible.id)

        self.assertIsNone(self.storage.get())

        self.assertEqual({'option_type': 'same_day'},
                         self.storage.get(self.dossier_responsible.id))

    def test_storage_list(self):
        self.login(self.regular_user)
        self.storage.set(TASK_REMINDER_SAME_DAY.option_type)
        self.storage.set(TASK_REMINDER_ONE_WEEK_BEFORE.option_type,
                         user_id=self.dossier_responsible.id)

        self.assertEqual({
            self.regular_user.id: {'option_type': 'same_day'},
            self.dossier_responsible.id: {'option_type': 'one_week_before'}},
            self.storage.list())

    def test_storage_clear_for_current_user(self):
        self.login(self.regular_user)
        self.storage.set(TASK_REMINDER_SAME_DAY.option_type)
        self.storage.set(TASK_REMINDER_ONE_WEEK_BEFORE.option_type,
                         user_id=self.dossier_responsible.id)
        self.storage.clear()

        self.assertEqual({
            self.dossier_responsible.id: {'option_type': 'one_week_before'}},
            self.storage.list())

    def test_storage_clear_for_other_user(self):
        self.login(self.regular_user)
        self.storage.set(TASK_REMINDER_SAME_DAY.option_type)
        self.storage.set(TASK_REMINDER_ONE_WEEK_BEFORE.option_type,
                         user_id=self.dossier_responsible.id)
        self.storage.clear(user_id=self.dossier_responsible.id)

        self.assertEqual({
            self.regular_user.id: {'option_type': 'same_day'}},
            self.storage.list())
