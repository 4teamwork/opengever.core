from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from opengever.meeting.protocol import ProtocolData
from opengever.testing import FunctionalTestCase


class TestProtocolJsonData(FunctionalTestCase):

    maxDiff = None

    def setUp(self):
        super(TestProtocolJsonData, self).setUp()
        self.proposal = create(
            Builder('proposal_model')
            .having(title=u'Proposal',
                    initial_position=u'Initial',
                    legal_basis=u'Legal!',
                    proposed_action=u'Yep',
                    considerations=u'We should think about it'))
        self.committee = create(Builder('committee_model'))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            start=datetime(2010, 1, 1)))

        self.agenda_item_proposal = create(
            Builder('agenda_item').having(
                proposal=self.proposal,
                meeting=self.meeting,
                discussion=u'Hmm',
                decision=u'Do it'))
        self.agend_item_text = create(
            Builder('agenda_item').having(
                title=u'Free Text',
                meeting=self.meeting,
                discussion=u'Blah',
                decision=u'Done',))

    def test_protocol_json(self):
        data = ProtocolData(self.meeting).data
        self.assertEqual(
            {'agenda_items': [
                {'description': u'Proposal',
                 'markdown:considerations': u'We should think about it',
                 'markdown:decision': u'Do it',
                 'markdown:discussion': u'Hmm',
                 'markdown:initial_position': u'Initial',
                 'markdown:legal_basis': u'Legal!',
                 'markdown:proposed_action': u'Yep',
                 'markdown:copy_for_attention': None,
                 'markdown:disclose_to': None,
                 'markdown:publish_in': None,
                 'number': None,
                 'title': u'Proposal',
                 'is_paragraph': False,},
                {'description': u'Free Text',
                 'markdown:considerations': None,
                 'markdown:decision': u'Done',
                 'markdown:discussion': u'Blah',
                 'markdown:initial_position': None,
                 'markdown:legal_basis': None,
                 'markdown:proposed_action': None,
                 'markdown:copy_for_attention': None,
                 'markdown:disclose_to': None,
                 'markdown:publish_in': None,
                 'number': None,
                 'title': u'Free Text',
                 'is_paragraph': False,}],
             'mandant': {'name': u'Client1'},
             'meeting': {'date': u'Jan 01, 2010',
                         'end_time': '',
                         'start_time': u'12:00 AM'},
             'participants': {'members': [], 'other': []},
             'protocol': {'type': u'Protocol'}},
            data
        )
