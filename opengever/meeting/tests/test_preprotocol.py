from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.meetings import EditPreProtocol
from opengever.meeting.browser.meetings import MeetingList
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Proposal
from opengever.testing import FunctionalTestCase


class TestPreProtocol(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestPreProtocol, self).setUp()
        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))
        committee_model = self.committee.load_model()
        self.meeting = create(Builder('meeting')
                              .having(committee=committee_model,
                                      date=date(2013, 1, 1),
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
                      'Proposal': 'Accept it',
                      'Discussion': 'We should accept it',
                      'Decision': 'Accepted'}).submit()

        proposal = Proposal.query.get(self.proposal_model.proposal_id)
        self.assertEqual('It is important', proposal.considerations)
        self.assertEqual('Accept it', proposal.proposed_action)

        agenda_item = AgendaItem.get(self.agenda_item.agenda_item_id)
        self.assertEqual('We should accept it', agenda_item.discussion)
        self.assertEqual('Accepted', agenda_item.decision)

        self.assertEqual(MeetingList.url_for(self.committee, self.meeting),
                         browser.url)
