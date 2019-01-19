from opengever.dossier.interfaces import IDocProperties
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


def get_doc_properties(document, prefix='ogg.meeting.'):
    docprops = getMultiAdapter((document, document.REQUEST), IDocProperties)
    return {key: value for key, value in docprops.get_properties().items()
            if key.startswith(prefix)}


class TestMeetingDocxProperties(IntegrationTestCase):
    features = ('meeting',)

    def test_non_meeting_document_should_not_have_meeting_properties(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            {},
            get_doc_properties(self.document),
            'A regular document should not contain meeting doc properties.')

    def test_pending_proposal_document(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            {'ogg.meeting.decision_number': '',
             'ogg.meeting.agenda_item_number': '',
             'ogg.meeting.agenda_item_number_raw': '',
             'ogg.meeting.proposal_title': 'Antrag f\xc3\xbcr Kreiselbau',
             'ogg.meeting.proposal_description': '',
             'ogg.meeting.proposal_state': 'Pending'},
            get_doc_properties(self.draft_proposal.get_proposal_document()))

    def test_submitted_proposal_document(self):
        with self.login(self.dossier_responsible):
            self.assertEquals(
                {'ogg.meeting.decision_number': '',
                 'ogg.meeting.agenda_item_number': '',
                 'ogg.meeting.agenda_item_number_raw': '',
                 'ogg.meeting.proposal_title': 'Vertr\xc3\xa4ge',
                 'ogg.meeting.proposal_description': 'F\xc3\xbcr weitere Bearbeitung bewilligen',
                 'ogg.meeting.proposal_state': 'Submitted'},
                get_doc_properties(self.proposal.get_proposal_document()))

        with self.login(self.committee_responsible):
            self.assertEquals(
                {'ogg.meeting.decision_number': '',
                 'ogg.meeting.agenda_item_number': '',
                 'ogg.meeting.agenda_item_number_raw': '',
                 'ogg.meeting.proposal_title': 'Vertr\xc3\xa4ge',
                 'ogg.meeting.proposal_description': 'F\xc3\xbcr weitere Bearbeitung bewilligen',
                 'ogg.meeting.proposal_state': 'Submitted'},
                get_doc_properties(self.submitted_proposal.get_proposal_document()))

    def test_scheduled_proposal_document(self):
        with self.login(self.committee_responsible):
            self.schedule_proposal(self.meeting, self.submitted_proposal)

        with self.login(self.dossier_responsible):
            self.assertEquals(
                {'ogg.meeting.decision_number': '',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.agenda_item_number_raw': 1,
                 'ogg.meeting.proposal_title': 'Vertr\xc3\xa4ge',
                 'ogg.meeting.proposal_description': 'F\xc3\xbcr weitere Bearbeitung bewilligen',
                 'ogg.meeting.proposal_state': 'Scheduled'},
                get_doc_properties(self.proposal.get_proposal_document()))

        with self.login(self.committee_responsible):
            self.assertEquals(
                {'ogg.meeting.decision_number': '',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.agenda_item_number_raw': 1,
                 'ogg.meeting.proposal_title': 'Vertr\xc3\xa4ge',
                 'ogg.meeting.proposal_description': 'F\xc3\xbcr weitere Bearbeitung bewilligen',
                 'ogg.meeting.proposal_state': 'Scheduled'},
                get_doc_properties(self.submitted_proposal.get_proposal_document()))

    def test_decided_proposal_document(self):
        with self.login(self.committee_responsible):
            agendaitem = self.schedule_proposal(self.meeting, self.submitted_proposal)
            self.decide_agendaitem_generate_and_return_excerpt(agendaitem)

        with self.login(self.dossier_responsible):
            self.assertEquals(
                {'ogg.meeting.decision_number': '2016 / 2',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.agenda_item_number_raw': 1,
                 'ogg.meeting.proposal_title': 'Vertr\xc3\xa4ge',
                 'ogg.meeting.proposal_description': 'F\xc3\xbcr weitere Bearbeitung bewilligen',
                 'ogg.meeting.proposal_state': 'Decided'},
                get_doc_properties(self.proposal.get_proposal_document()))

        with self.login(self.committee_responsible):
            self.assertEquals(
                {'ogg.meeting.decision_number': '2016 / 2',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.agenda_item_number_raw': 1,
                 'ogg.meeting.proposal_title': 'Vertr\xc3\xa4ge',
                 'ogg.meeting.proposal_description': 'F\xc3\xbcr weitere Bearbeitung bewilligen',
                 'ogg.meeting.proposal_state': 'Decided'},
                get_doc_properties(self.submitted_proposal.get_proposal_document()))

    def test_excerpt_document(self):
        with self.login(self.committee_responsible):
            agenda_item = self.schedule_proposal(self.meeting,
                                                 self.submitted_proposal)
            agenda_item.decide()
            with self.observe_children(self.meeting_dossier) as children:
                agenda_item.generate_excerpt(title='Excerpt')

            meeting_dossier_excerpt, = children['added']

            self.assertEquals(
                {'ogg.meeting.decision_number': '2016 / 2',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.agenda_item_number_raw': 1,
                 'ogg.meeting.proposal_title': 'Vertr\xc3\xa4ge',
                 'ogg.meeting.proposal_description': 'F\xc3\xbcr weitere Bearbeitung bewilligen',
                 'ogg.meeting.proposal_state': 'Scheduled'},
                get_doc_properties(meeting_dossier_excerpt))

            with self.observe_children(self.dossier) as children:
                agenda_item.return_excerpt(meeting_dossier_excerpt)

            case_dossier_excerpt, = children['added']

        with self.login(self.dossier_responsible):
            self.assertEquals(
                {'ogg.meeting.decision_number': '2016 / 2',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.agenda_item_number_raw': 1,
                 'ogg.meeting.proposal_title': 'Vertr\xc3\xa4ge',
                 'ogg.meeting.proposal_description': 'F\xc3\xbcr weitere Bearbeitung bewilligen',
                 'ogg.meeting.proposal_state': 'Decided'},
                get_doc_properties(case_dossier_excerpt))
