from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase


class TestRisProposalTransitionUnscheduleToDossier(IntegrationTestCase):

    features = ('ris',)

    def setUp(self):
        super(TestRisProposalTransitionUnscheduleToDossier, self).setUp()
        with self.login(self.manager):
            self.ris_proposal = create(
                Builder('ris_proposal')
                .within(self.dossier)
                .having(document=self.document)
                .in_state('proposal-state-scheduled')
            )

    @browsing
    def test_proposal_unschedule_to_dossier_api_transition_sets_wokflow_state(self, browser):
        self.login(self.dossier_responsible, browser)

        url = '{}/@workflow/proposal-transition-unschedule-to-dossier'.format(
            self.ris_proposal.absolute_url())
        browser.open(url, method='POST', headers=self.api_headers)

        self.assert_workflow_state('proposal-state-active', self.ris_proposal)

    @browsing
    def test_proposal_unschedule_to_dossier_api_transition_requires_modify_portal_content(self, browser):
        with self.login(self.regular_user):
            RoleAssignmentManager(self.portal).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )
            RoleAssignmentManager(self.dossier).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )

        self.login(self.reader_user, browser)
        url = '{}/@workflow/proposal-transition-unschedule-to-dossier'.format(
            self.ris_proposal.absolute_url())
        with browser.expect_http_error(code=400):
            browser.open(url, method='POST', headers=self.api_headers)
