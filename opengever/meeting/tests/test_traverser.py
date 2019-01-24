from opengever.testing import IntegrationTestCase
from opengever.meeting.traverser import MeetingDocumentWithFileTraverser
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

    def traverse_agenda_item_attachment(self, document, agenda_item, attachment_number):
        self.agenda_item_attachments.append((attachment_number, document))

    def traverse_agenda_item_excerpt(self, document, agenda_item, excerpt_number):
        self.agenda_item_excerpts.append((excerpt_number, document))


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
            [(i + 1, doc) for i, doc in enumerate(submitted_proposal.get_documents())],
            traverser.agenda_item_attachments)
        self.assertEqual(
             [(i + 1, doc) for i, doc in enumerate(submitted_proposal.get_excerpts())],
             traverser.agenda_item_excerpts)


class MeetingDocumentWithFileTraverserTestImplementation(MeetingDocumentWithFileTraverser):

    def __init__(self, meeting):
        super(MeetingDocumentWithFileTraverserTestImplementation, self).__init__(meeting)
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

    def traverse_agenda_item_attachment(self, document, agenda_item, attachment_number):
        self.agenda_item_attachments.append(document)

    def traverse_agenda_item_excerpt(self, document, agenda_item, excerpt_number):
        self.agenda_item_excerpts.append(document)


class TestMeetingDocumentWithFileTraverser(IntegrationTestCase):

    features = ('meeting',)

    def test_meeting_traverser_traverses_all_documents_with_file(self):
        self.login(self.committee_responsible)

        # Add two additional attachments, one without a file
        self.proposal.submit_additional_document(self.empty_document)
        self.proposal.submit_additional_document(self.subdocument)

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

        traverser = MeetingDocumentWithFileTraverserTestImplementation(
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
             submitted_proposal.get_excerpts(),
             traverser.agenda_item_excerpts)

        documents_without_file = [doc for doc in submitted_proposal.get_documents()
                                  if not doc.has_file()]
        documents_with_file = [doc for doc in submitted_proposal.get_documents()
                               if doc.has_file()]
        for document in documents_without_file:
            self.assertNotIn(document, traverser.agenda_item_attachments)
        self.assertItemsEqual(
            documents_with_file,
            traverser.agenda_item_attachments)
