from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.response import IResponseContainer
from opengever.task.reminder import ReminderSameDay
from opengever.task.reminder.reminder import TaskReminder
from opengever.task.response_syncer.workflow import WorkflowResponseSyncerReceiver
from opengever.testing import IntegrationTestCase
from opengever.testing.event_recorder import get_recorded_events
from opengever.testing.event_recorder import register_event_recorder
from plone import api
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class TestAssignTask(IntegrationTestCase):

    @browsing
    def test_do_nothing_when_responsible_has_not_changed(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assign_task(self.regular_user, u'Thats a job for you.')

        self.assertEquals(self.task.absolute_url(), browser.url.strip('/'))
        self.assertEquals(['No changes: same responsible selected'],
                          error_messages())

    def assign_task(self, responsible, response, browser=default_browser):
        data = {'form.widgets.transition': 'task-transition-reassign'}
        browser.open(self.task, data, view='assign-task')
        browser.fill({'Response': response})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(responsible)
        browser.click_on('Assign')

    @browsing
    def test_responsible_client_and_transition_field_is_hidden(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, view='assign-task')
        self.assertIsNone(browser.find('Responsible Client'))
        self.assertIsNone(browser.find('Transition'))

    @browsing
    def test_responsible_is_mandatory(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.task, view='assign-task')
        browser.click_on('Assign')

        self.assertEqual([], info_messages())
        errors = browser.css("#formfield-form-widgets-transition .error")
        self.assertEqual(['Required input is missing.'], errors.text)

    @browsing
    def test_updates_responsible(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assign_task(self.secretariat_user, u'Thats a job for you.')

        self.assertEquals(self.secretariat_user.getId(),
                          self.task.responsible)
        self.assertEquals(self.secretariat_user.getId(),
                          self.task.get_sql_object().responsible)
        self.assertEqual(['Task successfully reassigned.'], info_messages())
        self.assertEqual(self.task, browser.context)

    @browsing
    def test_remove_task_reminder_of_old_responsible(self, browser):
        self.login(self.regular_user, browser=browser)

        task_reminder = TaskReminder()
        task_reminder.set_reminder(self.task, ReminderSameDay.option_type)

        self.assertIsNotNone(task_reminder.get_reminder(self.task))

        self.assign_task(self.secretariat_user, u'Thats a job for you.')
        self.assertIsNone(task_reminder.get_reminder(self.task))

    @browsing
    def test_adds_an_corresponding_response(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assign_task(self.secretariat_user, u'Please make that for me.')

        response = IResponseContainer(self.task).list()[-1]
        self.assertEquals(
            [{'after': self.secretariat_user.getId(),
              'field_id': 'responsible',
              'field_title': u'label_responsible',
              'before': self.regular_user.getId()}],
            response.changes)
        self.assertEquals('Please make that for me.', response.text)

    @browsing
    def test_assign_open_task_to_a_foreign_org_unit_is_possible(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('task-state-open', self.task)

        org_unit = self.add_additional_admin_and_org_unit()[1]

        create(Builder('ogds_user')
               .id('johnny.english')
               .having(firstname=u'Johnny', lastname=u'English')
               .assign_to_org_units([org_unit]))

        self.assign_task(u'gdgs:johnny.english', u'Please make that for me.')

        self.assertEquals('johnny.english', self.task.responsible)
        self.assertEquals('gdgs', self.task.responsible_client)

    @browsing
    def test_switching_admin_unit_in_progress_state_is_not_possible(self, browser):
        self.login(self.regular_user, browser=browser)

        org_unit = self.add_additional_admin_and_org_unit()[1]

        create(Builder('ogds_user')
               .id('johnny.english')
               .having(firstname=u'Johnny', lastname=u'English')
               .assign_to_org_units([org_unit]))

        self.assign_task(u'gdgs:johnny.english', u'Please make that for me.')

        self.assertEquals(
            [u'Admin unit changes are not allowed if the task or forwarding is'
             u' already accepted.'],
            browser.css('.fieldErrorBox .error').text)

        self.assertEquals(self.regular_user.id, self.task.responsible)

    @browsing
    def test_reassign_task_to_a_team_is_possible(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_workflow_state('task-state-open', self.task)

        self.assign_task('team:1', 'Do something')
        self.assertEquals('team:1', self.task.responsible)

    @browsing
    def test_reassign_task_in_progress_state_to_a_team_isnt_possible(self, browser):
        self.login(self.regular_user, browser=browser)

        self.assign_task('team:1', 'Do something')

        self.assertEquals(
            ['Team responsibles are only allowed if the task or forwarding is open.'],
            browser.css('.fieldErrorBox .error').text)
        self.assertEquals(self.regular_user.getId(), self.task.responsible)

    @browsing
    def test_modify_event_is_fired_but_only_once(self, browser):
        register_event_recorder(IObjectModifiedEvent)

        self.login(self.regular_user, browser=browser)
        self.assign_task(self.secretariat_user, u'Thats a job for you.')

        events = get_recorded_events()

        self.assertEquals(1, len(events))
        self.assertEqual(self.task, events[0].object)

    @browsing
    def test_revokes_permission_for_former_responsible(self, browser):
        self.login(self.regular_user, browser=browser)

        self.assign_task(self.secretariat_user, u'Thats a job for you.')

        manager = RoleAssignmentManager(self.task)
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task).id,
              'principal': 'jurgen.konig'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task).id,
              'principal': u'fa_inbox_users'}],
            manager.storage._storage())

    @browsing
    def test_redirects_to_portal_when_current_user_has_no_longer_view_permission(self, browser):
        self.login(self.regular_user, browser=browser)

        api.content.disable_roles_acquisition(obj=self.dossier)
        self.assign_task(self.secretariat_user, u'Thats a job for you.')

        manager = RoleAssignmentManager(self.task)
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task).id,
              'principal': 'jurgen.konig'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task).id,
              'principal': u'fa_inbox_users'}],
            manager.storage._storage())

        self.assertEqual(self.portal.absolute_url(), browser.url)
        self.assertEqual(
            ['Task successfully reassigned. You are no longer permitted to '
             'access the task.'],
            info_messages())


