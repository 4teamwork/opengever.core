from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseContainer
from opengever.globalindex.model.reminder_settings import ReminderSetting
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.reminder import ReminderSameDay
from opengever.task.response_syncer.deadline import ModifyDeadlineResponseSyncerReceiver
from opengever.testing import IntegrationTestCase
from opengever.testing.event_recorder import get_recorded_events
from opengever.testing.event_recorder import register_event_recorder
from zExceptions import Unauthorized
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import datetime


class TestDeadlineModificationForm(IntegrationTestCase):

    def setUp(self):
        super(TestDeadlineModificationForm, self).setUp()

        # disable IInternalOpengeverRequestLayer check in StateSyncer receiver
        self.org_check = ModifyDeadlineResponseSyncerReceiver._check_internal_request
        ModifyDeadlineResponseSyncerReceiver._check_internal_request = lambda x: True

    def tearDown(self):
        super(TestDeadlineModificationForm, self).tearDown()
        ModifyDeadlineResponseSyncerReceiver._check_internal_request = self.org_check

    def _change_deadline(self, task, new_deadline, text=u'', browser=default_browser):
        browser.open(task)
        browser.click_on('task-transition-modify-deadline')
        browser.fill({'New Deadline': new_deadline.strftime('%d.%m.%Y'),
                      'Response': text})
        browser.click_on('Save')

    @browsing
    def test_task_deadline_is_updated_when_set_to_a_valid_date(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        new_deadline = datetime.date(2013, 10, 1)

        browser.open(self.task)
        browser.click_on('task-transition-modify-deadline')
        browser.fill({'New Deadline': new_deadline.strftime('%d.%m.%Y')})
        browser.click_on('Save')

        self.assertEquals(new_deadline, self.task.deadline)
        self.assertEquals(['Deadline successfully changed.'], info_messages())

    @browsing
    def test_raise_invalidation_error_when_new_deadline_is_the_current_one(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.task)
        browser.click_on('task-transition-modify-deadline')
        browser.fill({'New Deadline': self.task.deadline.strftime('%d.%m.%Y')})
        browser.click_on('Save')

        self.assertEquals('{}/@@modify_deadline'.format(self.task.absolute_url()),
                          browser.url)
        self.assertEquals(
            ['The given deadline, is the current one.'],
            browser.css('#formfield-form-widgets-new_deadline .error').text)

    @browsing
    def test_deadline_is_updated_also_in_globalindex(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        self._change_deadline(self.task, datetime.date(2013, 10, 1), '')

        self.assertEquals(self.task.get_sql_object().deadline,
                          datetime.date(2013, 10, 1))

    @browsing
    def test_according_response_is_created_when_modify_deadline(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        old_deadline = self.task.deadline

        self._change_deadline(self.task, datetime.date(2013, 10, 1), 'Lorem Ipsum')
        response = IResponseContainer(self.task).list()[-1]

        self.assertEquals('Lorem Ipsum', response.text)
        self.assertEquals(self.dossier_responsible.id, response.creator)
        self.assertEquals(
            [{'after': datetime.date(2013, 10, 1),
              'field_id': 'deadline',
              'field_title': u'label_deadline',
              'before': old_deadline}],
            response.changes)

    @browsing
    def test_successor_is_also_updated_when_modify_predecessors_deadline(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        # Make predecessor <-> successor pair
        predecessor = self.task
        successor = self.seq_subtask_1
        ISuccessorTaskController(successor).set_predecessor(
            ISuccessorTaskController(predecessor).get_oguid())

        self._change_deadline(
            predecessor, datetime.date(2013, 10, 1), 'Lorem Ipsum')

        self.assertEquals(successor.deadline, datetime.date(2013, 10, 1))

    @browsing
    def test_forwarding_predecessors_are_skipped_when_syncing_deadline_modification(self, browser):
        self.login(self.secretariat_user, browser=browser)

        # Make predecessor (forwarding) <-> successor (task) pair, like
        # it's created when assigning a forwarding to a dossier.
        predecessor = self.inbox_forwarding
        successor = self.seq_subtask_1
        ISuccessorTaskController(successor).set_predecessor(
            Oguid.for_object(predecessor).id)

        self._change_deadline(
            successor, datetime.date(2013, 10, 1), 'Lorem Ipsum')

        self.assertEquals(successor.deadline, datetime.date(2013, 10, 1))
        self.assertEquals(None, predecessor.deadline)

    @browsing
    def test_modify_event_is_fired_but_only_once(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        register_event_recorder(IObjectModifiedEvent)

        self._change_deadline(self.task, datetime.date(2013, 10, 1), '')

        events = get_recorded_events()

        self.assertEquals(1, len(events))
        self.assertEqual(self.task, events[0].object)

    @browsing
    def test_recalculate_remind_on_for_set_reminders_if_deadline_changed(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        self.task.deadline = today
        self.task.set_reminder(
            ReminderSameDay(), self.regular_user.id)
        self.task.sync()

        sql_setting = ReminderSetting.query.first()
        self.assertEqual(today, sql_setting.remind_day)

        self._change_deadline(self.task, tomorrow)

        sql_setting = ReminderSetting.query.first()
        self.assertEqual(tomorrow, sql_setting.remind_day)


class TestDeadlineModifierController(IntegrationTestCase):

    def test_modify_is_allowed_for_issuer_on_a_open_task(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-open', self.task)

        self.assertTrue(IDeadlineModifier(self.task).is_modify_allowed())

    def test_modify_is_allowed_for_issuer_on_a_in_progress_task(self):
        self.login(self.dossier_responsible)
        self.set_workflow_state('task-state-in-progress', self.task)

        self.assertTrue(IDeadlineModifier(self.task).is_modify_allowed())

    def test_modify_is_allowed_for_a_inbox_group_user_when_inbox_is_issuer(self):
        self.login(self.secretariat_user)
        self.set_workflow_state('task-state-in-progress', self.task)

        self.task.issuer = 'inbox:fa'
        self.task.sync()

        modifier = IDeadlineModifier(self.task)
        self.assertTrue(modifier.is_modify_allowed(include_agency=False))
        self.assertTrue(modifier.is_modify_allowed(include_agency=True))

    def test_modify_is_allowed_for_admin_on_a_open_task_as_agency(self):
        self.login(self.administrator)

        self.set_workflow_state('task-state-open', self.task)

        modifier = IDeadlineModifier(self.task)
        self.assertFalse(modifier.is_modify_allowed(include_agency=False))
        self.assertTrue(modifier.is_modify_allowed(include_agency=True))

    def test_modify_is_allowed_for_admin_on_a_in_progress_task_as_agency(self):
        self.login(self.administrator)

        self.set_workflow_state('task-state-in-progress', self.task)

        modifier = IDeadlineModifier(self.task)
        self.assertFalse(modifier.is_modify_allowed(include_agency=False))
        self.assertTrue(modifier.is_modify_allowed(include_agency=True))

    def test_modify_is_allowed_for_issuing_org_unit_agency_member_as_agency(self):
        self.login(self.secretariat_user)

        self.set_workflow_state('task-state-in-progress', self.task)

        modifier = IDeadlineModifier(self.task)
        self.assertFalse(modifier.is_modify_allowed(include_agency=False))
        self.assertTrue(modifier.is_modify_allowed(include_agency=True))


class TestDeadlineModifier(IntegrationTestCase):

    def test_raise_unauthorized_when_mofication_is_not_allowed(self):
        self.login(self.regular_user)

        with self.assertRaises(Unauthorized):
            IDeadlineModifier(self.task).modify_deadline(
                datetime.date(2013, 10, 1),
                'changed deadline',
                'task-transition-modify-deadline')
