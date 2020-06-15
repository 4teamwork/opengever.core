from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.testing import IntegrationTestCase
import json


class TestTransferTaskPost(IntegrationTestCase):
    features = ('activity', )
    maxDiff = None

    @browsing
    def test_task_transfer_changes_responsible(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.task.responsible,
                         "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), self.task.responsible)

        sql_task = self.task.get_sql_object()
        self.assertEqual(self.meeting_user.getId(), sql_task.responsible)
        activity = Activity.query.one()
        self.assertEqual('task-transition-reassign', activity.kind)

    @browsing
    def test_task_transfer_for_forwarding_changes_responsible(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.inbox_forwarding.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.inbox_forwarding.responsible,
                         "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), self.inbox_forwarding.responsible)

        sql_forwarding = self.inbox_forwarding.get_sql_object()
        self.assertEqual(self.meeting_user.getId(), sql_forwarding.responsible)
        activity = Activity.query.one()
        self.assertEqual('forwarding-transition-reassign', activity.kind)

    @browsing
    def test_task_transfer_changes_issuer(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.task.issuer,
                         "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), self.task.issuer)

        sql_task = self.task.get_sql_object()
        self.assertEqual(self.meeting_user.getId(), sql_task.issuer)
        activity = Activity.query.one()
        self.assertEqual('task-transition-change-issuer', activity.kind)

    @browsing
    def test_task_transfer_for_forwarding_changes_issuer(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.inbox_forwarding.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.inbox_forwarding.issuer,
                         "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), self.inbox_forwarding.issuer)

        sql_forwarding = self.inbox_forwarding.get_sql_object()
        self.assertEqual(self.meeting_user.getId(), sql_forwarding.issuer)
        activity = Activity.query.one()
        self.assertEqual('forwarding-transition-change-issuer', activity.kind)

    @browsing
    def test_task_transfer_changes_issuer_and_responsible(self, browser):
        self.login(self.administrator, browser=browser)
        self.task.responsible = self.task.issuer
        new_userid = self.meeting_user.getId()
        self.assertNotEqual(self.task.issuer, new_userid)
        browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.task.issuer,
                         "new_userid": new_userid}))

        self.assertEqual(self.task.issuer, new_userid)
        self.assertEqual(self.task.responsible, new_userid)

        sql_task = self.task.get_sql_object()
        self.assertEqual(sql_task.issuer, new_userid)
        self.assertEqual(sql_task.responsible, new_userid)

        activities = Activity.query.all()
        self.assertItemsEqual(['task-transition-reassign', 'task-transition-change-issuer'],
                              [activity.kind for activity in activities])

    @browsing
    def test_task_transfer_for_forwarding_changes_issuer_and_responsible(self, browser):
        self.login(self.administrator, browser=browser)
        self.inbox_forwarding.responsible = self.inbox_forwarding.issuer
        new_userid = self.meeting_user.getId()
        self.assertNotEqual(self.inbox_forwarding.issuer, new_userid)
        browser.open(self.inbox_forwarding.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.inbox_forwarding.issuer,
                         "new_userid": new_userid}))

        self.assertEqual(self.inbox_forwarding.issuer, new_userid)
        self.assertEqual(self.inbox_forwarding.responsible, new_userid)

        sql_forwarding = self.inbox_forwarding.get_sql_object()
        self.assertEqual(sql_forwarding.issuer, new_userid)
        self.assertEqual(sql_forwarding.responsible, new_userid)

        activities = Activity.query.all()
        self.assertItemsEqual(
            ['forwarding-transition-reassign', 'forwarding-transition-change-issuer'],
            [activity.kind for activity in activities])

    @browsing
    def test_task_transfer_does_not_trigger_notifications(self, browser):
        self.login(self.administrator, browser=browser)
        notifications_before = Notification.query.all()

        browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.task.responsible,
                         "new_userid": self.meeting_user.getId()})
                     )

        notifications_after = Notification.query.all()
        self.assertEqual(notifications_before, notifications_after)

    @browsing
    def test_transfer_task_without_new_userid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"old_userid": "kathi.barfuss"}))
        self.assertEqual(
            {"message": "Property 'new_userid' is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_task_without_old_userid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({"new_userid": "kathi.barfuss"}))
        self.assertEqual(
            {"message": "Property 'old_userid' is required",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_task_with_invalid_new_userid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                         headers=self.api_headers, data=json.dumps(
                            {"old_userid": self.regular_user.getId(), "new_userid": "chaosqueen"}))
        self.assertEqual(
            {"message": "userid 'chaosqueen' does not exist",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_task_with_invalid_old_userid_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                         headers=self.api_headers, data=json.dumps(
                            {"new_userid": "kathi.barfuss", "old_userid": "chaosqueen"})
                         )
        self.assertEqual(
            {"message": "userid 'chaosqueen' does not exist",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_task_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                         headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.task.responsible,
                         "new_userid": self.meeting_user.getId()}))

        self.assertEqual(401, browser.status_code)

    @browsing
    def test_transfer_task_with_identical_userids_raises_bad_request(self, browser):
        self.login(self.administrator, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                         headers=self.api_headers, data=json.dumps(
                            {"new_userid": "kathi.barfuss", "old_userid": "kathi.barfuss"})
                         )
        self.assertEqual(
            {"message": "'old_userid' and 'new_userid' should not be the same",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_transfer_task_from_inactive_user_works(self, browser):
        self.login(self.administrator, browser=browser)

        fired_employee = create(Builder('ogds_user').id(u'fired.employee').having(active=False))
        self.task.issuer = fired_employee.userid
        sql_task = self.task.get_sql_object()
        sql_task.issuer = fired_employee.userid

        browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": fired_employee.userid,
                         "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), self.task.issuer)
        sql_task = self.task.get_sql_object()
        self.assertEqual(self.meeting_user.getId(), sql_task.issuer)
        activity = Activity.query.one()
        self.assertEqual('task-transition-change-issuer', activity.kind)
