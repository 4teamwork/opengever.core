from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase


class TestRisProposalTransitionSchedule(IntegrationTestCase):

    features = ('ris',)

    def setUp(self):
        super(TestRisProposalTransitionSchedule, self).setUp()
        with self.login(self.manager):
            self.ris_proposal = create(
                Builder('ris_proposal')
                .within(self.dossier)
                .having(document=self.document)
                .in_state('proposal-state-submitted')
            )

    @browsing
    def test_proposal_schedule_api_transition_sets_wokflow_state(self, browser):
        self.login(self.dossier_responsible, browser)

        url = '{}/@workflow/proposal-transition-schedule'.format(
            self.ris_proposal.absolute_url())
        browser.open(url, method='POST', headers=self.api_headers)

        self.assert_workflow_state('proposal-state-scheduled', self.ris_proposal)

    @browsing
    def test_proposal_schedule_api_transition_requires_modify_portal_content(self, browser):
        with self.login(self.regular_user):
            RoleAssignmentManager(self.portal).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )
            RoleAssignmentManager(self.dossier).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )

        self.login(self.reader_user, browser)
        url = '{}/@workflow/proposal-transition-schedule'.format(
            self.ris_proposal.absolute_url())
        with browser.expect_http_error(code=400):
            browser.open(url, method='POST', headers=self.api_headers)

    @browsing
    def test_proposal_schedule_debug_action_sets_wokflow_state(self, browser):
        self.login(self.manager, browser)

        browser.open(self.ris_proposal)
        editbar.menu_option('Actions', 'Schedule (Manager: Debug)').click()

        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Item state changed.')

        self.assert_workflow_state('proposal-state-scheduled', self.ris_proposal)