class TestAssignTaskWithSuccessors(IntegrationTestCase):

    def setUp(self):
        super(TestAssignTaskWithSuccessors, self).setUp()
        self.login(self.regular_user)
        self.successor = create(Builder('task')
                                .within(self.dossier)
                                .having(responsible_client='fa',
                                        responsible=self.regular_user.getId())
                                .successor_from(self.task))

        # disable IInternalOpengeverRequestLayer check in StateSyncer receiver
        self.org_check = WorkflowResponseSyncerReceiver._check_internal_request
        WorkflowResponseSyncerReceiver._check_internal_request = lambda x: True

    def tearDown(self):
        super(TestAssignTaskWithSuccessors, self).tearDown()
        WorkflowResponseSyncerReceiver._check_internal_request = self.org_check

    @browsing
    def test_syncs_predecessor_when_reassigning_successor(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.successor)
        browser.find('task-transition-reassign').click()
        browser.fill({'Response': u'Bitte \xfcbernehmen Sie, Danke!'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.find('Assign').click()

        browser.open(self.task, view='tabbedview_view-overview')
        response = browser.css('.answers .answer')[0]
        self.assertEquals(
            [u'Reassigned from B\xe4rfuss K\xe4thi (kathi.barfuss) to K\xf6nig '
             u'J\xfcrgen (jurgen.konig)'],
            response.css('h3').text)
        self.assertEquals(
            self.secretariat_user.getId(), self.task.responsible)

    @browsing
    def test_syncs_successor_when_reassigning_predecessor(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task)
        browser.find('task-transition-reassign').click()
        browser.fill({'Response': u'Bitte \xfcbernehmen Sie, Danke!'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.find('Assign').click()

        browser.open(self.successor, view='tabbedview_view-overview')
        response = browser.css('.answers .answer')[0]
        self.assertEquals(
            [u'Reassigned from B\xe4rfuss K\xe4thi (kathi.barfuss) to K\xf6nig '
             u'J\xfcrgen (jurgen.konig)'],
            response.css('h3').text)
        self.assertEquals(
            self.secretariat_user.getId(), self.successor.responsible)

    @browsing
    def test_revokes_roles_also_on_predecessor_when_reassigning_successor(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.successor)
        browser.find('task-transition-reassign').click()
        browser.fill({'Response': u'Bitte \xfcbernehmen Sie, Danke!'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.find('Assign').click()

        manager = RoleAssignmentManager(self.task)
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task).id,
              'principal': 'jurgen.konig'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task).id,
              'principal': u'fa_inbox_users'}],
            manager.storage._storage())

    @browsing
    def test_revokes_roles_also_on_successor_when_reassigning_predecessor(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task)
        browser.find('task-transition-reassign').click()
        browser.fill({'Response': u'Bitte \xfcbernehmen Sie, Danke!'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.find('Assign').click()

        manager = RoleAssignmentManager(self.successor)
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.successor).id,
              'principal': 'jurgen.konig'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.successor).id,
              'principal': u'fa_inbox_users'}],
            manager.storage._storage())
