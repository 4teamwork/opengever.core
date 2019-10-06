from datetime import date
from ftw.testbrowser import browsing
from opengever.api.reminder import error_msgs
from opengever.task.reminder import ReminderOnDate
from opengever.task.reminder import ReminderOneDayBefore
from opengever.task.reminder import ReminderOneWeekBefore
from opengever.testing import IntegrationTestCase
import json


class TestTaskReminderAPI(IntegrationTestCase):

    def setUp(self):
        super(TestTaskReminderAPI, self).setUp()
        self.http_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    @browsing
    def test_post_adds_task_reminder(self, browser):
        self.login(self.regular_user, browser)
        payload = {'option_type': ReminderOneDayBefore.option_type}

        self.assertIsNone(
            self.task.get_reminder())

        browser.open(
            self.task.absolute_url() + '/@reminder',
            data=json.dumps(payload),
            method='POST',
            headers=self.http_headers,
        )

        self.assertEqual(204, browser.status_code)
        self.assertEqual(
            ReminderOneDayBefore(),
            self.task.get_reminder())

    @browsing
    def test_post_supports_reminder_params(self, browser):
        self.login(self.regular_user, browser)
        payload = {'option_type': ReminderOnDate.option_type,
                   'params': {'date': '2018-12-30'}}

        self.assertIsNone(
            self.task.get_reminder())

        browser.open(
            self.task.absolute_url() + '/@reminder',
            data=json.dumps(payload),
            method='POST',
            headers=self.http_headers,
        )

        self.assertEqual(204, browser.status_code)
        self.assertEqual(
            ReminderOnDate({'date': date(2018, 12, 30)}),
            self.task.get_reminder())

    @browsing
    def test_post_raises_when_option_type_is_missing(self, browser):
        self.login(self.regular_user, browser)
        payload = {}

        with browser.expect_http_error(400):
            browser.open(
                self.task.absolute_url() + '/@reminder',
                data=json.dumps(payload),
                method='POST',
                headers=self.http_headers,
            )

        self.assertEqual(
            {"message": error_msgs.get('missing_option_type'),
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_post_raises_409_when_adding_already_set_reminder(self, browser):
        self.login(self.regular_user, browser)
        self.task.set_reminder(ReminderOneDayBefore())

        payload = {'option_type': ReminderOneDayBefore.option_type}

        with browser.expect_http_error(409):
            browser.open(
                self.task.absolute_url() + '/@reminder',
                data=json.dumps(payload),
                method='POST',
                headers=self.http_headers,
            )

        self.assertEqual(
            ReminderOneDayBefore(),
            self.task.get_reminder())

    @browsing
    def test_post_shows_possible_reminder_options_if_option_does_not_exists(self, browser):
        self.login(self.regular_user, browser)
        payload = {'option_type': 'not_existing_option_type'}

        with browser.expect_http_error(400):
            browser.open(
                self.task.absolute_url() + '/@reminder',
                data=json.dumps(payload),
                method='POST',
                headers=self.http_headers,
            )

        self.assertEqual(
            {"message": error_msgs.get('non_existing_option_type'),
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_patch_updates_set_reminder(self, browser):
        self.login(self.regular_user, browser)
        self.task.set_reminder(ReminderOneDayBefore())

        payload = {'option_type': ReminderOneWeekBefore.option_type}

        browser.open(
            self.task.absolute_url() + '/@reminder',
            data=json.dumps(payload),
            method='PATCH',
            headers=self.http_headers,
        )

        self.assertEqual(204, browser.status_code)
        self.assertEqual(
            ReminderOneWeekBefore(),
            self.task.get_reminder())

    @browsing
    def test_patch_supports_reminder_params(self, browser):
        self.login(self.regular_user, browser)
        self.task.set_reminder(ReminderOnDate({'date': date(1995, 6, 29)}))

        payload = {'params': {'date': '2018-12-30'}}

        browser.open(
            self.task.absolute_url() + '/@reminder',
            data=json.dumps(payload),
            method='PATCH',
            headers=self.http_headers,
        )

        self.assertEqual(204, browser.status_code)
        self.assertEqual(
            ReminderOnDate({'date': date(2018, 12, 30)}),
            self.task.get_reminder())

    @browsing
    def test_patch_raises_404_when_updating_not_yet_set_reminder(self, browser):
        self.login(self.regular_user, browser)

        payload = {'option_type': ReminderOneWeekBefore.option_type}

        with browser.expect_http_error(404):
            browser.open(
                self.task.absolute_url() + '/@reminder',
                data=json.dumps(payload),
                method='PATCH',
                headers=self.http_headers,
            )

        self.assertIsNone(
            self.task.get_reminder())

    @browsing
    def test_delete_removes_task_reminder(self, browser):
        self.login(self.regular_user, browser)
        self.task.set_reminder(ReminderOneDayBefore())

        self.assertEqual(
            ReminderOneDayBefore(),
            self.task.get_reminder())

        browser.open(
            self.task.absolute_url() + '/@reminder',
            method='DELETE',
            headers=self.http_headers,
        )

        self.assertEqual(204, browser.status_code)
        self.assertIsNone(
            self.task.get_reminder())

    @browsing
    def test_delete_raises_404_if_removing_non_existing_task_reminder(self, browser):
        self.login(self.regular_user, browser)

        self.assertIsNone(
            self.task.get_reminder())

        with browser.expect_http_error(404):
            browser.open(
                self.task.absolute_url() + '/@reminder',
                method='DELETE',
                headers={'Accept': 'application/json'},
            )

        self.assertIsNone(
            self.task.get_reminder())
