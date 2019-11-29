from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from opengever.meeting.model import Proposal
from opengever.testing import IntegrationTestCase


VIEW_PERMISSIONS = (
    'Access contents information',
    'CMFEditions: Access previous versions',
    'View',
)


class TestSubmittedProposal(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_submitted_proposal_edit_allowed_when_submitted(self, browser):
        self.login(self.administrator, browser)
        proposal_model = self.submitted_proposal.load_model()
        self.assertEquals('submitted', proposal_model.workflow_state)
        browser.open(self.submitted_proposal)
        self.assertIn('Edit', editbar.contentviews())
        browser.open(self.submitted_proposal, view='edit')

    @browsing
    def test_submitted_proposal_edit_not_allowed_when_decided(self, browser):
        self.login(self.administrator, browser)
        proposal_model = self.submitted_proposal.load_model()
        proposal_model.workflow_state = 'decided'
        browser.open(self.submitted_proposal)
        self.assertNotIn('Edit', editbar.contentviews())
        with browser.expect_unauthorized():
            browser.open(self.submitted_proposal, view='edit')

    @browsing
    def test_submitted_proposal_can_be_rejected(self, browser):
        self.login(self.committee_responsible, browser)
        model = self.proposal.load_model()
        self.assertEqual(
            'opengever-meeting-committeecontainer/committee-1/submitted-proposal-1',
            model.submitted_physical_path)
        self.assertEqual(Proposal.STATE_SUBMITTED, self.proposal.get_state())
        self.assert_workflow_state('proposal-state-submitted', self.proposal)
        self.assertIsNotNone(self.proposal.date_of_submission)

        browser.visit(self.submitted_proposal, view='tabbedview_view-overview')
        browser.click_on('Reject')
        browser.fill({'Comment': u'Bitte \xfcberarbeiten'}).submit()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message(u'The proposal has been rejected successfully')

        self.assertIsNone(model.submitted_physical_path)
        self.assertIsNone(model.submitted_int_id)
        self.assertIsNone(model.submitted_admin_unit_id)
        self.assertIsNone(model.date_of_submission)
        self.assertEqual(Proposal.STATE_PENDING, self.proposal.get_state())
        self.assertIsNone(self.proposal.date_of_submission)
        self.assert_workflow_state('proposal-state-active', self.proposal)
        with self.assertRaises(KeyError):
            self.submitted_proposal

    @browsing
    def test_dossier_link_rendering_for_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        self.assertEqual(
            self.dossier.absolute_url(),
            browser.find(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung')
            .get('href'))

    def test_attributes_sort_order_for_submitted_proposal(self):
        self.login(self.committee_responsible)
        attributes = self.submitted_proposal.get_overview_attributes()
        self.assertEqual(
            [u'label_title',
             u'label_description',
             u'label_dossier',
             u'label_committee',
             u'label_meeting',
             u'label_issuer',
             u'proposal_document',
             u'label_workflow_state',
             u'label_decision_number'],
            [attribute.get('label') for attribute in attributes],
            )

    def test_sql_index_proposal_title_and_description_are_updated(self):
        # an agenda item is needed for this test
        self.login(self.committee_responsible)
        self.meeting.model.schedule_proposal(self.proposal.load_model())
        agenda_item = self.meeting.model.agenda_items[0]
        self.assertEquals(agenda_item.get_title(), agenda_item.proposal.submitted_title)

        agenda_item.set_title('New agenda item title')
        agenda_item.set_description('New agenda item description')

        self.assertEquals('New agenda item title', agenda_item.get_title())
        self.assertEquals('New agenda item title', agenda_item.proposal.submitted_title)

        self.assertEquals('New agenda item description', agenda_item.get_description())
        self.assertEquals('New agenda item description', agenda_item.proposal.submitted_description)

    def test_get_containing_dossier_for_submitted_proposal_if_on_same_admin_unit(self):
        self.login(self.committee_responsible)
        self.assertEqual(self.dossier,
                         self.submitted_proposal.get_containing_dossier())

    def test_get_none_for_containing_dossier_if_submitted_proposal_is_not_on_same_admin_unit(self):
        self.login(self.committee_responsible)
        self.proposal.load_model().admin_unit_id = u'another-client'
        self.assertIsNone(self.submitted_proposal.get_containing_dossier())

    @browsing
    def test_get_link_to_dossier_for_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open_html(self.submitted_proposal.get_dossier_link())
        self.assertEqual(
            self.dossier.title,
            browser.css('a').first.get('title'))
        self.assertEqual(
            self.dossier.absolute_url(),
            browser.css('a').first.get('href'))

    def test_get_link_returns_fallback_message_if_proposal_is_not_on_same_admin_unit(self):
        self.login(self.committee_responsible)
        self.proposal.load_model().admin_unit_id = u'another-client'
        self.assertEqual(
            u'label_dossier_not_available',
            self.submitted_proposal.get_dossier_link())

    @browsing
    def test_submitted_proposal_can_be_edited_in_browser(self, browser):
        self.login(self.committee_responsible, browser)
        browser.visit(self.submitted_proposal, view='edit')

        browser.fill({'Title': u'Submitted pr\xf6posal'}).save()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Changes saved')

        proposal = browser.context

        model = proposal.load_model()
        self.assertEqual(u'Submitted pr\xf6posal', model.submitted_title)

    @browsing
    def test_committee_member_can_view_proposal_document(self, browser):
        """The meeting_user is a CommitteeMember, who can access the proposal and
        its document read-only.
        """
        self.login(self.meeting_user, browser)
        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        self.assertTrue(browser.find(u'Vertr\xe4ge'))

        browser.open(self.submitted_proposal.get_proposal_document(), view='tabbedview_view-overview')
        expected_title = {'Title': u'Vertr\xe4ge'}
        self.assertDictContainsSubset(expected_title, dict(browser.css('.documentMetadata table').first.lists()))

    def test_committee_member_permissions_on_proposal_document(self):
        self.login(self.meeting_user)
        self.assert_has_permissions(
            VIEW_PERMISSIONS,
            self.submitted_proposal.get_proposal_document())

        self.assert_has_not_permissions(
            (
                'Modify portal content',
                'opengever.document: Checkout',
            ),
            self.submitted_proposal.get_proposal_document())

    def test_committee_responsible_can_edit_proposal_document(self):
        self.login(self.committee_responsible)
        self.assert_has_permissions(
            (
                'Access contents information',
                'CMFEditions: Access previous versions',
                'CMFEditions: Apply version control',
                'CMFEditions: Checkout to location',
                'CMFEditions: Manage versioning policies',
                'CMFEditions: Purge version',
                'CMFEditions: Revert to previous versions',
                'Change portal events',
                'Modify portal content',
                'View',
                'WebDAV Lock items',
                'WebDAV Unlock items',
                'WebDAV access',
                'opengever.document: Cancel',
                'opengever.document: Checkin',
                'opengever.document: Checkout',
            ),
            self.submitted_proposal.get_proposal_document())

    def test_committee_administrator_can_edit_proposal_document(self):
        self.login(self.administrator)
        self.assert_has_permissions(
            (
                'Access contents information',
                'CMFEditions: Access previous versions',
                'CMFEditions: Apply version control',
                'CMFEditions: Checkout to location',
                'CMFEditions: Manage versioning policies',
                'CMFEditions: Purge version',
                'CMFEditions: Revert to previous versions',
                'Change portal events',
                'Modify portal content',
                'View',
                'WebDAV Lock items',
                'WebDAV Unlock items',
                'WebDAV access',
                'opengever.document: Cancel',
                'opengever.document: Checkin',
                'opengever.document: Checkout',
            ),
            self.submitted_proposal.get_proposal_document())

    def test_access_to_mail_attached_to_proposal(self):
        with self.login(self.administrator):
            mail = create(Builder('mail').within(self.submitted_proposal))
            self.assert_has_permissions(VIEW_PERMISSIONS, mail,
                                        '(CommitteeAdministrator)')

        with self.login(self.committee_responsible):
            self.assert_has_permissions(VIEW_PERMISSIONS, mail,
                                        '(CommitteeResponsible)')

        with self.login(self.meeting_user):
            self.assert_has_permissions(VIEW_PERMISSIONS, mail,
                                        '(CommitteeMember)')

    @browsing
    def test_committee_member_should_not_be_able_to_reject_a_proposal(self, browser):
        """Regression test: committee members did see the "Reject" button,
        although it did not work.
        """
        self.login(self.meeting_user, browser)
        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        self.assertFalse(browser.find('Reject'))
