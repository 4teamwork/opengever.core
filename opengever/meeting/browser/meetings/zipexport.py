from ftw import bumblebee
from ftw.bumblebee.usersalt import get_user_salt
from ftw.bumblebee.utils import get_cookie_name
from ftw.bumblebee.viewlets.cookie import encode_cookie
from ftw.zipexport.generation import ZipGenerator
from ftw.zipexport.utils import normalize_path
from netsight.async.browser.BaseAsyncView import BaseAsyncView
from opengever.meeting.command import AgendaItemListOperations
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import MergeDocxProtocolCommand
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.exceptions import AgendaItemListMissingTemplate
from opengever.meeting.interfaces import IMeetingWrapper
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from StringIO import StringIO
from tempfile import TemporaryFile
from ZPublisher.Iterators import filestream_iterator
import json
import os
import pytz
import requests
import shutil
import tempfile


MEETINGZIPPREFIX = '_meeting_zip_export'


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

        The action should only appear when we are on a meeting view..
        """
        return IMeetingWrapper.providedBy(self.context)

    def generate_zip(self, process_id=None):
        response = self.request.response

        with ZipGenerator() as generator:
            # Protocol
            generator.add_file(*self.get_protocol())

            # Agenda items
            self.add_agenda_items_attachments(generator)
            self.add_agenda_item_proposal_documents(generator)

            # Agenda items list
            try:
                generator.add_file(*self.get_agendaitem_list())
            except AgendaItemListMissingTemplate:
                pass

            generator.add_file(*self.get_meeting_json())

            if process_id:
                self.set_progress(process_id, 90)

            # Return zip
            zip_file = generator.generate()

            if process_id:
                tmpdir = tempfile.gettempdir()
                shutil.copy(zip_file.name, '{}/{}{}'.format(tmpdir,
                                                            process_id,
                                                            MEETINGZIPPREFIX))
                return

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

    def get_bumblebee_cookie(self):
        return {get_cookie_name(): encode_cookie({'salt': get_user_salt()})}

    def get_pdf_for_document(self, doc, filename):
        """Fetch the pdf document from the bumblebee service. If the
        PDF document ist not yet created, the original document is returned.
        """
        pdf_url = bumblebee.get_service_v3().get_representation_url(doc, 'pdf')

        # Disallow redirects to not handle the fallback image for not existing
        # pdfs as a converted pdf
        r = requests.get(pdf_url,
                         stream=True,
                         cookies=self.get_bumblebee_cookie(),
                         allow_redirects=False)

        if r.status_code == 200:
            tmpfile = TemporaryFile()
            for chunk in r:
                tmpfile.write(chunk)

            tmpfile.seek(0)
            filename, ext = os.path.splitext(filename)
            new_filename = u'{}.pdf'.format(filename)
            return new_filename, tmpfile

        # Fallback if the pdf request was not sucessfull
        return filename, doc.file.open()

    def get_protocol(self):
        if self.model.has_protocol_document():
            protocol = self.model.protocol_document.resolve_document()
            protocol_modified = protocol.modified().asdatetime().astimezone(
                pytz.utc)

            if self.model.modified < protocol_modified:
                # Return current protocol
                filename = u'{}.docx'.format(safe_unicode(protocol.Title()))
                return self.get_pdf_for_document(protocol, filename)

        # Create new protocol
        operations = ProtocolOperations()
        command = MergeDocxProtocolCommand(
            self.context,
            self.model,
            operations,
            lock_document_after_creation=False)

        filename = u'{}.docx'.format(operations.get_title(self.model))
        return (filename, StringIO(command.generate_file_data()))

    def add_agenda_item_proposal_documents(self, generator):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.has_document:
                continue

            document = agenda_item.resolve_document()
            if not document:
                continue

            filename = agenda_item.get_document_filename_for_zip(document)
            generator.add_file(*self.get_pdf_for_document(document, filename))

    def add_agenda_items_attachments(self, generator):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.has_submitted_documents():
                continue

            for document in agenda_item.proposal.resolve_submitted_documents():
                filename = agenda_item.get_document_filename_for_zip(document)
                generator.add_file(*self.get_pdf_for_document(document, filename))

    def get_agendaitem_list(self):
        if self.model.has_agendaitem_list_document():
            agendaitem_list = self.model.agendaitem_list_document.resolve_document()
            agendaitem_list_modified = agendaitem_list.modified().asdatetime().astimezone(
                pytz.utc)

            if self.model.modified < agendaitem_list_modified:
                # Return current protocol

                filename = u'{}.docx'.format(safe_unicode(agendaitem_list.Title()))
                return self.get_pdf_for_document(agendaitem_list, filename)

        # Create new protocol
        operations = AgendaItemListOperations()
        command = CreateGeneratedDocumentCommand(
            self.context,
            self.model,
            operations,
        )

        filename = u'{}.docx'.format(operations.get_title(self.model))
        return (filename, StringIO(command.generate_file_data()))

    def get_meeting_json(self):
        json_data = {
            'version': '1.0.0',
            'meetings': [self.context.get_data_for_zip_export()],
        }
        return 'meeting.json', StringIO(json.dumps(json_data,
                                                   sort_keys=True,
                                                   indent=4))


class AsyncMeetingZipExport(BaseAsyncView, MeetingZipExport):

    def publishTraverse(self, request, name):
        if name in ('completed', 'processing', 'result', 'download'):
            return getattr(self, name)

        return self

    def __init__(self, context, request):
        super(AsyncMeetingZipExport, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        process_id = self._run()
        self.request.response.setHeader('Content-Type', 'application/json')
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return json.dumps({'process_id': process_id})

    def __run__(self, process_id=None):
        self.set_progress(process_id, 10)
        self.generate_zip(process_id=process_id)

    def download(self, process_id):
        """Downloads the zipfile"""
        response = self.request.response
        tmpdir = tempfile.gettempdir()

        zip_file_path = '{}/{}{}'.format(tmpdir,
                                         process_id,
                                         MEETINGZIPPREFIX)
        with open(zip_file_path, 'r') as zip_file:
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
