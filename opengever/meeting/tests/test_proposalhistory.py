from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.testing import FunctionalTestCase
from plone import api
from plone.protect import createToken
import transaction


class TestProposalHistory(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestProposalHistory, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'
        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repo_folder))
        self.excerpt_template = create(Builder('sablontemplate')
                                       .with_asset_file('excerpt_template.docx'))
        container = create(Builder('committee_container')
                           .having(excerpt_template=self.excerpt_template))
        self.committee = create(Builder('committee').within(container))
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model())
                              .link_with(self.meeting_dossier))

        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.document = create(Builder('document')
                               .within(self.dossier)
                               .titled('A Document'))
        self.proposal = create(Builder('proposal')
                               .within(self.dossier)
                               .having(title='Mach doch',
                                       committee=self.committee.load_model())
                               .relate_to(self.document))

    def open_overview(self, browser):
        browser.open(self.proposal, view='tabbedview_view-overview')

    def get_latest_history_entry_text(self, browser):
        return browser.css('div.answers .answer h3').first.text

    def get_history_entries_text(self, browser):
        return browser.css('div.answers .answer h3').text

    def submit_proposal(self):
        self.proposal.execute_transition('pending-submitted')
        transaction.commit()  # also make change visible in browser

    @browsing
    def test_creation_creates_history_entry(self, browser):
        browser.login()

        self.open_overview(browser)
        self.assertEqual(
            u'Created by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_submitting_proposal_creates_history_entries(self, browser):
        browser.login()
        self.open_overview(browser)

        # submit proposal
        browser.css('#pending-submitted').first.click()

        self.open_overview(browser)
        self.assertSequenceEqual(
            [u'Document A Document submitted in version 0 by Test User (test_user_1_)',
             u'Submitted by Test User (test_user_1_)'],
            self.get_history_entries_text(browser)[:2])

    @browsing
    def test_rejecting_proposals_creates_history_entries(self, browser):
        browser.login()
        self.open_overview(browser)

        # submit proposal
        browser.css('#pending-submitted').first.click()
        proposal = browser.context

        # reject submitted proposal
        submitted_proposal = proposal.load_model().resolve_submitted_proposal()
        browser.open(submitted_proposal, view='tabbedview_view-overview')
        browser.find('Reject').click()
        browser.fill({'Comment': u'Bitte \xfcberarbeiten'}).submit()

        self.open_overview(browser)
        self.assertSequenceEqual(
            u'Rejected by Test User (test_user_1_)',
            self.get_history_entries_text(browser)[0])

    @browsing
    def test_cancelling_and_reactivating_proposal_creates_history_entry(self, browser):
        browser.login()
        self.open_overview(browser)

        # cancel proposal
        browser.css('#pending-cancelled').first.click()
        self.open_overview(browser)
        self.assertEqual(
            u'Proposal cancelled by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

        # reactivate proposal
        browser.css('#cancelled-pending').first.click()
        self.open_overview(browser)
        self.assertEqual(
            u'Proposal reactivated by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_submitting_additional_document_creates_history_entry(self, browser):
        self.submit_proposal()
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled('Another document'))

        browser.login().visit(self.proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Attachments': document})
        browser.find('Submit Attachments').click()

        self.open_overview(browser)
        self.assertEqual(
            u'Document Another document submitted in version 0 by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_updating_existing_document_creates_history_entry(self, browser):
        self.submit_proposal()
        repository = api.portal.get_tool('portal_repository')
        repository.save(self.document)
        transaction.commit()

        browser.login().visit(self.proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Attachments': self.document})
        browser.find('Submit Attachments').click()

        self.open_overview(browser)
        self.assertEqual(
            u'Submitted document A Document updated to version 1 by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_scheduling_creates_history_entry(self, browser):
        self.submit_proposal()
        browser.login().open(
            self.meeting.get_url(view='unscheduled_proposals/1/schedule'))

        self.open_overview(browser)
        self.assertEqual(
            u'Scheduled for meeting C\xf6mmunity meeting by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_removing_from_schedule_creates_history_entry(self, browser):
        self.submit_proposal()
        browser.login().open(
            self.meeting.get_url(view='unscheduled_proposals/1/schedule'))

        browser.login().open(self.meeting.get_url(view='agenda_items/1/delete'))

        self.open_overview(browser)
        self.assertEqual(
            u'Removed from schedule of meeting C\xf6mmunity meeting by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_reopening_creates_history_entry(self, browser):
        self.submit_proposal()
        transaction.commit()
        browser.login().open(
            self.meeting.get_url(view='unscheduled_proposals/1/schedule'))
        browser.open(self.meeting.get_url(view='agenda_items/1/decide'),
                     data={'_authenticator': createToken()})
        browser.open(self.meeting.get_url(view='agenda_items/1/reopen'),
                     data={'_authenticator': createToken()})

        self.open_overview(browser)
        self.assertEqual(
            u'Proposal reopened by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_revising_creates_history_entry(self, browser):
        self.submit_proposal()
        transaction.commit()
        browser.login().open(
            self.meeting.get_url(view='unscheduled_proposals/1/schedule'))
        browser.open(self.meeting.get_url(view='agenda_items/1/decide'),
                     data={'_authenticator': createToken()})
        browser.open(self.meeting.get_url(view='agenda_items/1/reopen'),
                     data={'_authenticator': createToken()})
        browser.open(self.meeting.get_url(view='agenda_items/1/revise'),
                     data={'_authenticator': createToken()})

        self.open_overview(browser)
        self.assertEqual(
            u'Proposal revised by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))
