from opengever.dossier.interfaces import IDocProperties
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter


def get_doc_properties(document, prefix='ogg.meeting.'):
    docprops = getMultiAdapter((document, document.REQUEST), IDocProperties)
    return {key: value for key, value in docprops.get_properties().items()
            if key.startswith(prefix)}


class TestMeetingDocxProperties(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    def test_non_meeting_document_should_not_have_meeting_properties(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            {},
            get_doc_properties(self.document),
            'A regular document should not contain meeting doc properties.')

    def test_pending_proposal_document(self):
        self.login(self.dossier_responsible)
        self.assertEquals('pending', self.draft_word_proposal.get_state().title)
        self.assertEquals(
            {'ogg.meeting.decision_number': '',
             'ogg.meeting.agenda_item_number': '',
             'ogg.meeting.proposal_title': '\xc3\x84nderungen am Personalreglement'},
            get_doc_properties(self.word_proposal.get_proposal_document()))

    def test_submitted_proposal_document(self):
        with self.login(self.dossier_responsible):
            self.assertEquals('submitted', self.word_proposal.get_state().title)
            self.assertEquals(
                {'ogg.meeting.decision_number': '',
                 'ogg.meeting.agenda_item_number': '',
                 'ogg.meeting.proposal_title': '\xc3\x84nderungen am Personalreglement'},
                get_doc_properties(self.word_proposal.get_proposal_document()))

        with self.login(self.committee_responsible):
            self.assertEquals('submitted', self.submitted_word_proposal.get_state().title)
            self.assertEquals(
                {'ogg.meeting.decision_number': '',
                 'ogg.meeting.agenda_item_number': '',
                 'ogg.meeting.proposal_title': '\xc3\x84nderungen am Personalreglement'},
                get_doc_properties(self.submitted_word_proposal.get_proposal_document()))

    def test_scheduled_proposal_document(self):
        with self.login(self.committee_responsible):
            self.schedule_proposal(self.meeting, self.submitted_word_proposal)

        with self.login(self.dossier_responsible):
            self.assertEquals('scheduled', self.word_proposal.get_state().title)
            self.assertEquals(
                {'ogg.meeting.decision_number': '',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.proposal_title': '\xc3\x84nderungen am Personalreglement'},
                get_doc_properties(self.word_proposal.get_proposal_document()))

        with self.login(self.committee_responsible):
            self.assertEquals('scheduled', self.submitted_word_proposal.get_state().title)
            self.assertEquals(
                {'ogg.meeting.decision_number': '',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.proposal_title': '\xc3\x84nderungen am Personalreglement'},
                get_doc_properties(self.submitted_word_proposal.get_proposal_document()))

    def test_decided_proposal_document(self):
        with self.login(self.committee_responsible):
            self.schedule_proposal(self.meeting, self.submitted_word_proposal).decide()

        with self.login(self.dossier_responsible):
            self.assertEquals('decided', self.word_proposal.get_state().title)
            self.assertEquals(
                {'ogg.meeting.decision_number': '2016 / 2',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.proposal_title': '\xc3\x84nderungen am Personalreglement'},
                get_doc_properties(self.word_proposal.get_proposal_document()))

        with self.login(self.committee_responsible):
            self.assertEquals('decided', self.submitted_word_proposal.get_state().title)
            self.assertEquals(
                {'ogg.meeting.decision_number': '2016 / 2',
                 'ogg.meeting.agenda_item_number': '1.',
                 'ogg.meeting.proposal_title': '\xc3\x84nderungen am Personalreglement'},
                get_doc_properties(self.submitted_word_proposal.get_proposal_document()))
