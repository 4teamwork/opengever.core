from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.browser.meetings.preprotocol import EditPreProtocol
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.model import Proposal
from opengever.testing import FunctionalTestCase


class TestPreProtocol(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestPreProtocol, self).setUp()
        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))
        self.committee_model = self.committee.load_model()
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee_model,
                                      start=datetime(2013, 1, 1),
                                      location='There',))
        self.proposal_model = create(Builder('proposal_model'))
        self.agenda_item = create(
            Builder('agenda_item')
            .having(meeting=self.meeting,
                    proposal=self.proposal_model))

    @browsing
    def test_pre_protocol_can_be_edited(self, browser):
        browser.login()
        browser.open(EditPreProtocol.url_for(self.committee, self.meeting))

        browser.fill({'Considerations': 'It is important',
                      'Proposed action': 'Accept it',
                      'Discussion': 'We should accept it',
                      'Decision': 'Accepted'}).submit()

        self.assertEquals(['Changes saved'], info_messages())

        proposal = Proposal.query.get(self.proposal_model.proposal_id)
        self.assertEqual('It is important', proposal.considerations)
        self.assertEqual('Accept it', proposal.proposed_action)

        agenda_item = AgendaItem.get(self.agenda_item.agenda_item_id)
        self.assertEqual('We should accept it', agenda_item.discussion)
        self.assertEqual('Accepted', agenda_item.decision)

        self.assertEqual(MeetingList.url_for(self.committee, self.meeting),
                         browser.url)

    @browsing
    def test_pre_protocol_participants_can_be_edited(self, browser):
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)
        peter = create(Builder('member'))
        hans = create(Builder('member').having(
            firstname=u'Hans', lastname=u'M\xfcller'))
        create(Builder('membership').having(
            member=peter,
            committee=self.committee_model,
            date_from=yesterday, date_to=tomorrow))
        create(Builder('membership').having(
            member=hans,
            committee=self.committee_model,
            date_from=yesterday, date_to=tomorrow))

        browser.login()
        browser.open(EditPreProtocol.url_for(self.committee, self.meeting))

        browser.fill({'Presidency': str(peter.member_id),
                      'Secretary': str(hans.member_id),
                      'Participants': str(peter.member_id),
                      'Other Participants': 'Klara'}).submit()

        self.assertEquals(['Changes saved'], info_messages())

        # refresh intances
        meeting = Meeting.query.get(self.meeting.meeting_id)
        peter = Member.get(peter.member_id)
        hans = Member.get(hans.member_id)

        self.assertSequenceEqual([peter], meeting.participants)
        self.assertEqual(peter, meeting.presidency)
        self.assertEqual(hans, meeting.secretary)
        self.assertEqual(u'Klara', meeting.other_participants)
