from ftw.testbrowser import browsing
from opengever.task.reminder import ReminderOneDayBefore
from opengever.task.reminder.reminder import TaskReminder
from opengever.testing import IntegrationTestCase


class TestAcceptTaskWorkflowTransitionView(IntegrationTestCase):

    @browsing
    def test_reminders_of_responsbile_gets_cleared(self, browser):
        self.login(self.regular_user, browser)

        task_reminder = TaskReminder()
        task_reminder.set_reminder(
            self.seq_subtask_1, ReminderOneDayBefore(),
            user_id=self.regular_user.id)

        self.assertEqual(
            [self.regular_user.id],
            TaskReminder().get_reminders(self.seq_subtask_1).keys())

        browser.open(self.seq_subtask_1, view='accept_task_workflow_transition')

        self.assertEqual('OK', browser.contents)
        self.assertEqual(
            {},
            TaskReminder().get_reminders(self.seq_subtask_1))
