from datetime import date
from opengever.task.reminder import Reminder
from opengever.task.reminder import ReminderBeginningOfWeek
from opengever.task.reminder import ReminderOneDayBefore
from opengever.task.reminder import ReminderOneWeekBefore
from opengever.task.reminder import ReminderSameDay
from opengever.testing import IntegrationTestCase


class TestTaskReminderTypes(IntegrationTestCase):

    def test_reminders_can_be_created_via_factory_method(self):
        self.assertEqual(
            ReminderSameDay(),
            Reminder.create('same_day'))

        self.assertEqual(
            ReminderOneDayBefore(),
            Reminder.create('one_day_before'))

        self.assertEqual(
            ReminderOneWeekBefore(),
            Reminder.create('one_week_before'))

        self.assertEqual(
            ReminderBeginningOfWeek(),
            Reminder.create('beginning_of_week'))

    def test_reminders_can_be_serialized(self):
        self.assertEqual(
            {'option_type': 'same_day', 'params': {}},
            ReminderSameDay().serialize())

        self.assertEqual(
            {'option_type': 'one_day_before', 'params': {}},
            ReminderOneDayBefore().serialize())

        self.assertEqual(
            {'option_type': 'one_week_before', 'params': {}},
            ReminderOneWeekBefore().serialize())

        self.assertEqual(
            {'option_type': 'beginning_of_week', 'params': {}},
            ReminderBeginningOfWeek().serialize())

    def test_reminders_can_be_deserialized_from_data(self):
        self.assertEqual(
            ReminderSameDay(),
            Reminder.deserialize({'option_type': 'same_day'}))

        self.assertEqual(
            ReminderOneDayBefore(),
            Reminder.deserialize({'option_type': 'one_day_before'}))

        self.assertEqual(
            ReminderOneWeekBefore(),
            Reminder.deserialize({'option_type': 'one_week_before'}))

        self.assertEqual(
            ReminderBeginningOfWeek(),
            Reminder.deserialize({'option_type': 'beginning_of_week'}))

    def test_serialization_deserialization_rountrip(self):
        self.assertEqual(
            ReminderSameDay(),
            Reminder.deserialize(ReminderSameDay().serialize()))

        self.assertEqual(
            ReminderOneDayBefore(),
            Reminder.deserialize(ReminderOneDayBefore().serialize()))

        self.assertEqual(
            ReminderOneWeekBefore(),
            Reminder.deserialize(ReminderOneWeekBefore().serialize()))

        self.assertEqual(
            ReminderBeginningOfWeek(),
            Reminder.deserialize(ReminderBeginningOfWeek().serialize()))

    def test_calculate_trigger_date(self):
        deadline = date(2018, 7, 1)  # 01. July 2018, Sunday
        self.assertEqual(
            date(2018, 7, 1),  # Sunday
            ReminderSameDay().calculate_trigger_date(deadline))

        self.assertEqual(
            date(2018, 6, 30),  # Saturday
            ReminderOneDayBefore().calculate_trigger_date(deadline))

        self.assertEqual(
            date(2018, 6, 24),  # Sunday
            ReminderOneWeekBefore().calculate_trigger_date(deadline))

        self.assertEqual(
            date(2018, 6, 25),  # Monday
            ReminderBeginningOfWeek().calculate_trigger_date(deadline))

        deadline = date(2018, 7, 2)  # 02. July 2018, Monday
        self.assertEqual(
            date(2018, 7, 2),  # Monday
            ReminderBeginningOfWeek().calculate_trigger_date(deadline))
