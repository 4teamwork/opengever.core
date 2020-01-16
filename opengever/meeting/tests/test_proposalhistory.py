from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser as default_browser
from ftw.testbrowser import browsing
from opengever.meeting.model import SubmittedDocument
from opengever.testing import IntegrationTestCase
from plone import api
from plone.namedfile.file import NamedBlobFile
from plone.protect import createToken
from plone.uuid.interfaces import IUUID


class TestIntegrationProposalHistory(IntegrationTestCase):

    features = (
        'meeting',
        )

    def open_overview(self, browser, proposal=None):
        proposal = proposal or self.proposal
        browser.open(proposal, view='tabbedview_view-overview')

    def get_latest_history_entry_text(self, browser):
        return browser.css('div.answers .answer h3').first.text

    def get_history_entries_text(self, browser):
        return browser.css('div.answers .answer h3').text

    def get_history_entries_comment(self, browser):
        return browser.css('div.answers .answer .text').text

    def get_latest_history_entry_comment(self, browser):
        return browser.css('div.answers .answer .text').first.text

    def assert_proposal_history_records(
            self,
            expected_records,
            proposal=None,
            browser=default_browser,
            with_submitted=False,
            expected_comments=None
            ):
        """Assert that the last history entries of a proposal are correct.

        The parameter expected_records can be a string to assert for only the
        last history record or a list of entries to assert that the last n
        entries are correct.

        If with_submitted is True also assert that the history entries are
        present for the submitted proposal.
        """
        if not proposal:
            proposal = self.proposal

        # assert proposal record(s)
        self.open_overview(browser, proposal)
        # First the record texts
        if isinstance(expected_records, basestring):
            self.assertEqual(expected_records, self.get_latest_history_entry_text(browser))
        else:
            nof_records = len(expected_records)
            self.assertSequenceEqual(expected_records, self.get_history_entries_text(browser)[:nof_records])

        # Now the record comments
        if expected_comments is not None:
            if isinstance(expected_comments, basestring):
                self.assertEqual(expected_comments, self.get_latest_history_entry_comment(browser))
            else:
                nof_records = len(expected_comments)
                self.assertSequenceEqual(expected_comments, self.get_history_entries_comment(browser)[:nof_records])

        if not with_submitted:
            return

        # assert submitted proposal record(s)
        proposal_model = proposal.load_model()
        submitted_proposal = proposal_model.resolve_submitted_proposal()
        self.open_overview(browser, submitted_proposal)
        # First the record texts
        if isinstance(expected_records, basestring):
            self.assertEqual(expected_records, self.get_latest_history_entry_text(browser))
        else:
            nof_records = len(expected_records)
            self.assertSequenceEqual(expected_records, self.get_history_entries_text(browser)[:nof_records])
        # Now the record comments
        if expected_comments is not None:
            if isinstance(expected_comments, basestring):
                self.assertEqual(expected_comments, self.get_latest_history_entry_comment(browser))
            else:
                nof_records = len(expected_comments)
                self.assertSequenceEqual(expected_comments, self.get_history_entries_comment(browser)[:nof_records])

    @browsing
    def test_creation_creates_history_entry(self, browser):
        self.login(self.regular_user, browser)
        self.assert_proposal_history_records(
            u'Created by Ziegler Robert (robert.ziegler)',
            self.draft_proposal,
            browser,
            )

    @browsing
    def test_submitting_proposal_creates_history_entries(self, browser):
        self.login(self.regular_user, browser)
        self.open_overview(browser, self.draft_proposal)
        # submit proposal
        browser.click_on('proposal-transition-submit')
        browser.fill({'Comment': u'Bitte \xfcbernehmen'}).submit()
        expected_history = u'Submitted by B\xe4rfuss K\xe4thi (kathi.barfuss)'
        expected_comment = u'Bitte \xfcbernehmen'
        with self.login(self.meeting_user, browser):
            self.assert_proposal_history_records(
                    expected_history, self.draft_proposal, browser,
                    with_submitted=True, expected_comments=expected_comment)

    @browsing
    def test_rejecting_proposals_creates_history_entries(self, browser):
        self.login(self.regular_user, browser)
        self.open_overview(browser, self.proposal)
        # reject submitted proposal
        submitted_proposal = self.proposal.load_model().resolve_submitted_proposal()
        with self.login(self.committee_responsible, browser):
            self.open_overview(browser, submitted_proposal)
            browser.find('Reject').click()
            browser.fill({'Comment': u'Bitte \xfcberarbeiten'}).submit()
        expected_history = u'Rejected by M\xfcller Fr\xe4nzi (franzi.muller)'
        expected_comment = u'Bitte \xfcberarbeiten'
        self.assert_proposal_history_records(
                    expected_history, self.proposal, browser,
                    expected_comments=expected_comment)

    @browsing
    def test_cancelling_and_reactivating_proposal_creates_history_entry(self, browser):
        self.login(self.regular_user, browser)
        self.open_overview(browser, self.draft_proposal)
        # cancel proposal
        browser.click_on("proposal-transition-cancel")
        browser.fill({'Comment': u'Unn\xf6tig'}).submit()

        self.assert_proposal_history_records(
            u'Proposal cancelled by B\xe4rfuss K\xe4thi (kathi.barfuss)',
            self.draft_proposal,
            browser,
            expected_comments=u'Unn\xf6tig'
            )
        # reactivate proposal
        browser.click_on("proposal-transition-reactivate")
        browser.fill({'Comment': u'N\xf6tig'}).submit()
        self.assert_proposal_history_records(
            u'Proposal reactivated by B\xe4rfuss K\xe4thi (kathi.barfuss)',
            self.draft_proposal,
            browser,
            expected_comments=u'N\xf6tig'
            )

    @browsing
    def test_commenting_proposal_creates_history_entry(self, browser):
        self.login(self.regular_user, browser)
        self.open_overview(browser, self.proposal)

        # comment proposal
        comment = u'Bevor einreichen noch erg\xe4nzen'
        browser.click_on("Comment")
        browser.fill({'Comment': comment}).submit()
        with self.login(self.meeting_user, browser):
            self.assert_proposal_history_records(
                u'Proposal commented by B\xe4rfuss K\xe4thi (kathi.barfuss)',
                self.proposal,
                browser,
                expected_comments=comment,
                with_submitted=True
                )

    @browsing
    def test_commenting_submitted_proposal_creates_history_entry(self, browser):
        self.login(self.committee_responsible, browser)
        submitted_proposal = self.proposal.load_model().resolve_submitted_proposal()
        self.open_overview(browser, submitted_proposal)
        # comment proposal
        comment = u'Im n\xe4chsten meeting besprechen?'
        browser.click_on("Comment")
        browser.fill({'Comment': comment}).submit()
        self.assert_proposal_history_records(
            u'Proposal commented by M\xfcller Fr\xe4nzi (franzi.muller)',
            self.proposal,
            browser,
            expected_comments=comment,
            with_submitted=True
            )

    @browsing
    def test_commenting_decided_proposal_creates_history_entry_in_closed_dossier(self, browser):
        self.login(self.committee_responsible, browser)
        submitted_proposal = self.decided_proposal
        proposal = submitted_proposal.load_model().resolve_proposal()
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        self.open_overview(browser, submitted_proposal)
        # comment proposal
        comment = u'Can comment a decided proposal.'
        browser.click_on("Comment")
        browser.fill({'Comment': comment}).submit()
        self.assert_proposal_history_records(
            u'Proposal commented by M\xfcller Fr\xe4nzi (franzi.muller)',
            proposal,
            browser,
            expected_comments=comment,
            with_submitted=True
            )

    @browsing
    def test_submitting_additional_document_creates_history_entry(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.proposal)
        # submit additional document
        browser.find('Submit additional documents').click()
        browser.fill({'Attachments': self.subdocument})
        browser.find('Submit Attachments').click()
        with self.login(self.meeting_user, browser):
            self.assert_proposal_history_records(
                u'Document \xdcbersicht der Vertr\xe4ge von 2016 submitted in version 0 '
                u'by B\xe4rfuss K\xe4thi (kathi.barfuss)',
                self.proposal,
                browser,
                with_submitted=True,
                )

    @browsing
    def test_updating_existing_document_creates_history_entry(self, browser):
        self.login(self.regular_user, browser)
        self.document.file = NamedBlobFile('New', filename=u'test.txt')
        repository = api.portal.get_tool('portal_repository')
        repository.save(self.document)
        browser.open(self.proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Attachments': self.document})
        browser.find('Submit Attachments').click()
        with self.login(self.meeting_user, browser):
            self.assert_proposal_history_records(
                u'Submitted document Vertr\xe4gsentwurf updated to version 1 by B\xe4rfuss K\xe4thi (kathi.barfuss)',
                self.proposal,
                browser,
                with_submitted=True,
                )

    @browsing
    def test_unlock_submitted_document_creates_history_entry(self, browser):
        self.login(self.committee_responsible, browser)

        submitted_document = SubmittedDocument.query.get_by_source(
            self.proposal, self.document).resolve_submitted()

        browser.open(submitted_document, view="unlock_submitted_document_form")
        browser.find_button_by_label('Unlock').click()

        with self.login(self.meeting_user, browser):
            self.assert_proposal_history_records(
                u'Submitted document Vertr\xe4gsentwurf permanently unlocked '
                u'by M\xfcller Fr\xe4nzi (franzi.muller)',
                self.proposal,
                browser,
                with_submitted=True,
                )

    @browsing
    def test_scheduling_creates_history_entry(self, browser):
        self.login(self.meeting_user, browser)
        with self.login(self.committee_responsible, browser):
            self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.assert_proposal_history_records(
            u'Scheduled for meeting 9. Sitzung der Rechnungspr\xfcfungskommission '
            u'by M\xfcller Fr\xe4nzi (franzi.muller)',
            self.proposal,
            browser,
            with_submitted=True,
            )

    @browsing
    def test_removing_from_schedule_creates_history_entry(self, browser):
        self.login(self.meeting_user, browser)
        unscheduling_url = self.meeting.model.get_url(view='agenda_items/2/delete')
        with self.login(self.committee_responsible, browser):
            self.schedule_proposal(self.meeting, self.submitted_proposal)
            browser.open(unscheduling_url)
        self.assert_proposal_history_records(
            u'Removed from schedule of meeting 9. Sitzung der Rechnungspr\xfcfungskommission '
            u'by M\xfcller Fr\xe4nzi (franzi.muller)',
            self.proposal,
            browser,
            with_submitted=True,
            )

    @browsing
    def test_reopening_creates_history_entry(self, browser):
        self.login(self.meeting_user, browser)
        deciding_url = self.meeting.model.get_url(view='agenda_items/2/decide')
        generate_excerpt_url = self.meeting.model.get_url(view='agenda_items/2/generate_excerpt?excerpt_title=bla')
        return_excerpt_url = self.meeting.model.get_url(view='agenda_items/2/return_excerpt?document={}')
        reopening_url = self.meeting.model.get_url(view='agenda_items/2/reopen')
        with self.login(self.committee_responsible, browser):
            self.schedule_proposal(self.meeting, self.submitted_proposal)
            browser.open(deciding_url, data={'_authenticator': createToken()})
            browser.open(generate_excerpt_url, data={'_authenticator': createToken()})
            agenda_item = self.meeting.model.agenda_items[0]
            excerpt_document = agenda_item.get_excerpt_documents()[0]
            browser.open(return_excerpt_url.format(IUUID(excerpt_document)), data={'_authenticator': createToken()})

            browser.open(reopening_url, data={'_authenticator': createToken()})

        self.assert_proposal_history_records(
            u'Proposal reopened by M\xfcller Fr\xe4nzi (franzi.muller)',
            self.proposal,
            browser,
            with_submitted=True,
            )

    @browsing
    def test_deciding_creates_history_entry(self, browser):
        self.login(self.meeting_user, browser)
        deciding_url = self.meeting.model.get_url(view='agenda_items/2/decide')
        generate_excerpt_url = self.meeting.model.get_url(view='agenda_items/2/generate_excerpt?excerpt_title=bla')
        return_excerpt_url = self.meeting.model.get_url(view='agenda_items/2/return_excerpt?document={}')
        with self.login(self.committee_responsible, browser):
            self.schedule_proposal(self.meeting, self.submitted_proposal)
            browser.open(deciding_url, data={'_authenticator': createToken()})
            browser.open(generate_excerpt_url, data={'_authenticator': createToken()})
            agenda_item = self.meeting.model.agenda_items[0]
            excerpt_document = agenda_item.get_excerpt_documents()[0]
            browser.open(return_excerpt_url.format(IUUID(excerpt_document)), data={'_authenticator': createToken()})

        self.assert_proposal_history_records(
            u'Proposal decided by M\xfcller Fr\xe4nzi (franzi.muller)',
            self.proposal,
            browser,
            with_submitted=True,
            )

    @browsing
    def test_revising_creates_history_entry(self, browser):
        self.login(self.meeting_user, browser)
        deciding_url = self.meeting.model.get_url(view='agenda_items/2/decide')
        generate_excerpt_url = self.meeting.model.get_url(view='agenda_items/2/generate_excerpt?excerpt_title=bla')
        return_excerpt_url = self.meeting.model.get_url(view='agenda_items/2/return_excerpt?document={}')
        reopening_url = self.meeting.model.get_url(view='agenda_items/2/reopen')
        revising_url = self.meeting.model.get_url(view='agenda_items/2/revise')
        with self.login(self.committee_responsible, browser):
            self.schedule_proposal(self.meeting, self.submitted_proposal)
            browser.open(deciding_url, data={'_authenticator': createToken()})
            browser.open(generate_excerpt_url, data={'_authenticator': createToken()})
            agenda_item = self.meeting.model.agenda_items[0]
            excerpt_document = agenda_item.get_excerpt_documents()[0]
            browser.open(return_excerpt_url.format(IUUID(excerpt_document)), data={'_authenticator': createToken()})
            browser.open(reopening_url, data={'_authenticator': createToken()})
            browser.open(revising_url, data={'_authenticator': createToken()})

        self.assert_proposal_history_records(
            u'Proposal revised by M\xfcller Fr\xe4nzi (franzi.muller)',
            self.proposal,
            browser,
            with_submitted=True,
            )

    @browsing
    def test_comment_on_unsubmitted_proposal_does_not_try_to_sync(self, browser):
        self.login(self.meeting_user, browser)

        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title=u'Vertr\xe4ge',
                                  committee=self.committee.load_model(),
                                  issuer=self.dossier_responsible.getId())
                          .relate_to(self.document))

        # Add comment
        browser.open(proposal, view='addcomment')
        browser.fill({'Comment': u'Vorgezogener Kommentar'})
        browser.click_on('Confirm')

        browser.open(proposal, view='tabbedview_view-overview')
        self.assertEqual(
            'Vorgezogener Kommentar', browser.css('.answer .text')[0].text)
