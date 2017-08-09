from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.model import Proposal
from opengever.meeting.proposal import ISubmittedProposal
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from opengever.testing import IntegrationTestCase
from plone import api


class TestProposalWithWord(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    @browsing
    def test_creating_proposal_from_proposal_template(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill(
            {'Title': u'Baugesuch Kreuzachkreisel',
             'Committee': u'Rechnungspr\xfcfungskommission',
             'Proposal template': u'Baugesuch',
             'Edit after creation': True}).save()
        statusmessages.assert_no_error_messages()
        self.assertIn('external_edit', browser.css('.redirector').first.text,
                      'External editor should have been triggered.')

        proposal = browser.context
        browser.open(proposal, view='tabbedview_view-overview')
        self.assertEquals(
            [['Title', u'Baugesuch Kreuzachkreisel'],
             ['Committee', u'Rechnungspr\xfcfungskommission'],
             ['Meeting', ''],
             ['Proposal document',
              'Proposal document Baugesuch Kreuzachkreisel'],
             ['State', 'Pending'],
             ['Decision number', '']],
            browser.css('table.listing').first.lists())

        browser.click_on('Proposal document Baugesuch Kreuzachkreisel')
        browser.open(browser.context, view='tabbedview_view-overview')
        self.assertDictContainsSubset(
            {'Title': u'Proposal document Baugesuch Kreuzachkreisel'},
            dict(browser.css('table.listing').first.lists()))

        self.assertEquals(
            'Word Content',
            proposal.get_proposal_document().file.open().read())

        self.assertFalse(
            is_officeconnector_checkout_feature_enabled(),
            'Office connector checkout feature is now active: this means'
            ' that the document will no longer be checked out in the proposal'
            ' creation wizard and therefore the assertion "document is checked'
            ' out" will therefore fail.')
        self.assertEquals(
            self.dossier_responsible.getId(),
            self.get_checkout_manager(
                proposal.get_proposal_document()).get_checked_out_by())

    @browsing
    def test_proposal_document_is_visible_on_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_word_proposal, view='tabbedview_view-overview')
        self.assertEquals(
            [['Title', u'\xc4nderungen am Personalreglement'],
             ['Committee', u'Rechnungspr\xfcfungskommission'],
             ['Dossier', u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
             ['Meeting', ''],
             ['Proposal document',
              u'Proposal document \xc4nderungen am Personalreglement'],
             ['State', 'Submitted'],
             ['Decision number', ''],
             ['Attachments', u'Vertr\xe4gsentwurf']],
            browser.css('table.listing').first.lists())

    @browsing
    def test_visible_fields_in_addform(self, browser):
        """When the "word implementation" feature is enabled,
        the "old" trix fields should disappear.
        """
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        hidden = ('Legal basis',
                  'Initial position',
                  'Proposed action',
                  'Decision draft',
                  'Publish in',
                  'Disclose to',
                  'Copy for attention')
        missing = tuple(set(hidden) - set(browser.forms['form'].field_labels))
        self.assertItemsEqual(hidden, missing)

    @browsing
    def test_word_proposal_can_be_submitted(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assertEqual(Proposal.STATE_PENDING,
                         self.draft_word_proposal.get_state())
        self.assertEqual('proposal-state-active',
                         api.content.get_state(self.draft_word_proposal))

        browser.open(self.draft_word_proposal, view='tabbedview_view-overview')
        browser.click_on('Submit')
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Proposal successfully submitted.')
        self.assertEqual(Proposal.STATE_SUBMITTED,
                         self.draft_word_proposal.get_state())
        self.assertEqual('proposal-state-submitted',
                         api.content.get_state(self.draft_word_proposal))

        self.login(self.administrator)
        model = self.draft_word_proposal.load_model()
        submitted_proposal = model.resolve_submitted_proposal()
        proposal_file = self.draft_word_proposal.get_proposal_document().file
        submitted_proposal_file = submitted_proposal.get_proposal_document().file
        with proposal_file.open() as expected:
            with submitted_proposal_file.open() as got:
                self.assertEquals(expected.read(), got.read())

    @browsing
    def test_document_of_draft_proposal_can_be_edited(self, browser):
        self.login(self.dossier_responsible, browser)
        document = self.draft_word_proposal.get_proposal_document()
        browser.open(document, view='edit')
        self.assertEquals('Edit Document', plone.first_heading(),
                          'Document should be editable.')

    @browsing
    def test_document_of_proposal_cannot_be_edited_when_submitted(self, browser):
        self.login(self.dossier_responsible, browser)
        document = self.word_proposal.get_proposal_document()
        with browser.expect_unauthorized():
            browser.open(document, view='edit')

    @browsing
    def test_document_of_rejected_proposal_can_be_edited(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_word_proposal, view='tabbedview_view-overview')
        browser.find('Reject').click()
        browser.fill({'Comment': u'Bitte \xfcberarbeiten'}).submit()

        self.login(self.dossier_responsible, browser)
        document = self.word_proposal.get_proposal_document()
        browser.open(self.word_proposal.get_proposal_document(), view='edit')
        browser.open(document, view='edit')
        self.assertEquals('Edit Document', plone.first_heading(),
                          'Document should be editable.')

    @browsing
    def test_prevent_trashing_proposal_document(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assertFalse(
            api.user.has_permission(
                'opengever.trash: Trash content',
                obj=self.word_proposal.get_proposal_document()),
            'The proposal document should not be trashable.')
        self.assertFalse(
            api.user.has_permission(
                'opengever.trash: Trash content',
                obj=self.draft_word_proposal.get_proposal_document()),
            'The proposal document should not be trashable.')

    @browsing
    def test_proposal_cannot_change_state_when_documents_checked_out(self, browser):
        self.login(self.dossier_responsible, browser)
        document = self.draft_word_proposal.get_proposal_document()
        self.checkout_document(document)
        self.assertTrue(self.draft_word_proposal.contains_checked_out_documents())
        browser.open(self.draft_word_proposal, view='tabbedview_view-overview')
        browser.click_on('Submit')
        statusmessages.assert_message(
            'Cannot change the state because the proposal'
            ' contains checked out documents.')

    def test_decide_not_allowed_when_documents_checked_out(self):
        """When deciding the proposal on the proposal model, the proposal
        document must already be checked in.
        This also applies to the current user: the auto-checkin-feature is
        the job of the agenda item controller, not of the proposal model.
        """
        self.login(self.committee_responsible)
        item = self.schedule_proposal(self.meeting,
                                      self.submitted_word_proposal)
        self.checkout_document(self.submitted_word_proposal.get_proposal_document())

        model = self.submitted_word_proposal.load_model()
        with self.assertRaises(ValueError) as cm:
            model.decide(item)

        self.assertEquals(
            'Cannot decide proposal when proposal document is checked out.',
            str(cm.exception))

    def test_generate_excerpt_copies_document_to_target(self):
        self.login(self.administrator)
        self.assertEquals(
            [],
            ISubmittedProposal(self.submitted_word_proposal).excerpts)

        with self.observe_children(self.meeting_dossier) as children:
            self.submitted_word_proposal.generate_excerpt(self.meeting_dossier)

        self.assertEquals(1, len(children['added']),
                          'An excerpt document should have been added to the'
                          ' meeting dossier.')

        # The document should contain a copy of the proposal document file.
        excerpt_document ,= children['added']
        self.assertEquals('Excerpt \xc3\x84nderungen am Personalreglement',
                          excerpt_document.Title())
        self.assertEquals(u'excerpt-anderungen-am-personalreglement.docx',
                          excerpt_document.file.filename)
        self.assertEquals(MIME_DOCX, excerpt_document.file.contentType)
        self.assertEquals(
            self.submitted_word_proposal.get_proposal_document().file.data,
            excerpt_document.file.data)

        # The excerpt document should be referenced as relation.
        excerpts = ISubmittedProposal(self.submitted_word_proposal).excerpts
        self.assertEquals(1, len(excerpts))
        relation, = excerpts
        self.assertEquals(excerpt_document, relation.to_object)
