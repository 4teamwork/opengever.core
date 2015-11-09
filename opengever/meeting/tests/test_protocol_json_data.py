from datetime import date
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
                    dossier_reference_number='FD 2.6.8/1',
                    considerations=u'We should think about it'))
        self.committee = create(Builder('committee_model'))
        self.member_peter = create(Builder('member'))
        self.member_franz = create(Builder('member')
                                   .having(firstname=u'Franz',
                                           lastname=u'M\xfcller'))
        self.membership_peter = create(Builder('membership').having(
            member=self.member_peter,
            committee=self.committee,
            date_from=date(2010, 1, 1),
            date_to=date(2012, 1, 1),
            role=u'F\xfcrst'))
        self.membership_franz = create(Builder('membership').having(
            member=self.member_franz,
            committee=self.committee,
            date_from=date(2010, 1, 1),
            date_to=date(2012, 1, 1),
            role=None))
        self.meeting = create(Builder('meeting').having(
            committee=self.committee,
            participants=[self.member_peter, self.member_franz],
            other_participants=u'Hans M\xfcller\nHeidi Muster',
            protocol_start_page_number=42))

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
            {'_sablon': {'properties': {'start_page_number': 42}},
             'agenda_items': [
                {'description': u'Proposal',
                 'dossier_reference_number': 'FD 2.6.8/1',
                 'markdown:considerations': u'We should think about it',
                 'markdown:decision': u'Do it',
                 'markdown:discussion': u'Hmm',
                 'markdown:initial_position': u'Initial',
                 'markdown:legal_basis': u'Legal!',
                 'markdown:proposed_action': u'Yep',
                 'markdown:copy_for_attention': None,
                 'markdown:disclose_to': None,
                 'markdown:publish_in': None,
                 'number': '1.',
                 'title': u'Proposal',
                 'is_paragraph': False,},
                {'description': u'Free Text',
                 'dossier_reference_number': None,
                 'markdown:considerations': None,
                 'markdown:decision': u'Done',
                 'markdown:discussion': u'Blah',
                 'markdown:initial_position': None,
                 'markdown:legal_basis': None,
                 'markdown:proposed_action': None,
                 'markdown:copy_for_attention': None,
                 'markdown:disclose_to': None,
                 'markdown:publish_in': None,
                 'number': '2.',
                 'title': u'Free Text',
                 'is_paragraph': False,}],
             'mandant': {'name': u'Client1'},
             'meeting': {'date': u'Dec 13, 2011',
                         'end_time': u'11:45 AM',
                         'start_time': u'09:30 AM'},
             'participants': {
                'members': [{'fullname': u'Peter Meier',
                             'role': u'F\xfcrst'},
                            {'fullname': u'Franz M\xfcller',
                             'role': None}],
                'other': [u'Hans M\xfcller', u'Heidi Muster']},
             'protocol': {'type': u'Protocol'}},
            data
        )
