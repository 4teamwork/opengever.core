from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.browser import edit_public_trial
from opengever.testing import FunctionalTestCase
from zExceptions import Unauthorized
from opengever.base.behaviors.classification import PUBLIC_TRIAL_PRIVATE


class TestEditPublicTrialHelperFunction(FunctionalTestCase):

    def setUp(self):
        super(TestEditPublicTrialHelperFunction, self).setUp()
        self.grant('Contributor')

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        self.document = create(Builder('document')
                               .with_dummy_content()
                               .within(dossier))

        self.can_edit = edit_public_trial.can_access_public_trial_edit_form

    def test_parent_of_content_needs_to_be_a_dossier(self):
        user = self.portal.portal_membership.getAuthenticatedMember()

        self.assertTrue(self.can_edit(user, self.document))

        with self.assertRaises(AssertionError):
            self.can_edit(user, self.document.aq_parent)

    def test_one_of_the_parents_needs_to_be_a_dossier(self):
        user = self.portal.portal_membership.getAuthenticatedMember()
        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        task = create(Builder('task').within(dossier))
        document = create(Builder('document')
                          .with_dummy_content()
                          .within(task))

        self.assertTrue(self.can_edit(user, document))

    def test_user_WITH_modify_permission_in_open_state_CAN_edit(self):
        user = self.portal.portal_membership.getAuthenticatedMember()

        self.assertTrue(self.can_edit(user, self.document))

    def test_user_WITHOUT_modify_permission_in_open_state_CANNOT_edit(self):
        user = create(Builder('user').with_roles('Contributor'))
        self.assertFalse(self.can_edit(user, self.document))

    def test_does_not_work_on_subdossier(self):
        user = self.portal.portal_membership.getAuthenticatedMember()
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))

        with self.assertRaises(AssertionError):
            self.can_edit(user, subdossier)


class TestEditPublicTrialForm(FunctionalTestCase):

    def setUp(self):
        super(TestEditPublicTrialForm, self).setUp()
        self.grant('Contributor')

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        self.document = create(Builder('document')
                               .with_dummy_content()
                               .within(dossier))

    @browsing
    def test_raise_aunauthorized_if_the_user_CANNOT_modify(self, browser):
        user = create(Builder('user').with_roles('Contributor'))

        with self.assertRaises(Unauthorized):
            browser.login(user.getId()).visit(self.document,
                                              view='edit_public_trial')

    @browsing
    def test_user_CAN_access_edit_form(self, browser):
        browser.login().visit(self.document, view='edit_public_trial')

        self.assertEquals(
            '{0}/edit_public_trial'.format(self.document.absolute_url()),
            browser.url)

        self.assertTrue(browser.css('#form-widgets-public_trial'),
                        'Public trial field is no available.')

    @browsing
    def test_user_CAN_modify_public_trial_information(self, browser):
        browser.login().visit(self.document, view='edit_public_trial')
        browser.fill({'Public Trial': PUBLIC_TRIAL_PRIVATE}).submit()

        self.assertEquals('private', self.document.public_trial)

    @browsing
    def test_user_submit_cancel_button(self, browser):
        browser.login().visit(self.document, view='edit_public_trial')
        browser.find('Cancel').click()
        self.assertEquals(self.document.absolute_url(), browser.url)
