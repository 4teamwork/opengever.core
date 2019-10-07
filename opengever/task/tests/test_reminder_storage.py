from opengever.task.reminder import ReminderOneWeekBefore
from opengever.task.reminder import ReminderSameDay
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
        self.storage.set(ReminderSameDay())

        self.assertEqual({
            self.regular_user.id: {'option_type': 'same_day', 'params': {}}},
            self.storage._annotation_storage())

    def test_storage_set_for_other_user(self):
        self.login(self.regular_user)
        self.storage.set(ReminderSameDay(),
                         user_id=self.dossier_responsible.id)

        self.assertEqual({
            self.dossier_responsible.id: {'option_type': 'same_day', 'params': {}}},
            self.storage._annotation_storage())

    def test_storage_set_rejects_invalid_option_type(self):
        self.login(self.regular_user)
        with self.assertRaises(AssertionError):
            self.storage.set('unknown_option_type')

    def test_storage_set_only_accepts_bytestring_user_ids(self):
        self.login(self.regular_user)

        with self.assertRaises(AssertionError):
            self.storage.set(ReminderSameDay(),
                             user_id=self.dossier_responsible)

        with self.assertRaises(AssertionError):
            self.storage.set(ReminderSameDay(),
                             user_id=u'unicode')

    def test_storage_get_for_current_user(self):
        self.login(self.regular_user)
        self.storage.set(ReminderSameDay())

        self.assertEqual(ReminderSameDay(),
                         self.storage.get())

    def test_storage_get_for_other_user(self):
        self.login(self.regular_user)
        self.storage.set(ReminderSameDay(),
                         user_id=self.dossier_responsible.id)

        self.assertIsNone(self.storage.get())

        self.assertEqual(ReminderSameDay(),
                         self.storage.get(self.dossier_responsible.id))

    def test_storage_list(self):
        self.login(self.regular_user)
        self.storage.set(ReminderSameDay())
        self.storage.set(ReminderOneWeekBefore(),
                         user_id=self.dossier_responsible.id)

        self.assertEqual({
            self.regular_user.id: ReminderSameDay(),
            self.dossier_responsible.id: ReminderOneWeekBefore()},
            self.storage.list())

    def test_storage_clear_for_current_user(self):
        self.login(self.regular_user)
        self.storage.set(ReminderSameDay())
        self.storage.set(ReminderOneWeekBefore(),
                         user_id=self.dossier_responsible.id)
        self.storage.clear()

        self.assertEqual({
            self.dossier_responsible.id: ReminderOneWeekBefore()},
            self.storage.list())

    def test_storage_clear_for_other_user(self):
        self.login(self.regular_user)
        self.storage.set(ReminderSameDay())
        self.storage.set(ReminderOneWeekBefore(),
                         user_id=self.dossier_responsible.id)
        self.storage.clear(user_id=self.dossier_responsible.id)

        self.assertEqual({
            self.regular_user.id: ReminderSameDay()},
            self.storage.list())
