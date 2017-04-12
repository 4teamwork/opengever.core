from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.task.adapters import IResponseContainer
from opengever.task.browser.modify_deadline import ModifyDeadlineFormView
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.syncer import ModifyDeadlineResponseSyncerReceiver
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from zExceptions import Unauthorized
import datetime


class TestDeadlineModificationForm(FunctionalTestCase):

    def tearDown(self):
        super(TestDeadlineModificationForm, self).tearDown()
        self.enable_IInternalOpengeverRequestLayer()

    def enable_IInternalOpengeverRequestLayer(self):
        if not hasattr(self, '_patched_check_internal_request'):
            return

        ModifyDeadlineResponseSyncerReceiver._check_internal_request = \
            self._patched_check_internal_request

    def disable_IInternalOpengeverRequestLayer(self):
        setattr(self, '_patched_check_internal_request',
                ModifyDeadlineResponseSyncerReceiver._check_internal_request)
        ModifyDeadlineResponseSyncerReceiver._check_internal_request = lambda x: True

    def _change_deadline(self, task, new_deadline, text=u'', browser=default_browser):
        url = ModifyDeadlineFormView.url_for(
            task, transition='task-transition-modify-deadline')

        browser.login().open(url)
        browser.fill({'New Deadline': new_deadline.strftime('%m/%d/%y'),
                      'Response': text})
        browser.click_on('Save')

    @browsing
    def test_task_deadline_is_updated_when_set_to_a_valid_date(self, browser):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID, deadline=datetime.date(2013, 1, 1)))

        new_deadline = datetime.date(2013, 10, 1)

        url = ModifyDeadlineFormView.url_for(
            task, transition='task-transition-modify-deadline')
        browser.login().open(url)
        browser.fill({'New Deadline': new_deadline.strftime('%m/%d/%y'), })
        browser.click_on('Save')

        self.assertEquals(task.deadline, datetime.date(2013, 10, 1))
        self.assertEquals(['Deadline successfully changed.'], info_messages())

    @browsing
    def test_raise_invalidation_error_when_new_deadline_is_the_current_one(self, browser):
        current_deadline = datetime.date(2013, 1, 1)
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID, deadline=current_deadline))

        url = ModifyDeadlineFormView.url_for(task,
            transition='task-transition-modify-deadline')
        browser.login().open(url)
        browser.fill({'New Deadline': current_deadline.strftime('%m/%d/%y')})
        browser.click_on('Save')

        self.assertEquals('{}/@@modify_deadline'.format(task.absolute_url()),
                          browser.url)
        self.assertEquals(
            ['The given deadline, is the current one.'],
            browser.css('#formfield-form-widgets-new_deadline .error').text)

    @browsing
    def test_deadline_is_updated_also_in_globalindex(self, browser):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID, deadline=datetime.date(2013, 1, 1)))

        self._change_deadline(task, datetime.date(2013, 10, 1), '')

        self.assertEquals(task.get_sql_object().deadline, datetime.date(2013, 10, 1))

    @browsing
    def test_according_response_is_created_when_modify_deadline(self, browser):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID,
                              deadline=datetime.date(2013, 1, 1)))

        self._change_deadline(task, datetime.date(2013, 10, 1), 'Lorem Ipsum')
        container = IResponseContainer(task)
        response = container[-1]

        self.assertEquals('Lorem Ipsum', response.text)
        self.assertEquals(TEST_USER_ID, response.creator)
        self.assertEquals(
            [{'after': datetime.date(2013, 10, 1),
              'id': 'deadline',
              'name': u'label_deadline',
              'before': datetime.date(2013, 1, 1)}],
            response.changes)

    @browsing
    def test_successor_is_also_updated_when_modify_predecessors_deadline(self, browser):
        self.disable_IInternalOpengeverRequestLayer()
        predecessor = create(Builder('task')
                             .having(issuer=TEST_USER_ID,
                                     deadline=datetime.date(2013, 1, 1)))
        succesor = create(Builder('task')
                          .having(issuer=TEST_USER_ID,
                                  deadline=datetime.date(2013, 1, 1)))

        ISuccessorTaskController(succesor).set_predecessor(
            ISuccessorTaskController(predecessor).get_oguid())

        self._change_deadline(
            predecessor, datetime.date(2013, 10, 1), 'Lorem Ipsum')

        self.assertEquals(succesor.deadline, datetime.date(2013, 10, 1))


class TestDeadlineModifierController(FunctionalTestCase):

    def setUp(self):
        super(TestDeadlineModifierController, self).setUp()

        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_userid('hugo.boss'))

        create(Builder('ogds_user')
               .having(userid='hugo.boss'))

    def test_modify_is_allowed_for_issuer_on_a_open_task(self):
        task = create(Builder('task').having(issuer='hugo.boss'))

        login(self.portal, 'hugo.boss')
        self.assertTrue(IDeadlineModifier(task).is_modify_allowed())

    def test_modify_is_allowed_for_issuer_on_a_in_progress_task(self):
        task = create(Builder('task')
                      .having(issuer='hugo.boss', responsible=TEST_USER_ID)
                      .in_progress())

        login(self.portal, 'hugo.boss')
        self.assertTrue(IDeadlineModifier(task).is_modify_allowed())

    def test_modify_is_allowed_for_a_inbox_group_user_when_inbox_is_issuer(self):
        task = create(Builder('task')
                      .having(issuer='inbox:client1', responsible=TEST_USER_ID)
                      .in_progress())

        modifier = IDeadlineModifier(task)
        self.assertTrue(modifier.is_modify_allowed(include_agency=False))
        self.assertTrue(modifier.is_modify_allowed(include_agency=True))

    def test_modify_is_allowed_for_admin_on_a_open_task_as_agency(self):
        task = create(Builder('task')
                      .having(issuer='hugo.boss'))

        self.grant('Administrator')
        modifier = IDeadlineModifier(task)
        self.assertFalse(modifier.is_modify_allowed(include_agency=False))
        self.assertTrue(modifier.is_modify_allowed(include_agency=True))

    def test_modify_is_allowed_for_admin_on_a_in_progress_task_as_agency(self):
        task = create(Builder('task')
                      .having(issuer='hugo.boss')
                      .in_progress())

        self.grant('Administrator')
        modifier = IDeadlineModifier(task)
        self.assertFalse(modifier.is_modify_allowed(include_agency=False))
        self.assertTrue(modifier.is_modify_allowed(include_agency=True))

    def test_modify_is_allowed_for_issuing_org_unit_agency_member_as_agency(self):
        task = create(Builder('task')
                      .having(issuer=u'hugo.boss')
                      .in_progress())

        modifier = IDeadlineModifier(task)
        self.assertFalse(modifier.is_modify_allowed(include_agency=False))
        self.assertTrue(modifier.is_modify_allowed(include_agency=True))


class TestDeadlineModifier(FunctionalTestCase):

    def test_raise_unauthorized_when_mofication_is_not_allowed(self):
        task = create(Builder('task')
                      .having(issuer='hugo.boss',
                              deadline=datetime.date(2013, 1, 1))
                      .in_state('task-state-resolved'))

        with self.assertRaises(Unauthorized):
            IDeadlineModifier(task).modify_deadline(
                datetime.date(2013, 10, 1),
                'changed deadline',
                'task-transition-modify-deadline')
