from ftw.testbrowser import browsing
from opengever.task.reminder import ReminderOneDayBefore
from opengever.testing import IntegrationTestCase


class TestAcceptTaskWorkflowTransitionView(IntegrationTestCase):

    @browsing
    def test_reminders_of_responsbile_gets_cleared(self, browser):
        self.login(self.regular_user, browser)

        self.seq_subtask_1.set_reminder(
            ReminderOneDayBefore(),
            user_id=self.regular_user.id)

        self.assertEqual(
            [self.regular_user.id],
            self.seq_subtask_1.get_reminders().keys())

        browser.open(self.seq_subtask_1, view='accept_task_workflow_transition')

        self.assertEqual('OK', browser.contents)
        self.assertEqual(
            {},
            self.seq_subtask_1.get_reminders())
