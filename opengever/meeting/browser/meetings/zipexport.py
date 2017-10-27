from ftw.zipexport.generation import ZipGenerator
from ftw.zipexport.utils import normalize_path
from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting.command import AgendaItemListOperations
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import MergeDocxProtocolCommand
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.exceptions import AgendaItemListMissingTemplate
from opengever.meeting.interfaces import IMeetingWrapper
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from StringIO import StringIO
from ZPublisher.Iterators import filestream_iterator
import os
import pytz


class MeetingZipExport(BrowserView):
    """Iterate over meeting contents and return results in a .zip archive."""

    def __init__(self, context, request):
        super(MeetingZipExport, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        # Download zip file
        return self.generate_zip()

    def visible_in_actions_menu(self):
        """Returns ``True`` when the zip export action should be displayed
        in the actions menu.

        The action should only appear when we are on a meeting view and the
        word-meeting feature is enabled.
        """
        return IMeetingWrapper.providedBy(self.context) and \
            is_word_meeting_implementation_enabled()

    def generate_zip(self):
        response = self.request.response

        with ZipGenerator() as generator:
            # Protocol
            generator.add_file(*self.get_protocol())

            # Agenda items
            self.add_agenda_items_attachments(generator)
            if is_word_meeting_implementation_enabled():
                self.add_agenda_item_proposal_documents(generator)

            # Agenda items list
            try:
                generator.add_file(*self.get_agendaitem_list())
            except AgendaItemListMissingTemplate:
                pass

            # Return zip
            zip_file = generator.generate()
            filename = '{}.zip'.format(normalize_path(self.model.title))
            response.setHeader(
                "Content-Disposition",
                'inline; filename="{0}"'.format(
                    safe_unicode(filename).encode('utf-8')))
            response.setHeader("Content-type", "application/zip")
            response.setHeader(
                "Content-Length",
                os.stat(zip_file.name).st_size)

            return filestream_iterator(zip_file.name, 'rb')

    def get_protocol(self):
        if self.model.has_protocol_document():
            protocol = self.model.protocol_document.resolve_document()
            protocol_modified = protocol.modified().asdatetime().astimezone(
                pytz.utc)

            if self.model.modified < protocol_modified:
                # Return current protocol
                return (u'{}.docx'.format(safe_unicode(protocol.Title())),
                        protocol.file.open())

        # Create new protocol
        operations = ProtocolOperations()
        if is_word_meeting_implementation_enabled():
            command_class = MergeDocxProtocolCommand
        else:
            command_class = CreateGeneratedDocumentCommand
        command = command_class(
            self.context,
            self.model,
            operations,
            lock_document_after_creation=False)

        filename = u'{}.docx'.format(operations.get_title(self.model))
        return (filename, StringIO(command.generate_file_data()))

    def add_agenda_item_proposal_documents(self, generator):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.has_proposal:
                continue

            document = agenda_item.resolve_document()
            if not document:
                continue

            extension = os.path.splitext(document.file.filename)[1]
            path = u'{} {}/{}'.format(
                agenda_item.number,
                agenda_item.submitted_proposal.title,
                safe_unicode(document.Title()) + extension
            )
            generator.add_file(path, document.file.open())

    def add_agenda_items_attachments(self, generator):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.has_submitted_documents():
                continue

            for document in agenda_item.proposal.resolve_submitted_documents():
                extension = os.path.splitext(document.file.filename)[1]
                path = u'{} {}/{}'.format(
                    agenda_item.number,
                    agenda_item.submitted_proposal.title,
                    safe_unicode(document.Title()) + extension
                )
                generator.add_file(path, document.file.open())

    def get_agendaitem_list(self):
        if self.model.has_agendaitem_list_document():
            agendaitem_list = self.model.agendaitem_list_document.resolve_document()
            agendaitem_list_modified = agendaitem_list.modified().asdatetime().astimezone(
                pytz.utc)

            if self.model.modified < agendaitem_list_modified:
                # Return current protocol
                return (u'{}.docx'.format(safe_unicode(agendaitem_list.Title())),
                        agendaitem_list.file.open())

        # Create new protocol
        operations = AgendaItemListOperations()
        command = CreateGeneratedDocumentCommand(
            self.context,
            self.model,
            operations,
            )

        filename = u'{}.docx'.format(operations.get_title(self.model))
        return (filename, StringIO(command.generate_file_data()))
