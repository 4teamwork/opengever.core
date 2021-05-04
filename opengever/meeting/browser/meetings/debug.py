from ftw.zipexport.generation import ZipGenerator
from ftw.zipexport.utils import normalize_path
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.protocol import ProtocolData
from opengever.meeting.sablon import Sablon
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from StringIO import StringIO
from ZPublisher.Iterators import filestream_iterator
import os


class DebugDocxCompose(BrowserView):
    """Return a zip containing all raw files for docxcompose for debugging
    purposes.
    """
    operations = ProtocolOperations()

    def __init__(self, context, request):
        super(DebugDocxCompose, self).__init__(context, request)
        self.meeting = context.model

    def __call__(self):
        with ZipGenerator() as generator:
            self.add_header_sablon(generator)
            for index, agenda_item in enumerate(self.meeting.agenda_items, 1):
                self.add_agenda_item(index, agenda_item, generator)
            self.add_suffix_sablon(index, generator)

            # Return zip
            response = self.request.response
            zip_file = generator.generate()
            filename = '{}.zip'.format(normalize_path(self.meeting.title))
            response.setHeader(
                "Content-Disposition",
                'inline; filename="{0}"'.format(
                    safe_unicode(filename).encode('utf-8')))
            response.setHeader("Content-type", "application/zip")
            response.setHeader(
                "Content-Length",
                os.stat(zip_file.name).st_size)

            return filestream_iterator(zip_file.name, 'rb')

    def add_header_sablon(self, generator):
        template = self.meeting.get_protocol_header_template()
        sablon = Sablon(template).process(
            self.operations.get_meeting_data(self.meeting).as_json())
        generator.add_file(
            u'000_protocol_header_template.docx', StringIO(sablon.file_data))

    def add_suffix_sablon(self, index, generator):
        template = self.meeting.get_protocol_suffix_template()
        if template is None:
            return

        sablon = Sablon(template).process(
            self.operations.get_meeting_data(self.meeting).as_json())
        generator.add_file(
            u'{:03d}_protocol_suffix_template.docx'.format(index + 1),
            StringIO(sablon.file_data))

    def add_agenda_item(self, index, agenda_item, generator):
        if agenda_item.is_paragraph:
            self.add_sablon_for_paragraph(
                index, agenda_item, generator)

        elif agenda_item.has_document:
            self.add_agenda_item_document(index, agenda_item, generator)

    def add_sablon_for_paragraph(self, index, agenda_item, generator):
        committee = self.meeting.committee.resolve_committee()
        template = committee.get_paragraph_template()
        if template is None:
            return
        sablon = Sablon(template).process(
            ProtocolData(self.meeting, [agenda_item]).as_json())

        filename = u'{:03d}_paragraph_{}.docx'.format(
            index, safe_unicode(agenda_item.title))
        generator.add_file(filename, StringIO(sablon.file_data))

    def add_agenda_item_document(self, index, agenda_item, generator):
        document = agenda_item.resolve_document()

        filename = u'{:03d}_agenda_item_{}.docx'.format(
            index, safe_unicode(document.Title()))

        generator.add_file(filename, document.file.open())
