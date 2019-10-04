from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.activity.dispatcher import NotificationDispatcher
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.activity.roles import TASK_REMINDER_WATCHER_ROLE
from opengever.base.interfaces import IDataCollector
from opengever.task.activities import TaskReminderActivity
from opengever.task.reminder import ReminderBeginningOfWeek
from opengever.task.reminder import ReminderOneDayBefore
from opengever.task.reminder import ReminderOneWeekBefore
from opengever.task.reminder import ReminderSameDay
from opengever.task.reminder.reminder import TaskReminder
from opengever.testing import IntegrationTestCase
from zope.component import getAdapter
import json
import pytz


class TestTaskReminderOptions(IntegrationTestCase):

    def test_calculate_remind_on(self):
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


class TestTaskReminder(IntegrationTestCase):

    features = ('activity', )

    def test_set_reminder_creates_annotation_entry_for_current_user(self):
        self.login(self.regular_user)
        self.task.set_reminder(ReminderOneDayBefore.option_type)

        self.assertEqual(
            ReminderOneDayBefore(),
            self.task.get_reminder())

        self.assertIsNone(self.task.get_reminder(
            user_id=self.dossier_responsible.getId()))

    def test_set_reminder_updates_annotations_entry_if_already_exists(self):
        self.login(self.regular_user)
        self.task.set_reminder(ReminderOneDayBefore.option_type)
        self.task.set_reminder(ReminderOneWeekBefore.option_type)

        self.assertEqual(
            ReminderOneWeekBefore(),
            self.task.get_reminder())

    def test_clear_reminder_removes_annotation_reminder_for_current_user(self):
        self.login(self.regular_user)

        self.task.set_reminder(ReminderOneDayBefore.option_type)
        self.task.set_reminder(
            ReminderOneDayBefore.option_type,
            user_id=self.dossier_responsible.getId())

        self.task.clear_reminder()
        self.assertIsNone(self.task.get_reminder())

        self.assertEqual(
            ReminderOneDayBefore(),
            self.task.get_reminder(
                user_id=self.dossier_responsible.getId()))

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
        self.set_workflow_state('task-state-open', self.subtask)

        self.sequential_task.responsible = self.dossier_responsible.getId()
        self.sequential_task.issuer = self.regular_user.getId()
        self.sequential_task.deadline = today + timedelta(days=5)

        with self.login(self.regular_user):
            self.task.set_reminder(ReminderSameDay.option_type)
            self.task.sync()

            self.sequential_task.set_reminder(ReminderSameDay.option_type)
            self.sequential_task.sync()

        with self.login(self.dossier_responsible):
            self.subtask.set_reminder(ReminderOneDayBefore.option_type)
            self.subtask.sync()

        with freeze(pytz.UTC.localize(datetime.combine(today, datetime.min.time()))):
            TaskReminder().create_reminder_notifications()

        task_reminder_activities = Activity.query.filter(
            Activity.kind == TaskReminderActivity.kind)

        self.assertEqual(2, task_reminder_activities.count())

        notifications = []
        [notifications.extend(activity.notifications) for activity in task_reminder_activities]

        self.assertEqual(2, len(notifications))
        self.assertItemsEqual(
            [self.regular_user.getId(), self.dossier_responsible.getId()],
            [notification.userid for notification in notifications])

    def test_do_not_create_reminder_activity_if_task_is_finished(self):
        self.login(self.administrator)
        today = date.today()

        self.task.responsible = self.dossier_responsible.getId()
        self.task.issuer = self.regular_user.getId()
        self.task.deadline = today

        with self.login(self.regular_user):
            self.task.set_reminder(ReminderSameDay.option_type)
            self.task.sync()

        def create_reminders_for_task_in_state(task, state):
            self.set_workflow_state(state, task)

            with freeze(pytz.UTC.localize(datetime.combine(today, datetime.min.time()))):
                TaskReminder().create_reminder_notifications()

        create_reminders_for_task_in_state(self.task, 'task-state-tested-and-closed')
        create_reminders_for_task_in_state(self.task, 'task-state-resolved')

        task_reminder_activities = Activity.query.filter(
            Activity.kind == TaskReminderActivity.kind)

        self.assertEqual(0, task_reminder_activities.count())

        # Test if it's working at all
        create_reminders_for_task_in_state(self.task, 'task-state-open')

        task_reminder_activities = Activity.query.filter(
            Activity.kind == TaskReminderActivity.kind)

        self.assertEqual(1, task_reminder_activities.count())

    def test_reminder_notifications_respects_user_notification_settings(self):
        self.login(self.administrator)

        # Validate, that the user wants to get badge-notifications for task
        # reminders. This is essential for this test.
        user_settings = NotificationDispatcher().get_setting(
            'task-reminder', self.regular_user.getId())
        self.assertIn(TASK_REMINDER_WATCHER_ROLE,
                      user_settings.badge_notification_roles)

        today = date.today()

        self.task.responsible = self.dossier_responsible.getId()
        self.task.issuer = self.regular_user.getId()
        self.task.deadline = today

        with self.login(self.regular_user):
            self.task.set_reminder(ReminderSameDay.option_type)
            self.task.sync()

        with freeze(pytz.UTC.localize(datetime.combine(today, datetime.min.time()))):
            TaskReminder().create_reminder_notifications()

        notifications = Notification.query.by_user(self.regular_user.getId())
        self.assertEqual(1, notifications.count())

        notification = notifications.first()
        self.assertTrue(notification.is_badge)


