from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.task.adapters import IResponseContainer
from opengever.task.response_syncer.workflow import WorkflowResponseSyncerReceiver
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestAssignTask(FunctionalTestCase):

    def setUp(self):
        super(TestAssignTask, self).setUp()

        self.james = create(Builder('ogds_user')
                            .in_group(self.org_unit.users_group)
                            .having(userid='james.bond',
                                    firstname='James',
                                    lastname='Bond'))

        self.task = create(Builder('task')
                           .having(responsible_client='client1',
                                   responsible=TEST_USER_ID))

    @browsing
    def test_do_nothing_when_responsible_has_not_changed(self, browser):
        self.assign_task('Test', TEST_USER_ID, '')

        self.assertEquals(self.task.absolute_url(), browser.url.strip('/'))
        self.assertEquals(['No changes: same responsible selected'],
                          error_messages())

    @browsing
    def test_responsible_client_and_transition_field_is_hidden(self, browser):
        browser.login().open(self.task, view='assign-task')

        self.assertEquals(None, browser.find('Responsible Client'))

    @browsing
    def test_updates_responsible(self, browser):

        self.assign_task('James', 'james.bond', '')

        self.assertEquals('james.bond', self.task.responsible)
        self.assertEquals('james.bond',
                          self.task.get_sql_object().responsible)

    @browsing
    def test_adds_an_corresponding_response(self, browser):
        self.assign_task('James', 'james.bond', 'Please make that for me.')

        response = IResponseContainer(self.task)[-1]

        self.assertEquals(
            [{'after': u'james.bond', 'id': 'responsible',
             'name': u'label_responsible', 'before': 'test_user_1_'}],
            response.changes)
        self.assertEquals('Please make that for me.', response.text)

    def assign_task(self, name, userid, response, browser=default_browser):
        data = {'form.widgets.transition': 'task-transition-reassign'}
        browser.login().open(self.task, data, view='assign-task')
        browser.fill({'Responsible': userid, 'Response': response})
        browser.click_on('Assign')


class TestAssignTaskWithSuccessors(FunctionalTestCase):

    def setUp(self):
        super(TestAssignTaskWithSuccessors, self).setUp()
        self.james = create(Builder('ogds_user')
                            .in_group(self.org_unit.users_group)
                            .having(userid='james.bond',
                                    firstname='James',
                                    lastname='Bond'))

        self.predecessor = create(Builder('task')
                                  .having(responsible_client='client1',
                                          responsible=TEST_USER_ID))
        self.successor = create(Builder('task')
                                .having(responsible_client='client1',
                                        responsible=TEST_USER_ID)
                                .successor_from(self.predecessor))

        # disable IInternalOpengeverRequestLayer check in StateSyncer receiver
        self.org_check = WorkflowResponseSyncerReceiver._check_internal_request
        WorkflowResponseSyncerReceiver._check_internal_request = lambda x: True

    def tearDown(self):
        super(TestAssignTaskWithSuccessors, self).tearDown()
        WorkflowResponseSyncerReceiver._check_internal_request = self.org_check

    @browsing
    def test_syncs_predecessor_when_reassigning_successor(self, browser):
        browser.login().open(self.successor)
        browser.find('task-transition-reassign').click()
        browser.fill({'Responsible': 'james.bond',
                      'Response': u'Bitte \xfcbernehmen Sie, Danke!'})
        browser.find('Assign').click()

        browser.open(self.predecessor, view='tabbedview_view-overview')
        response = browser.css('.answers .answer')[0]
        self.assertEquals(
            ['Reassigned from Test User (test_user_1_) to Bond James '
             '(james.bond) by Test User (test_user_1_)'],
            response.css('h3').text)
        self.assertEquals('james.bond', self.predecessor.responsible)

    @browsing
    def test_syncs_successor_when_reassigning_successor(self, browser):
        browser.login().open(self.predecessor)
        browser.find('task-transition-reassign').click()
        browser.fill({'Responsible': 'james.bond',
                      'Response': u'Bitte \xfcbernehmen Sie, Danke!'})
        browser.find('Assign').click()

        browser.open(self.successor, view='tabbedview_view-overview')
        response = browser.css('.answers .answer')[0]
        self.assertEquals(
            ['Reassigned from Test User (test_user_1_) to Bond James '
             '(james.bond) by Test User (test_user_1_)'],
            response.css('h3').text)
        self.assertEquals('james.bond', self.successor.responsible)
