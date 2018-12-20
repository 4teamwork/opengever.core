from ftw.testbrowser import browsing
from opengever.base.behaviors.classification import PUBLIC_TRIAL_PRIVATE
from opengever.base.browser import edit_public_trial
from opengever.testing import IntegrationTestCase
from plone import api
from zExceptions import Unauthorized


class TestEditPublicTrialHelperFunction(IntegrationTestCase):

    def setUp(self):
        super(TestEditPublicTrialHelperFunction, self).setUp()
        self.can_edit = edit_public_trial.can_access_public_trial_edit_form

    def test_parent_of_content_needs_to_be_a_dossier(self):
        self.login(self.regular_user)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        user = api.user.get_current()
        self.assertTrue(self.can_edit(user, self.document))

        with self.assertRaises(AssertionError):
            self.can_edit(user, self.document.aq_parent)

    def test_one_of_the_parents_needs_to_be_a_dossier(self):
        self.login(self.regular_user)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        self.assertTrue(self.can_edit(api.user.get_current(), self.taskdocument))

    def test_user_CANNOT_edit_when_parent_dossier_is_inactive(self):
        self.login(self.regular_user)
        self.set_workflow_state('dossier-state-inactive', self.dossier)

        self.assertFalse(self.can_edit(api.user.get_current(), self.document))

    def test_user_WITH_modify_permission_in_open_state_CAN_edit(self):
        self.login(self.regular_user)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        self.assertTrue(self.can_edit(api.user.get_current(), self.document))

    def test_user_WITHOUT_modify_permission_in_open_state_CANNOT_edit(self):
        self.login(self.regular_user)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        self.assertFalse(self.can_edit(self.reader_user, self.document))

    def test_does_not_work_on_subdossier(self):
        self.login(self.regular_user)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        with self.assertRaises(AssertionError):
            self.can_edit(api.user.get_current(), self.subdossier)


class TestEditPublicTrialForm(IntegrationTestCase):

    @browsing
    def test_raise_aunauthorized_if_the_user_CANNOT_modify(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        self.login(self.reader_user, browser=browser)
        with self.assertRaises(Unauthorized):
            browser.visit(self.document, view='edit_public_trial')

    @browsing
    def test_user_CAN_access_edit_form(self, browser):
        self.login(self.regular_user, browser=browser)
        self.login(self.administrator, browser=browser)

        self.set_workflow_state('dossier-state-resolved', self.dossier)
        browser.visit(self.document, view='edit_public_trial')

        self.assertEquals(
            '{0}/edit_public_trial'.format(self.document.absolute_url()),
            browser.url)

        self.assertTrue(browser.css('#form-widgets-public_trial'),
                        'Public trial field is no available.')

    @browsing
    def test_user_CAN_modify_public_trial_information(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.document, view='edit_public_trial')
        browser.fill({'Public Trial': PUBLIC_TRIAL_PRIVATE}).submit()

        self.assertEquals('private', self.document.public_trial)

    @browsing
    def test_user_CAN_modify_public_trial_statement(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.visit(self.document, view='edit_public_trial')
        browser.fill({'Public trial statement': 'Foo statement'}).submit()

        self.assertEquals('Foo statement',
                          self.document.public_trial_statement)

    @browsing
    def test_user_submit_cancel_button(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.visit(self.document, view='edit_public_trial')
        browser.find('Cancel').click()
        self.assertEquals(self.document.absolute_url(), browser.url)
