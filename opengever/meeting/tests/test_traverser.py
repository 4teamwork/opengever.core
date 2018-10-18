from opengever.testing import IntegrationTestCase
from opengever.meeting.traverser import MeetingTraverser


class MeetingTraverserTestImplementation(MeetingTraverser):

    def __init__(self, meeting):
        super(MeetingTraverserTestImplementation, self).__init__(meeting)
        self.protocol_document = None
        self.agenda_item_list_document = None
        self.agenda_item_documents = []
        self.agenda_item_attachments = []
        self.agenda_item_excerpts = []

    def traverse_protocol_document(self, document):
        self.protocol_document = document

    def traverse_agenda_item_list_document(self, document):
        self.agenda_item_list_document = document

    def traverse_agenda_item_document(self, document, agenda_item):
        self.agenda_item_documents.append(document)

    def traverse_agenda_item_attachment(self, document, agenda_item):
        self.agenda_item_attachments.append(document)

    def traverse_agenda_item_excerpt(self, document, agenda_item):
        self.agenda_item_excerpts.append(document)


class TestMeetingTraverser(IntegrationTestCase):

    features = ('meeting',)

    def test_meeting_traverser_traverses_all_documents(self):
        self.login(self.committee_responsible)

        proposal_agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        self.schedule_paragraph(
            self.meeting, "I'm a paragraph and thus should not be relevant")
        ad_hoc_agend_item = self.schedule_ad_hoc(
            self.meeting, "I'm an ad hoc agenda item")
        submitted_proposal = proposal_agenda_item.proposal.resolve_submitted_proposal()

        self.decide_agendaitem_generate_and_return_excerpt(proposal_agenda_item)
        self.generate_protocol_document(self.meeting)
        self.generate_agenda_item_list(self.meeting)

        traverser = MeetingTraverserTestImplementation(
            self.meeting.model).traverse()

        self.assertEqual(
            self.meeting.model.protocol_document.resolve_document(),
            traverser.protocol_document)
        self.assertEqual(
            self.meeting.model.agendaitem_list_document.resolve_document(),
            traverser.agenda_item_list_document)
        self.assertEqual(
            [proposal_agenda_item.resolve_document(),
             ad_hoc_agend_item.resolve_document()],
            traverser.agenda_item_documents)
        self.assertEqual(
            submitted_proposal.get_documents(),
            traverser.agenda_item_attachments)
        self.assertEqual(
             submitted_proposal.get_excerpts(),
             traverser.agenda_item_excerpts)
