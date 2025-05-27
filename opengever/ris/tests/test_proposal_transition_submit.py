from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase
import json


class TestRisProposalTransitionSubmit(IntegrationTestCase):

    features = ('ris',)

    def setUp(self):
        super(TestRisProposalTransitionSubmit, self).setUp()
        with self.login(self.manager):
            self.ris_proposal = create(
                Builder('ris_proposal')
                .within(self.dossier)
                .having(document=self.document)
            )

    @browsing
    def test_proposal_submit_action_redirects_to_ris(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.ris_proposal)
        browser.allow_redirects = False
        editbar.menu_option('Actions', 'Submit').click()

        self.assertEqual(302, browser.status_code)
        self.assertEqual(
            'http://ris.example.com/spv/antrag-einreichen?context={}'.format(
                self.ris_proposal.absolute_url()
            ),
            browser.headers['location']
        )

    @browsing
    def test_proposal_submit_api_transition_sets_wokflow_state(self, browser):
        self.login(self.dossier_responsible, browser)

        url = '{}/@workflow/proposal-transition-submit'.format(
            self.ris_proposal.absolute_url())
        browser.open(url, method='POST', headers=self.api_headers)

        self.assert_workflow_state('proposal-state-submitted', self.ris_proposal)

    @browsing
    def test_proposal_submit_api_transition_requires_modify_portal_content(self, browser):
        with self.login(self.regular_user):
            RoleAssignmentManager(self.portal).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )
            RoleAssignmentManager(self.dossier).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )

        self.login(self.reader_user, browser)
        url = '{}/@workflow/proposal-transition-submit'.format(
            self.ris_proposal.absolute_url())
        with browser.expect_http_error(code=400):
            browser.open(url, method='POST', headers=self.api_headers)

    @browsing
    def test_proposal_submit_debug_action_sets_wokflow_state(self, browser):
        self.login(self.manager, browser)

        browser.open(self.ris_proposal)
        editbar.menu_option('Actions', 'Submit (Manager: Debug)').click()

        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Item state changed.')

        self.assert_workflow_state('proposal-state-submitted', self.ris_proposal)

    @browsing
    def test_can_submit_attachments_to_submitted_proposal(self, browser):
        self.login(self.manager, browser)
        ris_proposal = create(
            Builder('ris_proposal')
            .within(self.dossier)
            .having(document=self.document)
            .in_state('proposal-state-submitted')
        )
        attachment_1 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'proposal attachment 1')
        )
        attachment_2 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'proposal attachment 2')
        )

        # assert ris proposal has no attachments
        self.assertEqual(len(ris_proposal.attachments), 0)
        data = json.dumps({
            "attachments": [
                attachment_1.absolute_url(),
                attachment_2.absolute_url()
            ]
        })
        # patch request to update attachments
        browser.open(
            ris_proposal.absolute_url(),
            data,
            method='PATCH',
            headers=self.api_headers
        )
        # assert ris proposal attachments after patch update request
        self.assertEqual(len(ris_proposal.attachments), 2)
