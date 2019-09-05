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
import json


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
        self.set_workflow_state('dossier-state-resolved', self.resolvable_subdossier)
        self.deactivate(self.resolvable_dossier, browser)
        self.assert_workflow_state('dossier-state-active', self.resolvable_dossier)
        expected_msgs = [u"The Dossier can\'t be deactivated, the subdossier"
                         u" Resolvable Subdossier is already resolved."]
        self.assert_errors(self.resolvable_dossier, browser, expected_msgs)

    @browsing
    def test_fails_with_checked_out_documents(self, browser):
        self.login(self.dossier_responsible, browser)
        self.checkout_document(self.resolvable_document)
        self.deactivate(self.resolvable_dossier, browser)
        self.assert_workflow_state('dossier-state-active', self.resolvable_dossier)
        expected_msgs = [u"The Dossier can't be deactivated, not all "
                         u"contained documents are checked in."]
        self.assert_errors(self.resolvable_dossier, browser, expected_msgs)

    @browsing
    def test_not_possible_with_not_closed_tasks(self, browser):
        self.login(self.dossier_responsible, browser)
        task = create(Builder('task')
                      .having(responsible_client='fa',
                              responsible=self.regular_user.getId(),
                              issuer=self.dossier_responsible.getId())
                      .within(self.empty_dossier)
                      .in_state('task-state-in-progress'))

        self.deactivate(self.empty_dossier, browser)
        self.assert_workflow_state('dossier-state-active', self.empty_dossier)
        expected_msgs = [u"The Dossier can't be deactivated, not all contained"
                         u" tasks are in a closed state."]
        self.assert_errors(self.empty_dossier, browser, expected_msgs)

        self.set_workflow_state('task-state-tested-and-closed', task)
        self.deactivate(self.empty_dossier, browser)
        self.assert_workflow_state('dossier-state-inactive', self.empty_dossier)

    @browsing
    def test_not_possible_with_active_proposals(self, browser):
        self.login(self.committee_responsible, browser)
        proposal = create(Builder('proposal').within(self.empty_dossier)
                                             .having(committee=self.committee))

        self.login(self.dossier_responsible, browser)

        self.deactivate(self.empty_dossier, browser)
        self.assert_workflow_state('dossier-state-active', self.empty_dossier)

        expected_msgs = [u"The Dossier can't be deactivated, it contains "
                         u"active proposals."]
        self.assert_errors(self.empty_dossier, browser, expected_msgs)

        api.content.transition(proposal, 'proposal-transition-cancel')
        self.deactivate(self.empty_dossier, browser)
        self.assert_workflow_state('dossier-state-inactive', self.empty_dossier)

    @browsing
    def test_recursively_deactivate_subdossier(self, browser):
        self.login(self.secretariat_user, browser)
        self.deactivate(self.resolvable_dossier, browser, use_editbar=True)
        statusmessages.assert_no_error_messages()
        self.assert_workflow_state('dossier-state-inactive', self.resolvable_subdossier)
        self.assert_workflow_state('dossier-state-inactive', self.resolvable_dossier)

    @browsing
    def test_already_inactive_subdossier_will_be_ignored(self, browser):
        self.login(self.secretariat_user, browser)
        self.deactivate(self.resolvable_subdossier, browser, use_editbar=True)
        self.assert_workflow_state('dossier-state-inactive', self.resolvable_subdossier)

        self.deactivate(self.resolvable_dossier, browser, use_editbar=True)
        statusmessages.assert_no_error_messages()
        self.assert_workflow_state('dossier-state-inactive', self.resolvable_dossier)
        self.assert_workflow_state('dossier-state-inactive', self.resolvable_subdossier)

    @browsing
    def test_sets_end_date_to_current_date(self, browser):
        self.login(self.secretariat_user, browser)
        with freeze(datetime(2016, 3, 29)):
            self.deactivate(self.resolvable_dossier, browser, use_editbar=True)

        self.assert_end_date(self.resolvable_dossier, date(2016, 3, 29))

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


class TestDossierDeactivationRESTAPI(TestDossierDeactivation):

    def deactivate(self, dossier, browser, use_editbar=False, payload=None):
        browser.raise_http_errors = False
        url = dossier.absolute_url() + '/@workflow/dossier-transition-deactivate'
        kwargs = {'method': 'POST',
                  'headers': self.api_headers}
        if payload is not None:
            kwargs['data'] = json.dumps(payload)
        browser.open(url, **kwargs)

    def assert_errors(self, dossier, browser, error_msgs):
        self.assertEquals(400, browser.status_code)
        self.assertEquals(
            {u'error':
                {u'message': u'',
                 u'errors': error_msgs,
                 u'type': u'PreconditionsViolated'}},
            browser.json)
        expected_url = dossier.absolute_url() + \
            '/@workflow/dossier-transition-deactivate'
        self.assertEquals(expected_url, browser.url)

    @browsing
    def test_deactivating_dossier_non_recursively_is_forbidden(self, browser):
        self.login(self.regular_user, browser)
        payload = {'include_children': False}
        self.deactivate(self.empty_dossier, browser, payload=payload)
        self.assertEqual(
            {u'error': {
                u'message': u'Deactivating dossier must always be recursive',
                u'type': u'Bad Request'}},
            browser.json)
        self.assert_workflow_state('dossier-state-active', self.empty_dossier)
