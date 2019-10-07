from datetime import date
from opengever.task.reminder import Reminder
from opengever.task.reminder import ReminderBeginningOfWeek
from opengever.task.reminder import ReminderOnDate
from opengever.task.reminder import ReminderOneDayBefore
from opengever.task.reminder import ReminderOneWeekBefore
from opengever.task.reminder import ReminderSameDay
from opengever.task.reminder.model import UnknownField
from opengever.testing import IntegrationTestCase
from zope.schema.interfaces import RequiredMissing
from zope.schema.interfaces import WrongType


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

        self.assertEqual(
            ReminderOnDate({'date': date(2018, 12, 30)}),
            Reminder.create('on_date', {'date': date(2018, 12, 30)}))

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

        self.assertEqual(
            {'option_type': 'on_date',
             'params': {'date': date(2018, 12, 30)}},
            ReminderOnDate({'date': date(2018, 12, 30)}).serialize())

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

        self.assertEqual(
            ReminderOnDate({'date': date(2018, 12, 30)}),
            Reminder.deserialize({'option_type': 'on_date',
                                  'params': {'date': date(2018, 12, 30)}}))

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

        self.assertEqual(
            ReminderOnDate({'date': date(2018, 12, 30)}),
            Reminder.deserialize(
                ReminderOnDate({'date': date(2018, 12, 30)}).serialize()))

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

        self.assertEqual(
            date(2018, 12, 30),
            ReminderOnDate(
                {'date': date(2018, 12, 30)}
            ).calculate_trigger_date(deadline))

    def test_parameter_schema_gets_validated(self):
        with self.assertRaises(WrongType):
            ReminderOnDate({'date': True})

        with self.assertRaises(RequiredMissing):
            ReminderOnDate()

        with self.assertRaises(UnknownField):
            ReminderOnDate({'unexpected': 'param',
                            'date': date(2018, 12, 30)})
