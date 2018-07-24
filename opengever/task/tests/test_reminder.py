from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.task.activities import TaskReminderActivity
from opengever.task.reminder import TASK_REMINDER_BEGINNING_OF_WEEK
from opengever.task.reminder import TASK_REMINDER_ONE_DAY_BEFORE
from opengever.task.reminder import TASK_REMINDER_ONE_WEEK_BEFORE
from opengever.task.reminder import TASK_REMINDER_SAME_DAY
from opengever.task.reminder.reminder import TaskReminder
from opengever.testing import IntegrationTestCase
import pytz


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


class TestTaskReminder(IntegrationTestCase):

    features = ('activity', )

    def test_set_reminder_creates_annotation_entry_for_current_user(self):
        self.login(self.regular_user)
        task_reminder = TaskReminder()
        task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_DAY_BEFORE)

        self.assertEqual(
            TASK_REMINDER_ONE_DAY_BEFORE.option_type,
            task_reminder.get_reminder(self.task).option_type)

        self.assertIsNone(task_reminder.get_reminder(
            self.task, user_id=self.dossier_responsible.getId()))

    def test_set_reminder_updates_annotations_entry_if_already_exists(self):
        self.login(self.regular_user)
        task_reminder = TaskReminder()
        task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_DAY_BEFORE)
        task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_WEEK_BEFORE)

        self.assertEqual(
            TASK_REMINDER_ONE_WEEK_BEFORE.option_type,
            task_reminder.get_reminder(self.task).option_type)

    def test_set_reminder_creates_sql_entry_for_current_user(self):
        self.login(self.regular_user)
        task_reminder = TaskReminder()
        task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_DAY_BEFORE)

        reminder = task_reminder.get_sql_reminder(self.task)

        self.assertEqual(
            TASK_REMINDER_ONE_DAY_BEFORE.option_type,
            reminder.option_type
            )

        self.assertEqual(
            TASK_REMINDER_ONE_DAY_BEFORE.calculate_remind_on(self.task.deadline),
            reminder.remind_day
            )

        self.assertIsNone(task_reminder.get_sql_reminder(
            self.task, user_id=self.dossier_responsible.getId()))

    def test_set_reminder_updates_sql_entry_if_already_exists(self):
        self.login(self.regular_user)
        task_reminder = TaskReminder()
        task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_DAY_BEFORE)
        task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_WEEK_BEFORE)

        self.assertEqual(
            TASK_REMINDER_ONE_WEEK_BEFORE.option_type,
            task_reminder.get_sql_reminder(self.task).option_type)

    def test_clear_reminder_removes_annotation_reminder_for_current_user(self):
        self.login(self.regular_user)
        task_reminder = TaskReminder()

        task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_DAY_BEFORE)
        task_reminder.set_reminder(
            self.task, TASK_REMINDER_ONE_DAY_BEFORE,
            user_id=self.dossier_responsible.getId())

        task_reminder.clear_reminder(self.task)
        self.assertIsNone(task_reminder.get_reminder(self.task))

        self.assertEqual(
            TASK_REMINDER_ONE_DAY_BEFORE.option_type,
            task_reminder.get_reminder(
                self.task, user_id=self.dossier_responsible.getId()).option_type)

    def test_clear_reminder_removes_sql_reminder_for_current_user(self):
        self.login(self.regular_user)
        task_reminder = TaskReminder()

        task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_DAY_BEFORE)
        task_reminder.set_reminder(
            self.task, TASK_REMINDER_ONE_DAY_BEFORE,
            user_id=self.dossier_responsible.getId())

        task_reminder.clear_reminder(self.task)
        self.assertIsNone(task_reminder.get_sql_reminder(self.task))

        self.assertEqual(
            TASK_REMINDER_ONE_DAY_BEFORE.option_type,
            task_reminder.get_sql_reminder(
                self.task, user_id=self.dossier_responsible.getId()).option_type)

    def test_create_reminder_notifications_does_nothing_if_there_are_no_reminder_settings(self):
        self.login(self.regular_user)

        TaskReminder().create_reminder_notifications()

        self.assertEqual(0, Activity.query.count())
        self.assertEqual(0, Notification.query.count())

    def test_create_reminder_notifications_adds_notifications_for_each_reminder_if_reaching_remind_day(self):
        self.login(self.administrator)
        today = date.today()

        self.task.responsible = self.dossier_responsible.getId()
        self.task.issuer = self.regular_user.getId()
        self.task.deadline = today

        self.subtask.responsible = self.dossier_responsible.getId()
        self.subtask.issuer = self.regular_user.getId()
        self.subtask.deadline = today + timedelta(days=1)

        self.sequential_task.responsible = self.dossier_responsible.getId()
        self.sequential_task.issuer = self.regular_user.getId()
        self.sequential_task.deadline = today + timedelta(days=5)

        task_reminder = TaskReminder()

        with self.login(self.regular_user):
            task_reminder.set_reminder(self.task, TASK_REMINDER_SAME_DAY)
            task_reminder.set_reminder(self.sequential_task, TASK_REMINDER_SAME_DAY)

        with self.login(self.dossier_responsible):
            task_reminder.set_reminder(self.subtask, TASK_REMINDER_ONE_DAY_BEFORE)

        with freeze(pytz.UTC.localize(datetime.combine(today, datetime.min.time()))):
            task_reminder.create_reminder_notifications()

        task_reminder_activities = Activity.query.filter(
            Activity.kind == TaskReminderActivity.kind)

        self.assertEqual(2, task_reminder_activities.count())

        notifications = []
        [notifications.extend(activity.notifications) for activity in task_reminder_activities]

        self.assertEqual(2, len(notifications))
        self.assertItemsEqual(
            [self.regular_user.getId(), self.dossier_responsible.getId()],
            [notification.userid for notification in notifications])
