class MeetingTraverser(object):
    """Traverse the meeting and its documents.

    Knows the meetings strucutre and its documents. Provides hook methods to
    add functionality for a concrete traverser.

    Might be a candidate to be refactored into a visitor in the future.
    """
    def __init__(self, meeting):
        self.meeting = meeting

    def traverse(self):
        self.traverse_protocol()
        self.traverse_agenda_item_list()
        self.traverse_agenda_items()

        return self

    def traverse_protocol(self):
        protocol = self._get_protocol_document()
        if protocol:
            self.traverse_protocol_document(protocol)

    def traverse_agenda_item_list(self):
        agenda_item_list = self._get_agenda_item_list_document()
        if agenda_item_list:
            self.traverse_agenda_item_list_document(agenda_item_list)

    def traverse_agenda_items(self):
        for agenda_item in self.meeting.agenda_items:
            self.traverse_agenda_item(agenda_item)

    def traverse_agenda_item(self, agenda_item):
        agenda_item_doc = self._get_agenda_item_document(agenda_item)
        if agenda_item_doc:
            self.traverse_agenda_item_document(
                agenda_item_doc, agenda_item)

        for attachment in self._get_agenda_item_attachments(agenda_item):
            if attachment:
                self.traverse_agenda_item_attachment(
                    attachment, agenda_item)

        for excerpt in self._get_agenda_item_excerpts(agenda_item):
            if excerpt:
                self.traverse_agenda_item_excerpt(excerpt, agenda_item)

    def _get_protocol_document(self):
        if not self.meeting.has_protocol_document():
            return None

        return self.meeting.protocol_document.resolve_document()

    def _get_agenda_item_list_document(self):
        if not self.meeting.has_agendaitem_list_document():
            return None

        return self.meeting.agendaitem_list_document.resolve_document()

    def _get_agenda_item_document(self, agenda_item):
        return agenda_item.resolve_document()

    def _get_agenda_item_attachments(self, agenda_item):
        return agenda_item.resolve_submitted_documents()

    def _get_agenda_item_excerpts(self, agenda_item):
        return agenda_item.get_excerpt_documents()

    def traverse_protocol_document(self, document):
        pass

    def traverse_agenda_item_list_document(self, document):
        pass

    def traverse_agenda_item_document(self, document, agenda_item):
        pass

    def traverse_agenda_item_attachment(self, document, agenda_item):
        pass

    def traverse_agenda_item_excerpt(self, document, agenda_item):
        pass
