from ftw.zipexport.generation import ZipGenerator
from ftw.zipexport.utils import normalize_path
from opengever.meeting.command import AgendaItemListOperations
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import ProtocolOperations
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from StringIO import StringIO
from ZPublisher.Iterators import filestream_iterator
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

            # Return zip
            zip_file = generator.generate()
            filename = '{}.zip'.format(self.model.title.encode('utf-8'))
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
                namedfile = protocol.file
                return (namedfile.filename, namedfile.open())

        # Create new protocol
        operations = ProtocolOperations()
        command = CreateGeneratedDocumentCommand(
            self.context,
            self.model,
            operations,
            lock_document_after_creation=False)

        filename = operations.get_filename(self.model)
        return (filename, StringIO(command.generate_file_data()))

    def add_agenda_items_attachments(self, generator):

        for agenda_item in self.model.agenda_items:
            if not agenda_item.has_submitted_documents():
                continue

            for document in agenda_item.proposal.resolve_submitted_documents():
                namedfile = document.file                
                path = u'{} {}/{}'.format(
                    agenda_item.number,
                    agenda_item.proposal.title,
                    namedfile.filename
                )
                generator.add_file(path, namedfile.open())
