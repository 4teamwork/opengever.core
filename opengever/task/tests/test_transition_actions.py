from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
import re


URL_WIHOUT_TOKEN_RE = re.compile(r'(.*)([\?, &]_authenticator=.*)')


class BaseTransitionActionTestMixin(object):

    def assert_action(self, browser, expected):
        url = URL_WIHOUT_TOKEN_RE.match(browser.url).groups()[0]
        self.assertEquals(expected, url)


class BaseTransitionActionFunctionalTest(FunctionalTestCase, BaseTransitionActionTestMixin):

    def do_transition(self, browser, task):
        browser.login().open(task)
        browser.css('#workflow-transition-{}'.format(self.transition)).first.click()


class TestDelegateAction(BaseTransitionActionFunctionalTest):
    transition = 'task-transition-delegate'

    @browsing
    def test_is_delegate_form(self, browser):
        task = create(Builder('task').in_state('task-state-in-progress'))
        self.do_transition(browser, task)
        self.assert_action(browser, 'http://nohost/plone/task-1/@@delegate_recipients')
        self.assertEquals('Delegate task', browser.css('.documentFirstHeading').first.text)


class TestModifyDeadlineAction(BaseTransitionActionFunctionalTest):
    transition = 'task-transition-modify-deadline'

    @browsing
    def test_is_modify_deadline_form(self, browser):
        task = create(Builder('task').in_state('task-state-in-progress'))
        self.do_transition(browser, task)
        self.assertEquals('Modify deadline', browser.css('.documentFirstHeading').first.text)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/@@modify_deadline?form.widgets.transition=task-transition-modify-deadline',
            )


