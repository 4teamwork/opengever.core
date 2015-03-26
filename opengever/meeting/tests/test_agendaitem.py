from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.meetings.agendaitem import DeleteAgendaItem
from opengever.meeting.browser.meetings.agendaitem import ScheduleSubmittedProposal
from opengever.meeting.browser.meetings.agendaitem import ScheduleText
from opengever.meeting.browser.meetings.agendaitem import UpdateAgendaItemOrder
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.model import Meeting
from opengever.meeting.model import Proposal
from opengever.testing import FunctionalTestCase
from zExceptions import Unauthorized
import transaction


class TestAgendaItem(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestAgendaItem, self).setUp()
        self.repo = create(Builder('repository_root'))
        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model(),
                                      start=datetime(2013, 1, 1),
                                      location='There',))

    def setup_proposal(self):
        root = create(Builder('repository_root'))
        folder = create(Builder('repository').within(root))
        dossier = create(Builder('dossier').within(folder))
        proposal = create(Builder('proposal')
                          .within(dossier)
                          .having(committee=self.committee.load_model()))
        proposal.execute_transition('pending-submitted')

        return proposal

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
    def test_text_and_paragraph_agenda_item_disabled_for_held_meetings(self, browser):
        self.meeting.execute_transition('pending-held')
        transaction.commit()

        url = ScheduleText.url_for(self.committee, self.meeting)
        with self.assertRaises(Unauthorized):
            browser.login().open(url, data=dict(title='foo'))

    @browsing
    def test_proposal_agenda_item_can_be_added_to_meeting(self, browser):
        proposal = self.setup_proposal()
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
    def test_proposal_agenda_item_disabled_for_held_meetings(self, browser):
        self.meeting.execute_transition('pending-held')
        proposal = self.setup_proposal()
        proposal_model = proposal.load_model()
        transaction.commit()

        url = ScheduleSubmittedProposal.url_for(self.committee, self.meeting)
        with self.assertRaises(Unauthorized):
            browser.login().open(
                url, data=dict(proposal_id=proposal_model.proposal_id))

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

    @browsing
    def test_agenda_item_deletion_disabled_for_held_meetings(self, browser):
        agenda_item = create(Builder('agenda_item').having(
            meeting=self.meeting))
        self.meeting.execute_transition('pending-held')
        transaction.commit()

        url = DeleteAgendaItem.url_for(
            self.committee, self.meeting, agenda_item)
        with self.assertRaises(Unauthorized):
            browser.login().open(url)

    def test_update_agenda_item_order(self):
        item1 = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting, sort_order=1))
        item2 = create(Builder('agenda_item').having(
            title=u'bar', meeting=self.meeting, sort_order=2))

        self.assertEqual(1, item1.sort_order)
        self.assertEqual(2, item2.sort_order)

        view = UpdateAgendaItemOrder(
            self.committee, self.request, self.meeting)
        view.update_sortorder({"sortOrder": [2, 1]})

        self.assertEqual(2, item1.sort_order)
        self.assertEqual(1, item2.sort_order)
