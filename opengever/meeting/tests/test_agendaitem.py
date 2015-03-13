from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.model import Meeting
from opengever.meeting.model import Proposal
from opengever.testing import FunctionalTestCase


class TestAgendaItem(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestAgendaItem, self).setUp()
        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model(),
                                      start=datetime(2013, 1, 1),
                                      location='There',))

    @browsing
    def test_free_text_agend_item_can_be_added(self, browser):
        browser.login()
        browser.open(MeetingList.url_for(self.committee, self.meeting))

        form = browser.css('#schedule_text').first
        form.fill({'title': 'My Agenda Item'})
        browser.css('#submit-schedule-text').first.click()

        meeting = Meeting.query.get(self.meeting.meeting_id)
        self.assertEqual(1, len(meeting.agenda_items))
        agenda_item = meeting.agenda_items[0]
        self.assertEqual('My Agenda Item', agenda_item.title)
        self.assertIsNone(agenda_item.proposal)
        self.assertFalse(agenda_item.is_paragraph)

    @browsing
    def test_paragraph_agenda_item_can_be_added(self, browser):
        browser.login()
        browser.open(MeetingList.url_for(self.committee, self.meeting))

        form = browser.css('#schedule_text').first
        form.fill({'title': 'My Paragraph'})
        browser.css('#submit-schedule-paragraph').first.click()

        meeting = Meeting.query.get(self.meeting.meeting_id)
        self.assertEqual(1, len(meeting.agenda_items))
        agenda_item = meeting.agenda_items[0]
        self.assertEqual('My Paragraph', agenda_item.title)
        self.assertIsNone(agenda_item.proposal)
        self.assertTrue(agenda_item.is_paragraph)

    @browsing
    def test_proposal_agenda_item_can_be_added_to_meeting(self, browser):
        root = create(Builder('repository_root'))
        folder = create(Builder('repository').within(root))
        dossier = create(Builder('dossier').within(folder))
        proposal = create(Builder('proposal')
                          .within(dossier)
                          .having(committee=self.committee.load_model()))
        proposal.execute_transition('pending-submitted')

        proposal_model = proposal.load_model()

        browser.login()
        browser.open(MeetingList.url_for(self.committee, self.meeting))
        form = browser.css('#schedule_proposal').first
        form.fill({'proposal_id': str(proposal_model.proposal_id)}).submit()

        # refresh model instances
        meeting = Meeting.query.get(self.meeting.meeting_id)
        proposal_model = Proposal.query.get(proposal_model.proposal_id)

        self.assertEqual(1, len(meeting.agenda_items))
        agenda_item = meeting.agenda_items[0]
        self.assertIsNotNone(agenda_item.proposal)
        self.assertEqual(proposal_model, agenda_item.proposal)
        self.assertFalse(agenda_item.is_paragraph)

    @browsing
    def test_agenda_item_can_be_deleted(self, browser):
        create(Builder('agenda_item').having(meeting=self.meeting))
        self.assertEqual(1, len(self.meeting.agenda_items))

        browser.login()
        browser.open(MeetingList.url_for(self.committee, self.meeting))
        browser.css('.delete_agenda_item').first.click()

        # refresh model instances
        meeting = Meeting.query.get(self.meeting.meeting_id)
        self.assertEqual(0, len(meeting.agenda_items))