class TestReOpenAction(BaseTransitionActionFunctionalTest):
    transition = 'task-transition-cancelled-open'

    @browsing
    def test_is_responseform(self, browser):
        task = create(Builder('task').in_state('task-state-cancelled'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-cancelled-open',
            )


class TestReassignAction(BaseTransitionActionFunctionalTest):
    transition = 'task-transition-reassign'

    @browsing
    def test_is_reassign_form(self, browser):
        task = create(Builder('task'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/@@assign-task?form.widgets.transition=task-transition-reassign',
            )


class TestCancelAction(BaseTransitionActionFunctionalTest):
    transition = 'task-transition-open-cancelled'

    @browsing
    def test_is_responseform(self, browser):
        task = create(Builder('task'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-open-cancelled',
            )


class TestRejectAction(BaseTransitionActionFunctionalTest):

    transition = 'task-transition-open-rejected'

    @browsing
    def test_is_responseform(self, browser):
        task = create(Builder('task'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-open-rejected',
            )


class TestInProgressResolveAction(BaseTransitionActionFunctionalTest):
    transition = 'task-transition-in-progress-resolved'

    @browsing
    def test_is_responseform_for_unidirectional_tasks(self, browser):
        task = create(Builder('task')
                      .having(task_type='information')
                      .in_state('task-state-in-progress'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-in-progress-resolved',
            )

    @browsing
    def test_is_responseform_for_bidirectional_orgunit_intern_tasks(self, browser):
        task = create(Builder('task')
                      .in_state('task-state-in-progress'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-in-progress-resolved',
            )

    @browsing
    def test_is_complete_successor_form_for_successors(self, browser):
        predecessor = create(Builder('task'))
        dossier = create(Builder('dossier'))
        task = create(Builder('task')
                      .within(dossier)
                      .having(task_type='comment')
                      .in_state('task-state-in-progress')
                      .successor_from(predecessor))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/dossier-1/task-2/@@complete_successor_task?transition=task-transition-in-progress-resolved',
            )

    @browsing
    def test_is_responseform_for_forwarding_successors(self, browser):
        forwarding = create(Builder('forwarding'))
        task = create(Builder('task')
                      .in_state('task-state-in-progress')
                      .successor_from(forwarding))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-in-progress-resolved',
            )


class TestOpenResolveAction(BaseTransitionActionFunctionalTest):

    transition = 'task-transition-open-resolved'

    @browsing
    def test_is_responseform(self, browser):
        task = create(Builder('task'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-open-resolved',
            )


class TestInProgressTestedAndClosedAction(BaseTransitionActionFunctionalTest):

    transition = 'task-transition-in-progress-tested-and-closed'
    task_type = 'direct-execution'

    @browsing
    def test_is_responseform_for_non_successor(self, browser):
        task = create(Builder('task')
                      .having(task_type=self.task_type)
                      .in_state('task-state-in-progress'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-in-progress-tested-and-closed',
            )

    @browsing
    def test_is_complete_successor_form_for_successors(self, browser):
        predecessor = create(Builder('task'))
        dossier = create(Builder('dossier'))
        task = create(Builder('task')
                      .within(dossier)
                      .having(task_type=self.task_type)
                      .in_state('task-state-in-progress')
                      .successor_from(predecessor))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/dossier-1/task-2/@@complete_successor_task'
            '?transition=task-transition-in-progress-tested-and-closed',
            )

    @browsing
    def test_is_responseform_for_forwarding_successors(self, browser):
        forwarding = create(Builder('forwarding'))
        task = create(Builder('task')
                      .having(task_type=self.task_type)
                      .in_state('task-state-in-progress')
                      .successor_from(forwarding))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-in-progress-tested-and-closed',
            )


class TestAccept(BaseTransitionActionFunctionalTest):

    transition = 'task-transition-open-in-progress'

    def setUp(self):
        super(TestAccept, self).setUp()
        additional = create(Builder('admin_unit').id(u'additional'))
        create(Builder('org_unit')
               .id(u'additional')
               .having(admin_unit=additional)
               .with_default_groups()
               .assign_users([self.user], to_inbox=False))

    @browsing
    def test_is_responseform_for_adminunit_intern_tasks(self, browser):
        task = create(Builder('task')
                      .having(responsible_client='client1'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-open-in-progress',
            )

    @browsing
    def test_is_accept_wizzard_for_task_assigned_to_foreign_adminunit(self, browser):
        task = create(Builder('task')
                      .having(responsible_client='additional'))
        self.do_transition(browser, task)

        self.assert_action(
            browser,
            'http://nohost/plone/task-1/@@accept_choose_method',
            )


class TestOpenToClose(BaseTransitionActionFunctionalTest):

    transition = 'task-transition-open-tested-and-closed'

    def setUp(self):
        super(TestOpenToClose, self).setUp()
        additional = create(Builder('admin_unit').id(u'additional'))
        create(Builder('org_unit')
               .id(u'additional')
               .having(admin_unit=additional)
               .with_default_groups()
               .assign_users([self.user], to_inbox=False))

    @browsing
    def test_is_addform_for_bidirectional_tasks(self, browser):
        task = create(Builder('task')
                      .having(task_type='comment'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-open-tested-and-closed',
            )

    @browsing
    def test_is_addform_for_unidirectional_adminunit_intern_tasks(self, browser):
        task = create(Builder('task')
                      .having(task_type='information'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-open-tested-and-closed',
            )

    @browsing
    def test_is_responseform_for_unidirectional_tasks_on_foreign_admin_unit_without_documents(self, browser):
        task = create(Builder('task')
                      .having(task_type='information',
                              responsible_client='additional'))
        self.do_transition(browser, task)

        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-open-tested-and-closed',
            )

    @browsing
    def test_is_closetask_wizard_for_unidirectional_tasks_on_foreign_admin_unit_with_documents(self, browser):
        task = create(Builder('task')
                      .having(task_type='information',
                              responsible_client='additional'))
        create(Builder('document').within(task))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/@@close-task-wizard_select-documents',
            )


class TestReworkAction(BaseTransitionActionFunctionalTest):

    transition = 'task-transition-resolved-in-progress'

    @browsing
    def test_is_addform(self, browser):
        task = create(Builder('task').in_state('task-state-resolved'))
        self.do_transition(browser, task)
        self.assert_action(
            browser,
            'http://nohost/plone/task-1/addresponse?form.widgets.transition=task-transition-resolved-in-progress',
            )