class TestTaskReminderSelector(IntegrationTestCase):

    features = ('activity', )

    @browsing
    def test_displayed_on_in_progress_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, view='tabbedview_view-overview')
        self.assertTrue(browser.css('#task-reminder-selector'))

    @browsing
    def test_not_displayed_on_resolved_task(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.expired_task, view='tabbedview_view-overview')
        self.assertFalse(browser.css('#task-reminder-selector'))

    @browsing
    def test_init_state_keys(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(self.task, view='tabbedview_view-overview')
        init_state = self._get_init_state(browser)

        self.assertEqual(
            ['endpoint', 'reminder_options', 'error_msg'],
            init_state.keys())

    @browsing
    def test_init_state_endpoint(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(self.task, view='tabbedview_view-overview')
        init_state = self._get_init_state(browser)

        self.assertEqual(
            init_state.get('endpoint'),
            self.task.absolute_url() + '/@reminder')

    @browsing
    def test_init_state_selected_option(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.visit(self.task, view='tabbedview_view-overview')
        init_state = self._get_init_state(browser)
        selected_option = filter(lambda x: x.get('selected'),
                                 init_state.get('reminder_options'))

        self.assertEqual(1, len(selected_option))
        self.assertEqual(
            'no-reminder',
            selected_option[0].get('option_type'))

        self.task.set_reminder(ReminderOneDayBefore.option_type)
        browser.visit(self.task, view='tabbedview_view-overview')
        init_state = self._get_init_state(browser)
        selected_option = filter(lambda x: x.get('selected'),
                                 init_state.get('reminder_options'))

        self.assertEqual(1, len(selected_option))
        self.assertEqual(
            ReminderOneDayBefore.option_type,
            selected_option[0].get('option_type'))

    def _get_init_state(self, browser):
        return json.loads(
            browser.css('#task-reminder-selector').first.get('data-state'))


class TestTaskReminderTransport(IntegrationTestCase):

    def test_extract_all_task_reminders_for_all_responsible_representatives(self):
        self.login(self.regular_user)

        self.task.set_reminder(
            ReminderOneDayBefore.option_type, user_id=self.regular_user.id)
        self.task.set_reminder(
            ReminderOneDayBefore.option_type, user_id=self.dossier_responsible.id)
        self.task.set_reminder(
            ReminderOneDayBefore.option_type, user_id=self.secretariat_user.id)

        # single user
        collector = getAdapter(self.task, IDataCollector, name='task-reminders')
        self.assertEqual(
            {self.regular_user.id: {
                'option_type': ReminderOneDayBefore.option_type,
                'params': {}}},
            collector.extract())

        # inbox group
        self.task.responsible = 'inbox:fa'
        collector = getAdapter(self.task, IDataCollector, name='task-reminders')
        self.assertEqual(
            {self.secretariat_user.id: {
                'option_type': ReminderOneDayBefore.option_type,
                'params': {}}},
            collector.extract())

    def test_transport_reminders(self):
        self.login(self.regular_user)

        self.task.set_reminder(
            ReminderOneDayBefore.option_type, user_id=self.regular_user.id)

        collector = getAdapter(self.task, IDataCollector, name='task-reminders')
        data = collector.extract()

        self.assertEqual({}, self.subtask.get_reminders())
        collector = getAdapter(self.subtask, IDataCollector, name='task-reminders')
        collector.insert(data)
        self.assertEqual(
            {self.regular_user.id: ReminderOneDayBefore()},
            self.subtask.get_reminders())
