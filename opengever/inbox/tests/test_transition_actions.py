from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.task.tests.test_transition_actions import BaseTransitionActionFunctionalTest


class TestAcceptAction(BaseTransitionActionFunctionalTest):
    transition = 'forwarding-transition-accept'

    def setUp(self):
        super(TestAcceptAction, self).setUp()

        additional = create(Builder('admin_unit').id(u'additional'))
        create(Builder('org_unit')
               .id(u'additional')
               .having(admin_unit=additional)
               .with_default_groups()
               .assign_users([self.user], to_inbox=False))

    @browsing
    def test_is_accept_wizzard(self, browser):
        forwarding = create(Builder('forwarding')
                      .having(responsible_client='additional'))
        self.do_transition(browser, forwarding)
        self.assert_action(browser, 'http://nohost/plone/forwarding-1/@@accept_choose_method')


class TestRefuseAction(BaseTransitionActionFunctionalTest):
    transition = 'forwarding-transition-refuse'

    def setUp(self):
        super(TestRefuseAction, self).setUp()

        additional = create(Builder('admin_unit').id(u'additional'))
        create(Builder('org_unit')
               .id(u'additional')
               .having(admin_unit=additional)
               .with_default_groups()
               .assign_users([self.user], to_inbox=False))

    @browsing
    def test_is_refuse_form(self, browser):
        forwarding = create(Builder('forwarding')
                      .having(responsible_client='additional'))
        self.do_transition(browser, forwarding)
        self.assert_action(
            browser,
            'http://nohost/plone/forwarding-1/@@refuse-task?form.widgets.transition=forwarding-transition-refuse',
            )


class TestAssignToDossierAction(BaseTransitionActionFunctionalTest):
    transition = 'forwarding-transition-assign-to-dossier'

    @browsing
    def test_is_assign_wizzard(self, browser):
        forwarding = create(Builder('forwarding'))
        self.do_transition(browser, forwarding)
        self.assert_action(browser, 'http://nohost/plone/forwarding-1/@@assign_choose_method')


class TestReassignToDossierAction(BaseTransitionActionFunctionalTest):
    transition = 'forwarding-transition-reassign'

    @browsing
    def test_is_assign_task_form(self, browser):
        forwarding = create(Builder('forwarding'))
        self.do_transition(browser, forwarding)
        self.assert_action(
            browser,
            'http://nohost/plone/forwarding-1/@@assign-task?form.widgets.transition=forwarding-transition-reassign',
            )


class TestReassignRefuseAction(BaseTransitionActionFunctionalTest):

    transition = 'forwarding-transition-reassign-refused'

    @browsing
    def test_is_assign_fowarding_form(self, browser):
        forwarding = create(Builder('forwarding')
                            .in_state('forwarding-state-refused'))
        self.do_transition(browser, forwarding)
        self.assert_action(
            browser,
            'http://nohost/plone/forwarding-1/@@assign-forwarding'
            '?form.widgets.transition=forwarding-transition-reassign-refused',
            )


class TestCloseAction(BaseTransitionActionFunctionalTest):

    transition = 'forwarding-transition-close'

    @browsing
    def test_is_assign_fowarding_form(self, browser):
        forwarding = create(Builder('forwarding'))
        self.do_transition(browser, forwarding)
        self.assert_action(browser, 'http://nohost/plone/forwarding-1/@@close-forwarding')
