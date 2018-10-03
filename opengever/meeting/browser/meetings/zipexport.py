from ftw.zipexport.generation import ZipGenerator
from ftw.zipexport.utils import normalize_path
from opengever.base.handlebars import get_handlebars_template
from opengever.base.utils import disable_edit_bar
from opengever.meeting import _
from opengever.meeting.command import AgendaItemListOperations
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import MergeDocxProtocolCommand
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.exceptions import AgendaItemListMissingTemplate
from opengever.meeting.interfaces import IMeetingWrapper
from opengever.meeting.zipexport import MeetingZipExporter
from pkg_resources import resource_filename
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from StringIO import StringIO
from zExceptions import BadRequest
from zope.i18n import translate
from zope.interface import alsoProvides
from ZPublisher.Iterators import filestream_iterator
import json
import os
import pytz
import uuid


class PollMeetingZip(BrowserView):
    """Poll for meeting zip status, download once all files are available."""

    def __init__(self, context, request):
        super(PollMeetingZip, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        public_id = self.request.get('public_id')
        if not public_id:
            raise BadRequest('must supply public_id of zip-job.')

        # find committee
        committee_model = self.model.committee
        committee = committee_model.oguid.resolve_object()
        public_id = uuid.UUID(public_id)

        exporter = MeetingZipExporter(self.model, committee, public_id=public_id)
        status = exporter.get_status()

        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        return json.dumps(status)


class DownloadMeetingZip(BrowserView):

    def __init__(self, context, request):
        super(DownloadMeetingZip, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        public_id = self.request.get('public_id')
        if not public_id:
            raise BadRequest('must supply public_id of zip-job.')

        # find committee
        committee_model = self.model.committee
        committee = committee_model.oguid.resolve_object()
        public_id = uuid.UUID(public_id)

        exporter = MeetingZipExporter(self.model, committee, public_id=public_id)

        response = self.request.response
        with ZipGenerator() as generator:
            exporter.zip_documents(generator)
            zip_file = generator.generate()
            filename = '{}.zip'.format(normalize_path(self.model.title))
            response.setHeader(
                'Content-Disposition',
                'inline; filename="{0}"'.format(
                    safe_unicode(filename).encode('utf-8')))
            response.setHeader(
                'Content-type', 'application/zip')
            response.setHeader(
                'Content-Length', os.stat(zip_file.name).st_size)

            return filestream_iterator(zip_file.name, 'rb')


class DemandMeetingZip(BrowserView):
    """Display a view where the zip can be downloaded eventually."""

    def __init__(self, context, request):
        super(DemandMeetingZip, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        disable_edit_bar()
        alsoProvides(self.request, IDisableCSRFProtection)

        committee_model = self.model.committee
        committee = committee_model.oguid.resolve_object()

        public_id = self.request.get('public_id', None)
        if public_id:
            # XXX validate id
            self.public_id = public_id
            return super(DemandMeetingZip, self).__call__()

        else:
            public_id = MeetingZipExporter(self.model, committee).demand_pdfs()
            self.public_id = str(public_id)
            url = "{}/@@demand_meeting_zip?public_id={}".format(
                self.context.absolute_url(), self.public_id)
            return self.request.RESPONSE.redirect(url)

    @property
    def vuejs_template(self):
        return get_handlebars_template(
            resource_filename('opengever.meeting.browser.meetings',
                              'templates/demand_zip.html'))

    def visible_in_actions_menu(self):
        """Returns ``True`` when the zip export action should be displayed
        in the actions menu.

        The action should only appear when we are on a meeting view..
        """
        return IMeetingWrapper.providedBy(self.context)

    def get_zip_export_title(self):
        return _(u'title_zip_export',
                 default=u'Zip export: ${title}',
                 mapping={'title': self.model.get_title()})

    def translations(self):
        return json.dumps({
            'label_info': translate(
                _(u'label_info', default=u'Information'),
                context=self.request),
            'label_warning': translate(
                _(u'label_warning', default=u'Warning'),
                context=self.request),
            'label_error': translate(
                _(u'label_error', default=u'Error'),
                context=self.request),
            'msg_some_documents_remain_uncoverted': translate(
                _(u'msg_some_documents_remain_uncoverted',
                  default=u'Some documents could not be converted to PDF, '
                           'their original files will be included in the '
                           'Zip.'),
                context=self.request),
            'msg_zip_ready_for_download': translate(
                _(u'msg_zip_ready_for_download',
                  default=u'The zip file is ready for download.'),
                context=self.request),
            'msg_zip_timeout': translate(
                _(u'msg_zip_timeout',
                  default=u'Generating the Zip took too long.'),
                context=self.request),
            'msg_zip_error': translate(
                _(u'msg_zip_error',
                  default=u'There was an error while generating the Zip.'),
                context=self.request),
            'msg_zip_creation_in_progress': translate(
                _(u'msg_zip_creation_in_progress',
                  default=u'A Zip file with PDFs for all documents of this '
                           'meeting is being generated.'),
                context=self.request),
            'desc_pdf_zip_contents': translate(
                _(u'desc_pdf_zip_contents',
                  default=u'The zip contains a PDF file for each document in '
                           'this meeting and a JSON file which allows it to '
                           'be imported by the meeting app.'),
                context=self.request),
            'label_button_download_zip': translate(
                _(u'label_button_download_zip',
                  default=u'Download Zip'),
                context=self.request),
            'label_button_error': translate(
                _(u'label_button_error',
                  default=u'Error Generating Zip'),
                context=self.request),
            'label_button_creation_in_progress': translate(
                _(u'label_button_creation_in_progress',
                  default=u'Generating Zip ...'),
                context=self.request),
            'label_backlink_to_meeting': translate(
                _(u'label_backlink_to_meeting',
                  default=u'Back to the meeting'),
                context=self.request),
        })

    def poll_url(self):
        return "{}/@@poll_meeting_zip?public_id={}".format(
            self.context.absolute_url(), self.public_id)

    def download_url(self):
        return "{}/@@download_meeting_zip?public_id={}".format(
            self.context.absolute_url(), self.public_id)

    def meeting_url(self):
        return self.model.get_url()

    def zip_export_url(self):
        return self.model.get_url(view='export-meeting-zip')


class MeetingZipExport(BrowserView):
    """Iterate over meeting contents and return results in a .zip archive."""

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
            self.add_agenda_item_proposal_documents(generator)

            # Agenda items list
            try:
                generator.add_file(*self.get_agendaitem_list())
            except AgendaItemListMissingTemplate:
                pass

            generator.add_file(*self.get_meeting_json())

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
        command = MergeDocxProtocolCommand(
            self.context,
            self.model,
            operations)

        filename = u'{}.docx'.format(operations.get_title(self.model))
        return (filename, StringIO(command.generate_file_data()))

    def add_agenda_item_proposal_documents(self, generator):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.has_document:
                continue

            document = agenda_item.resolve_document()
            if not document:
                continue

            path = agenda_item.get_document_filename_for_zip(document)
            generator.add_file(path, document.get_file().open())

    def add_agenda_items_attachments(self, generator):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.has_submitted_documents():
                continue

            for document in agenda_item.proposal.resolve_submitted_documents():
                path = agenda_item.get_document_filename_for_zip(document)
                generator.add_file(path, document.get_file().open())

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

    def get_meeting_json(self):
        json_data = {
            'version': '1.0.0',
            'meetings': [self.context.get_data_for_zip_export()],
        }
        return 'meeting.json', StringIO(json.dumps(json_data,
                                                   sort_keys=True,
                                                   indent=4))
