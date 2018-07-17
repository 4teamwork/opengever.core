from datetime import date
from opengever.task.reminder import TASK_REMINDER_SAME_DAY
from opengever.task.reminder import TASK_REMINDER_ONE_DAY_BEFORE
from opengever.task.reminder import TASK_REMINDER_ONE_WEEK_BEFORE
from opengever.task.reminder import TASK_REMINDER_BEGINNING_OF_WEEK
from opengever.testing import IntegrationTestCase


class TestTaskReminderOptions(IntegrationTestCase):

    def test_calculate_remind_on(self):
        deadline = date(2018, 7, 1)  # 01. July 2018, Sunday
        self.assertEqual(
            date(2018, 7, 1),  # Sunday
            TASK_REMINDER_SAME_DAY.calculate_remind_on(deadline))

        self.assertEqual(
            date(2018, 6, 30),  # Saturday
            TASK_REMINDER_ONE_DAY_BEFORE.calculate_remind_on(deadline))

        self.assertEqual(
            date(2018, 6, 24),  # Sunday
            TASK_REMINDER_ONE_WEEK_BEFORE.calculate_remind_on(deadline))

        self.assertEqual(
            date(2018, 6, 25),  # Monday
            TASK_REMINDER_BEGINNING_OF_WEEK.calculate_remind_on(deadline))

        deadline = date(2018, 7, 2)  # 02. July 2018, Monday
        self.assertEqual(
            date(2018, 7, 2),  # Monday
            TASK_REMINDER_BEGINNING_OF_WEEK.calculate_remind_on(deadline))
