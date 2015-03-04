from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestProposalHistory(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestProposalHistory, self).setUp()
        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model(),
                                      date=date(2013, 1, 1),
                                      location='There',))
        root = create(Builder('repository_root'))
        folder = create(Builder('repository').within(root))
        self.dossier = create(Builder('dossier').within(folder))
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
    def test_submitting_additional_document_creates_history_entry(self, browser):
        self.submit_proposal()
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled('Another document'))

        browser.login().visit(self.proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Documents': document})
        browser.find('Submit Documents').click()

        self.open_overview(browser)
        self.assertEqual(
            u'Document Another document submitted in version 0 by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_upading_existing_document_creates_history_entry(self, browser):
        self.submit_proposal()
        repository = api.portal.get_tool('portal_repository')
        repository.save(self.document)
        transaction.commit()

        browser.login().visit(self.proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Documents': self.document})
        browser.find('Submit Documents').click()

        self.open_overview(browser)
        self.assertEqual(
            u'Submitted document A Document updated to version 1 by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_scheduling_creates_history_entry(self, browser):
        self.submit_proposal()
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        form = browser.css('#schedule_proposal').first
        form.fill(
            {'proposal_id': str(self.proposal.load_model().proposal_id)}
        ).submit()

        self.open_overview(browser)
        self.assertEqual(
            u'Scheduled for meeting There, Jan 01, 2013 by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))

    @browsing
    def test_removing_from_schedule_creates_history_entry(self, browser):
        self.submit_proposal()
        # schedule proposal
        browser.login().open(MeetingList.url_for(self.committee, self.meeting))
        form = browser.css('#schedule_proposal').first
        form.fill(
            {'proposal_id': str(self.proposal.load_model().proposal_id)}
        ).submit()

        browser.css('.delete_agenda_item').first.click()

        self.open_overview(browser)
        self.assertEqual(
            u'Removed from schedule of meeting There, Jan 01, 2013 by Test User (test_user_1_)',
            self.get_latest_history_entry_text(browser))
