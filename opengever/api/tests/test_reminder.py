from ftw.testbrowser import restapi
from opengever.api.reminder import error_msgs
from opengever.task.reminder import TASK_REMINDER_ONE_DAY_BEFORE
from opengever.task.reminder import TASK_REMINDER_ONE_WEEK_BEFORE
from opengever.task.reminder.reminder import TaskReminder
from opengever.testing import IntegrationTestCase


class TestTaskReminderAPI(IntegrationTestCase):

    def setUp(self):
        super(TestTaskReminderAPI, self).setUp()
        self.task_reminder = TaskReminder()

    @restapi
    def test_post_adds_task_reminder(self, api_client):
        self.login(self.regular_user, api_client)
        payload = {'option_type': TASK_REMINDER_ONE_DAY_BEFORE.option_type}
        self.assertIsNone(self.task_reminder.get_reminder(self.task))

        api_client.open(self.task, endpoint='@reminder', data=payload)
        self.assertEqual(204, api_client.status_code)
        self.assertEqual(
            TASK_REMINDER_ONE_DAY_BEFORE.option_type,
            self.task_reminder.get_reminder(self.task).option_type,
        )

    @restapi
    def test_post_raises_when_option_type_is_missing(self, api_client):
        self.login(self.regular_user, api_client)
        payload = {}

        with api_client.expect_http_error(400):
            api_client.open(self.task, endpoint='@reminder', data=payload)

        expected_error = {
            "message": error_msgs.get('missing_option_type'),
            "type": "BadRequest",
        }
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_post_raises_409_when_adding_already_set_reminder(self, api_client):
        self.login(self.regular_user, api_client)
        self.task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_DAY_BEFORE)
        payload = {'option_type': TASK_REMINDER_ONE_WEEK_BEFORE.option_type}

        with api_client.expect_http_error(409):
            api_client.open(self.task, endpoint='@reminder', data=payload)

        self.assertEqual(
            TASK_REMINDER_ONE_DAY_BEFORE.option_type,
            self.task_reminder.get_reminder(self.task).option_type,
        )

    @restapi
    def test_post_shows_possible_reminder_options_if_option_does_not_exists(self, api_client):
        self.login(self.regular_user, api_client)
        payload = {'option_type': 'not_existing_option_type'}
        with api_client.expect_http_error(400):
            api_client.open(self.task, endpoint='@reminder', data=payload)

        expected_error = {
            "message": error_msgs.get('non_existing_option_type'),
            "type": "BadRequest",
        }
        self.assertEqual(expected_error, api_client.contents)

    @restapi
    def test_patch_updates_set_reminder(self, api_client):
        self.login(self.regular_user, api_client)
        self.task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_DAY_BEFORE)
        payload = {'option_type': TASK_REMINDER_ONE_WEEK_BEFORE.option_type}
        api_client.open(self.task, endpoint='@reminder', data=payload, method='PATCH')

        self.assertEqual(204, api_client.status_code)
        self.assertEqual(
            TASK_REMINDER_ONE_WEEK_BEFORE.option_type,
            self.task_reminder.get_reminder(self.task).option_type,
        )

    @restapi
    def test_patch_raises_404_when_updating_not_yet_set_reminder(self, api_client):
        self.login(self.regular_user, api_client)
        payload = {'option_type': TASK_REMINDER_ONE_WEEK_BEFORE.option_type}
        with api_client.expect_http_error(404):
            api_client.open(self.task, endpoint='@reminder', data=payload, method='PATCH')

        self.assertIsNone(self.task_reminder.get_reminder(self.task))

    @restapi
    def test_delete_removes_task_reminder(self, api_client):
        self.login(self.regular_user, api_client)
        self.task_reminder.set_reminder(self.task, TASK_REMINDER_ONE_DAY_BEFORE)

        self.assertEqual(
            TASK_REMINDER_ONE_DAY_BEFORE.option_type,
            self.task_reminder.get_reminder(self.task).option_type,
        )

        api_client.open(self.task, endpoint='@reminder', method='DELETE')

        self.assertEqual(204, api_client.status_code)
        self.assertIsNone(self.task_reminder.get_reminder(self.task))

    @restapi
    def test_delete_raises_404_if_removing_non_existing_task_reminder(self, api_client):
        self.login(self.regular_user, api_client)
        self.assertIsNone(self.task_reminder.get_reminder(self.task))

        with api_client.expect_http_error(404):
            api_client.open(self.task, endpoint='@reminder', method='DELETE')

        self.assertIsNone(self.task_reminder.get_reminder(self.task))
