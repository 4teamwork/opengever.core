from ftw.zipexport.generation import ZipGenerator
from ftw.zipexport.utils import normalize_path
from opengever.meeting.command import AgendaItemListOperations
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import ProtocolOperations
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from StringIO import StringIO
from ZPublisher.Iterators import filestream_iterator
import cgi
import os
import pytz


class MeetingZipExport(BrowserView):

    def __init__(self, context, request):
        super(MeetingZipExport, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        # Download zip file
        return self.generate_zip()

    def generate_zip(self):
        response = self.request.response

        with ZipGenerator() as generator:
            # Protocol
            generator.add_file(*self.get_protocol())

            # Agenda items
            self.add_agenda_items_attachments(generator)

            # Agenda items list
            self.add_agenda_item_list(generator)

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
        command = CreateGeneratedDocumentCommand(
            self.context,
            self.model,
            operations,
            lock_document_after_creation=False)

        filename = u'{}.docx'.format(operations.get_title(self.model))
        return (filename, StringIO(command.generate_file_data()))

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

    def add_agenda_item_list(self, generator):
        has_template = AgendaItemListOperations().get_sablon_template(
            self.model)

        if self.model.agenda_items and has_template:
            view = self.context.restrictedTraverse('@@agenda_item_list')
            generator.add_file(view.get_document_filename(),
                               StringIO(view.create_agenda_item_list()))
