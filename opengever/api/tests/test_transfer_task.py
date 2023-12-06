from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.task.browser.accept.utils import accept_task_with_successor
from opengever.task.reminder import ReminderOneDayBefore
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import obj2brain
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
    def test_limited_admin_can_transfer_a_task(self, browser):
        self.login(self.limited_admin, browser=browser)
        browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.task.responsible,
                         "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), self.task.responsible)

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
    def test_limited_admin_can_transfer_a_forwarding(self, browser):
        self.login(self.limited_admin, browser=browser)
        browser.open(self.inbox_forwarding.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.inbox_forwarding.responsible,
                         "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), self.inbox_forwarding.responsible)

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
                         data=json.dumps({"old_userid": self.regular_user.id}))
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
                         data=json.dumps({"new_userid": self.regular_user.id}))
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
                            {"new_userid": self.regular_user.id, "old_userid": "chaosqueen"})
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
                            {"new_userid": self.regular_user.id, "old_userid": self.regular_user.id})
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

    @browsing
    def test_task_transfer_changes_responsible_of_resolved_task(self, browser):
        self.login(self.administrator, browser=browser)
        self.set_workflow_state('task-state-resolved', self.task)
        browser.open(self.task.absolute_url() + '/@transfer-task', method='POST',
                     headers=self.api_headers, data=json.dumps(
                        {"old_userid": self.task.responsible,
                         "new_userid": self.meeting_user.getId()}))

        self.assertEqual(self.meeting_user.getId(), self.task.responsible)

        sql_task = self.task.get_sql_object()
        self.assertEqual(self.meeting_user.getId(), sql_task.responsible)
        activity = Activity.query.one()
        self.assertEqual('task-transition-reassign', activity.kind)


class TestTransferTaskInterAdminUnit(IntegrationTestCase):

    features = ('activity', )
    maxDiff = None

    def prepare_accepted_task_pair(self):
        issuer_id = self.dossier_responsible.id
        responsible_id = self.regular_user.id

        predecessor = create(
            Builder('task')
            .within(self.dossier)
            .having(issuer=issuer_id,
                    responsible=responsible_id,
                    responsible_client='fa',
                    task_type='correction')
            .in_state('task-state-open')
            .titled(u'Inquiry from a concerned citizen'))

        successor = accept_task_with_successor(
            self.dossier,
            str(predecessor.oguid),
            u'I accept this task',
        )

        # Set four reminders for both task side and both users
        for user_id in (issuer_id, responsible_id):
            for task in (predecessor, successor):
                task.set_reminder(ReminderOneDayBefore(), user_id=user_id)

        return predecessor, successor

    @browsing
    def test_transfer_responsible_when_invoked_on_predecessor(self, browser):
        self.login(self.regular_user, browser)

        predecessor, successor = self.prepare_accepted_task_pair()
        self.assert_transferred_properly(
            browser,
            fieldname='responsible',
            local_task=predecessor,
            remote_task=successor,
        )

    @browsing
    def test_transfer_responsible_when_invoked_on_successor(self, browser):
        self.login(self.regular_user, browser)

        predecessor, successor = self.prepare_accepted_task_pair()
        self.assert_transferred_properly(
            browser,
            fieldname='responsible',
            local_task=successor,
            remote_task=predecessor,
        )

    @browsing
    def test_transfer_issuer_when_invoked_on_predecessor(self, browser):
        self.login(self.regular_user, browser)

        predecessor, successor = self.prepare_accepted_task_pair()
        self.assert_transferred_properly(
            browser,
            fieldname='issuer',
            local_task=predecessor,
            remote_task=successor,
        )

    @browsing
    def test_transfer_issuer_when_invoked_on_successor(self, browser):
        self.login(self.regular_user, browser)

        predecessor, successor = self.prepare_accepted_task_pair()
        self.assert_transferred_properly(
            browser,
            fieldname='issuer',
            local_task=successor,
            remote_task=predecessor,
        )

    def assert_transferred_properly(self, browser, fieldname,
                                    local_task, remote_task):
        """This is the core for the test cases above.

        Built with more abstract local and remote tasks that are passed in,
        and a `fieldname` that refers to either 'responsible' or 'issuer',
        so we can test different permutations (invocation from both sides
        of a task pair, responsible vs. issuer).
        """
        self.login(self.administrator, browser)

        new_userid = self.meeting_user.getId()
        old_userid = getattr(local_task, fieldname)

        with self.observe_notifications() as notifications, \
                self.observe_reminders(local_task) as local_reminders, \
                self.observe_reminders(remote_task) as remote_reminders, \
                self.observe_responses(local_task) as local_responses, \
                self.observe_responses(remote_task) as remote_responses:

            browser.open(local_task.absolute_url() + '/@transfer-task',
                         method='POST', headers=self.api_headers,
                         data=json.dumps({
                             "old_userid": old_userid,
                             "new_userid": new_userid}
            ))

        # Verify that transfer happened on both sides of the task pair
        for task in (local_task, remote_task):

            # Field on dexterity object got updated
            self.assertEqual(new_userid, getattr(task, fieldname))

            # Metadata in catalog got updated
            self.assertEqual(new_userid, getattr(obj2brain(task), fieldname))

            # Attribute on SQL entity got updated
            self.assertEqual(new_userid, getattr(task.get_sql_object(), fieldname))

            # Local role assignments got transferred if responsible changed
            if fieldname == 'responsible':
                mgr = RoleAssignmentManager(task)
                old_user_assignments = mgr.get_assignments_by_principal_id(old_userid)
                new_user_assignments = mgr.get_assignments_by_principal_id(new_userid)
                self.assertEqual(1, len(old_user_assignments))
                self.assertEqual(1, len(new_user_assignments))

                new_user_assignment = new_user_assignments[0]
                self.assertEqual({
                    'cause': {
                        'id': ASSIGNMENT_VIA_TASK,
                        'title': u'Via task',
                    },
                    'principal': new_userid,
                    'reference': {
                        'title': task.title,
                        'url': task.absolute_url(),
                    },
                    'roles': ['Editor']},
                    new_user_assignment.serialize())

        # Both sides contain appropriate responses
        for responses in (local_responses, remote_responses):

            # Exactly one new response got added
            self.assertEqual(1, len(responses['added']))
            response = responses['added'][0]

            # With a change for the expected field, from old to new user
            expected_changes = [{
                'field_id': fieldname,
                'field_title': u'label_%s' % fieldname,
                'before': old_userid,
                'after': new_userid,
            }]
            self.assertEqual(expected_changes, response.changes)

            # Marked with the appropriate transition
            if fieldname == 'responsible':
                expected_transition = 'task-transition-reassign'

            elif fieldname == 'issuer':
                expected_transition = 'task-transition-change-issuer'

            self.assertEqual(expected_transition, response.transition)

            # Created by the Admin that performed the transfer
            self.assertEqual(self.administrator.id, response.creator)

        # Reminders for old user got removed, on both sides
        for reminders in (local_reminders, remote_reminders):
            self.assertEqual([old_userid], reminders['removed'])

        # No notifications have been generated
        self.assertEqual([], notifications['added'])
