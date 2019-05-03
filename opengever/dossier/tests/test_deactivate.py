from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testing import freeze
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.testing import IntegrationTestCase
from plone import api


class TestDossierDeactivation(IntegrationTestCase):

    def deactivate(self, dossier, browser, use_editbar=False):
        if use_editbar:
            browser.open(dossier)
            editbar.menu_option('Actions', 'dossier-transition-deactivate').click()
        else:
            browser.open(dossier, view='transition-deactivate',
                         send_authenticator=True)

    def assert_errors(self, dossier, browser, error_msgs):
        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(error_msgs, error_messages())

    def assert_end_date(self, dossier, end_date):
        self.assertEqual(end_date, IDossier(dossier).end)

    @browsing
    def test_fails_with_resolved_subdossier(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_workflow_state('dossier-state-resolved', self.subdossier)
        self.deactivate(self.dossier, browser)
        self.assert_workflow_state('dossier-state-active', self.dossier)
        expected_msgs = [u"The Dossier can't be deactivated, it contains "
                         u"active proposals.",
                         u"The Dossier can\'t be deactivated, the subdossier"
                         u" 2016 is already resolved.",
                         u"The Dossier can't be deactivated, not all contained"
                         u" tasks are in a closed state."]
        self.assert_errors(self.dossier, browser, expected_msgs)

    @browsing
    def test_fails_with_checked_out_documents(self, browser):
        self.login(self.dossier_responsible, browser)
        self.checkout_document(self.document)
        self.deactivate(self.dossier, browser)
        self.assert_workflow_state('dossier-state-active', self.dossier)
        expected_msgs = [u"The Dossier can't be deactivated, not all "
                         u"containeddocuments are checked in.",
                         u"The Dossier can't be deactivated, it contains "
                         u"active proposals.",
                         u"The Dossier can't be deactivated, not all contained"
                         u" tasks are in a closed state."]
        self.assert_errors(self.dossier, browser, expected_msgs)

    @browsing
    def test_not_possible_with_not_closed_tasks(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assert_workflow_state('task-state-in-progress', self.task)
        self.deactivate(self.dossier, browser)
        self.assert_workflow_state('dossier-state-active', self.dossier)
        expected_msgs = [u"The Dossier can't be deactivated, it contains "
                         u"active proposals.",
                         u"The Dossier can't be deactivated, not all contained"
                         u" tasks are in a closed state."]
        self.assert_errors(self.dossier, browser, expected_msgs)

    @browsing
    def test_not_possible_with_active_proposals(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assert_workflow_state('proposal-state-active', self.draft_proposal)
        self.deactivate(self.dossier, browser)
        self.assert_workflow_state('dossier-state-active', self.dossier)
        expected_msgs = [u"The Dossier can't be deactivated, it contains "
                         u"active proposals.",
                         u"The Dossier can't be deactivated, not all contained"
                         u" tasks are in a closed state."]
        self.assert_errors(self.dossier, browser, expected_msgs)

    @browsing
    def test_recursively_deactivate_subdossier(self, browser):
        self.login(self.secretariat_user, browser)
        subdossier = create(Builder('dossier').within(self.empty_dossier))
        self.deactivate(self.empty_dossier, browser, use_editbar=True)
        statusmessages.assert_no_error_messages()
        self.assert_workflow_state('dossier-state-inactive', self.empty_dossier)
        self.assert_workflow_state('dossier-state-inactive', subdossier)

    @browsing
    def test_already_inactive_subdossier_will_be_ignored(self, browser):
        self.login(self.secretariat_user, browser)
        subdossier = create(Builder('dossier').within(self.empty_dossier)
                            .in_state('dossier-state-inactive'))
        self.deactivate(self.empty_dossier, browser, use_editbar=True)
        statusmessages.assert_no_error_messages()
        self.assert_workflow_state('dossier-state-inactive', self.empty_dossier)
        self.assert_workflow_state('dossier-state-inactive', subdossier)

    @browsing
    def test_sets_end_date_to_current_date(self, browser):
        self.login(self.secretariat_user, browser)
        with freeze(datetime(2016, 3, 29)):
            self.deactivate(self.empty_dossier, browser, use_editbar=True)

        self.assert_end_date(self.empty_dossier, date(2016, 3, 29))

    @browsing
    def test_subdossiers_the_user_cannot_view_can_also_block_deactivation(self, browser):
        with self.login(self.dossier_manager):
            # Protect self.subsubdossier so it cannot be seen by an 'Editor' of self.subdossier
            self.assertFalse(getattr(self.subsubdossier, '__ac_local_roles_block__', False))
            dossier_protector = IProtectDossier(self.subsubdossier)
            dossier_protector.dossier_manager = self.dossier_manager.getId()
            dossier_protector.reading = [self.secretariat_user.getId()]
            dossier_protector.protect()
            self.assertTrue(getattr(self.subsubdossier, '__ac_local_roles_block__', False))
            self.assertFalse(
                api.user.has_permission('View', user=self.regular_user, obj=self.subsubdossier),
                'This test does not actually test what it says on the tin, if self.regular_user can see self.subsubdossier.',
            )

            # Grant self.regular_user 'Editor' on self.subdossier so the action to deactivate is presented to the user
            RoleAssignmentManager(self.subdossier).add_or_update_assignment(
                SharingRoleAssignment(self.regular_user.getId(), ['Reader', 'Contributor', 'Editor']))

        self.login(self.regular_user, browser)
        self.deactivate(self.subdossier, browser)
        expected_msgs = [u"The Dossier 2016 contains a subdossier "
                         u"which can't be deactivated by the user."]
        self.assert_errors(self.subdossier, browser, expected_msgs)
