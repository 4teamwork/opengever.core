from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.task.adapters import IResponseContainer
from opengever.task.response_syncer.workflow import WorkflowResponseSyncerReceiver
from opengever.testing import IntegrationTestCase
from opengever.testing.event_recorder import get_recorded_events
from opengever.testing.event_recorder import register_event_recorder
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class TestAssignTask(IntegrationTestCase):

    @browsing
    def test_do_nothing_when_responsible_has_not_changed(self, browser):
        self.login(self.regular_user, browser=browser)

        responsible = 'fa:{}'.format(self.regular_user.getId())
        self.assign_task(responsible, u'Thats a job for you.')

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
    def test_updates_responsible(self, browser):
        self.login(self.regular_user, browser=browser)

        responsible = 'fa:{}'.format(self.secretariat_user.getId())
        self.assign_task(responsible, u'Thats a job for you.')

        self.assertEquals(self.secretariat_user.getId(),
                          self.task.responsible)
        self.assertEquals(self.secretariat_user.getId(),
                          self.task.get_sql_object().responsible)

    @browsing
    def test_adds_an_corresponding_response(self, browser):
        self.login(self.regular_user, browser=browser)

        responsible = 'fa:{}'.format(self.secretariat_user.getId())
        self.assign_task(responsible, u'Please make that for me.')

        response = IResponseContainer(self.task)[-1]
        self.assertEquals(
            [{'after': self.secretariat_user.getId(),
              'id': 'responsible',
              'name': u'label_responsible',
              'before': self.regular_user.getId()}],
            response.changes)
        self.assertEquals('Please make that for me.', response.text)

    @browsing
    def test_assign_task_only_to_users_of_the_current_orgunit(self, browser):
        self.login(self.regular_user, browser=browser)

        org_unit2 = create(Builder('org_unit')
                           .id('afi')
                           .having(title=u'Finanzdirektion',
                                   admin_unit_id='fa')
                           .with_default_groups())

        self.hans = create(Builder('ogds_user')
                           .id('james.bond')
                           .having(firstname=u'James', lastname=u'Bond')
                           .assign_to_org_units([org_unit2]))

        data = {'form.widgets.transition': 'task-transition-reassign'}
        browser.open(self.task, data, view='assign-task')

        browser.open(self.task,
                     data={'q': 'james', 'page': 1},
                     view='@@assign-task/++widget++form.widgets.responsible/search')
        self.assertEquals([], browser.json.get('results'))

        browser.open(self.task,
                     data={'q': 'robert', 'page': 1},
                     view='@@assign-task/++widget++form.widgets.responsible/search')
        self.assertEquals(
            [{u'_resultId': u'fa:robert.ziegler',
              u'id': u'fa:robert.ziegler',
              u'text': u'Finanzamt: Ziegler Robert (robert.ziegler)'}],
            browser.json.get('results'))

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
        responsible = 'fa:{}'.format(self.secretariat_user.getId())
        self.assign_task(responsible, u'Thats a job for you.')

        events = get_recorded_events()

        self.assertEquals(1, len(events))
        self.assertEqual(self.task, events[0].object)


class TestAssignTaskWithSuccessors(IntegrationTestCase):

    def setUp(self):
        super(TestAssignTaskWithSuccessors, self).setUp()
        self.login(self.regular_user)
        self.successor = create(Builder('task')
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
        form.find_widget('Responsible').fill(
            'fa:{}'.format(self.secretariat_user.getId()))
        browser.find('Assign').click()

        browser.open(self.task, view='tabbedview_view-overview')
        response = browser.css('.answers .answer')[0]
        self.assertEquals(
            [u'Reassigned from B\xe4rfuss K\xe4thi (kathi.barfuss) to K\xf6nig '
             u'J\xfcrgen (jurgen.konig) by B\xe4rfuss K\xe4thi (kathi.barfuss)'],
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
        form.find_widget('Responsible').fill(
            'fa:{}'.format(self.secretariat_user.getId()))
        browser.find('Assign').click()

        browser.open(self.successor, view='tabbedview_view-overview')
        response = browser.css('.answers .answer')[0]
        self.assertEquals(
            [u'Reassigned from B\xe4rfuss K\xe4thi (kathi.barfuss) to K\xf6nig '
             u'J\xfcrgen (jurgen.konig) by B\xe4rfuss K\xe4thi (kathi.barfuss)'],
            response.css('h3').text)
        self.assertEquals(
            self.secretariat_user.getId(), self.successor.responsible)
