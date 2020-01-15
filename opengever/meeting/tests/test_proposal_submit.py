from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import date
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseContainer
from opengever.meeting.model import Committee
from opengever.meeting.model import Proposal
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestProposalSubmit(IntegrationTestCase):

    features = (
        'meeting',
    )

    def _assert_proposal_submitted_correctly(self, browser):
        proposal_model = self.draft_proposal.load_model()

        self.assertEqual(Proposal.STATE_SUBMITTED, self.draft_proposal.get_state())
        self.assert_workflow_state('proposal-state-submitted', self.draft_proposal)
        self.assertEqual(date.today(), self.draft_proposal.date_of_submission)

        # submitted proposal created
        self.login(self.committee_responsible, browser)
        self.assertEqual(u'opengever-meeting-committeecontainer'
                         u'/committee-2/submitted-proposal-2',
                         proposal_model.submitted_physical_path)
        submitted_proposal = self.portal.restrictedTraverse(
            proposal_model.submitted_physical_path.encode('utf-8'))
        self.assertEqual(self.empty_committee,
                         aq_parent(aq_inner(submitted_proposal)))
        self.assertEqual(date.today(), submitted_proposal.date_of_submission)

        # model synced
        self.assertEqual(proposal_model, submitted_proposal.load_model())
        self.assertEqual(Oguid.for_object(submitted_proposal),
                         proposal_model.submitted_oguid)
        self.assertEqual('submitted', proposal_model.workflow_state)
        self.assertEqual(u'Antrag f\xfcr Kreiselbau',
                         proposal_model.submitted_title)
        self.assertEqual(date.today(), proposal_model.date_of_submission)

        # document copied
        self.assertEqual(1, len(submitted_proposal.get_documents()))
        submitted_document = submitted_proposal.get_documents()[0]
        self.assertEqual(self.document.Title(), submitted_document.Title())
        self.assertEqual(self.document.file.filename,
                         submitted_document.file.filename)

        self.assertSubmittedDocumentCreated(self.draft_proposal, self.document)

        # document should have custom lock message
        browser.open(submitted_document)
        statusmessages.assert_message(
            u'This document has been submitted as a copy of Vertr\xe4gsentwurf and '
            u'cannot be edited directly. Unlock')
        self.assertEqual(
            self.document.absolute_url(),
            browser.css('.portalMessage.info a').first.get('href'))

    @browsing
    def test_api_proposal_submit_transition(self, browser):
        self.login(self.dossier_responsible, browser)
        self.add_related_item(self.draft_proposal, self.document)

        data = {'text': 'Fertig!'}
        url = '{}/@workflow/proposal-transition-submit'.format(
            self.draft_proposal.absolute_url())
        browser.open(url, method='POST', data=json.dumps(data),
                     headers=self.api_headers)

        proposal_history = IResponseContainer(self.draft_proposal)
        proposal_submitted = proposal_history.list()[-2]

        self.assertEqual(u'Fertig!', proposal_submitted.text)
        self.assertEqual(u'submitted', proposal_submitted.response_type)

        doc_submitted = proposal_history.list()[-1]
        self.assertEqual(u'document_submitted', doc_submitted.response_type)

        self._assert_proposal_submitted_correctly(browser)

    @browsing
    def test_proposal_submission_works_correctly(self, browser):
        self.login(self.dossier_responsible, browser)
        self.add_related_item(self.draft_proposal, self.document)

        proposal_model = self.draft_proposal.load_model()
        self.assertIsNone(proposal_model.submitted_physical_path)
        self.assertEqual(Proposal.STATE_PENDING, self.draft_proposal.get_state())
        self.assert_workflow_state('proposal-state-active', self.draft_proposal)

        self.assertIsNone(self.draft_proposal.date_of_submission)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-submit")
        browser.click_on("Confirm")
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Review state changed successfully.')

        self._assert_proposal_submitted_correctly(browser)

    @browsing
    def test_proposal_can_not_be_submitted_when_committee_is_inactive(self, browser):
        self.login(self.committee_responsible)
        self.empty_committee.load_model().deactivate()
        self.assertEqual(Committee.STATE_INACTIVE,
                         self.empty_committee.load_model().get_state())

        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        button = browser.find("proposal-transition-submit")
        self.assertFalse(button)

    @browsing
    def test_resubmit_rejected_proposal_with_mail_attachments(self, browser):
        with self.login(self.dossier_responsible, browser):
            self.draft_proposal.relatedItems.append(
                self.as_relation_value(self.mail_eml))

            browser.visit(self.draft_proposal, view='tabbedview_view-overview')
            browser.click_on("proposal-transition-submit")
            browser.click_on('Confirm')

            submitted_proposal = self.draft_proposal.load_model().resolve_submitted_proposal()

        with self.login(self.committee_responsible, browser):
            browser.visit(submitted_proposal, view='tabbedview_view-overview')
            browser.click_on('Reject')
            browser.click_on('Confirm')

        with self.login(self.dossier_responsible, browser):
            browser.visit(self.draft_proposal, view='tabbedview_view-overview')
            browser.click_on("proposal-transition-submit")
            browser.click_on('Confirm')

            statusmessages.assert_message('Review state changed successfully.')

    @browsing
    def test_proposal_can_be_submitted_without_permission_on_commitee(self, browser):
        self.login(self.dossier_responsible, browser)
        # https://github.com/4teamwork/opengever.ftw/issues/41
        self.assertFalse(getSecurityManager().checkPermission(
            'View', self.draft_proposal.get_committee()))
        self.assertEqual(Proposal.STATE_PENDING, self.draft_proposal.get_state())
        browser.visit(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-submit")
        browser.click_on("Confirm")
        self.assertEqual(Proposal.STATE_SUBMITTED, self.draft_proposal.get_state())
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Review state changed successfully.')
        self.assertEqual('proposal-state-submitted',
                         api.content.get_state(self.draft_proposal))

        self.login(self.administrator)
        model = self.draft_proposal.load_model()
        submitted_proposal = model.resolve_submitted_proposal()
        proposal_file = self.draft_proposal.get_proposal_document().file
        submitted_proposal_file = submitted_proposal.get_proposal_document().file
        with proposal_file.open() as expected:
            with submitted_proposal_file.open() as got:
                self.assertEquals(expected.read(), got.read())

    def test_is_submission_allowed(self):
        self.login(self.administrator)
        self.assertFalse(self.draft_proposal.is_submit_additional_documents_allowed())

        self.assertTrue(self.proposal.is_submit_additional_documents_allowed())

        # these transitions are not exposed on the proposal side
        proposal_model = self.proposal.load_model()
        proposal_model.execute_transition('submitted-scheduled')
        self.assertTrue(self.proposal.is_submit_additional_documents_allowed())

        proposal_model.execute_transition('scheduled-decided')
        self.assertFalse(self.proposal.is_submit_additional_documents_allowed())
