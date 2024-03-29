from ftw.zipexport.generation import ZipGenerator
from ftw.zipexport.utils import normalize_path
from logging import getLogger
from opengever.base import utils
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.handlebars import get_handlebars_template
from opengever.base.utils import disable_edit_bar
from opengever.meeting import _
from opengever.meeting.interfaces import IMeetingWrapper
from opengever.meeting.zipexport import MeetingDocumentZipper
from opengever.meeting.zipexport import MeetingZipExporter
from opengever.meeting.zipexport import ZipJobManager
from pkg_resources import resource_filename
from plone import api
from plone.namedfile.utils import stream_data
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zExceptions import MethodNotAllowed
from zExceptions import Redirect
from zope.i18n import translate
from zope.interface import alsoProvides
from ZPublisher.Iterators import filestream_iterator
import json
import os


logger = getLogger('opengever.meeting')


def require_job_id_parameter(request):
    job_id = request.get('job_id')
    if not job_id:
        raise BadRequest('must supply valid job_id of zip-job.')

    return job_id


def require_job(request, meeting, job_id):
    job_manager = ZipJobManager(meeting)

    try:
        job = job_manager.get_job(job_id)
    except KeyError:
        msg = _(u'msg_no_export_for_job_id',
                default=u'No zip job could be found for the supplied '
                        u'job id ${job_id}.',
                mapping={'job_id': job_id})
        api.portal.show_message(
            message=msg, request=request, type='error')
        raise Redirect(meeting.get_url())

    return job


class PollMeetingZip(BrowserView):
    """Poll for meeting zip progress, download once all files are available."""

    def __init__(self, context, request):
        super(PollMeetingZip, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        if self.request.method != 'POST':
            raise MethodNotAllowed()

        job_id = require_job_id_parameter(self.request)
        job = require_job(self.request, self.model, job_id)

        exporter = MeetingZipExporter(self.model, job_id)
        if exporter.is_finished_converting():
            exporter.generate_zipfile()

        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        return json.dumps(job.get_progress())


class DownloadMeetingZip(BrowserView):

    def __init__(self, context, request):
        super(DownloadMeetingZip, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        job_id = require_job_id_parameter(self.request)
        job = require_job(self.request, self.model, job_id)

        zip_file = job.get_zip_file()
        filename = u'{}.zip'.format(normalize_path(self.model.title))
        set_attachment_content_disposition(
            self.request, filename, file=zip_file)
        return stream_data(zip_file)


class DemandMeetingZip(BrowserView):
    """Display a view where the zip can be downloaded eventually."""

    def __init__(self, context, request):
        super(DemandMeetingZip, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        disable_edit_bar()
        alsoProvides(self.request, IDisableCSRFProtection)

        job_id = self.request.get('job_id', None)
        if job_id:
            # Render view in polling mode
            require_job(self.request, self.model, job_id)
            self.job_id = job_id
            return super(DemandMeetingZip, self).__call__()

        else:
            # Create a new job, and then redirect to view in polling mode
            logger.info('Starting PDF Zip export for %s' % self.model.get_url())
            job = MeetingZipExporter(self.model).demand_pdfs()
            url = "{}/@@demand_meeting_zip?job_id={}".format(
                self.context.absolute_url(), job.job_id)
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
            'msg_some_documents_remain_unconverted': translate(
                _(u'msg_some_documents_remain_unconverted',
                  default=u'Some documents could not be converted to PDF, '
                  u'their original files will be included in the Zip.'),
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
                  u'meeting is being generated.'),
                context=self.request),
            'desc_pdf_zip_contents': translate(
                _(u'desc_pdf_zip_contents',
                  default=u'The zip contains a PDF file for each document in '
                  u'this meeting and a JSON file which allows it to '
                  u'be imported by the meeting app.'),
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
        return "{}/@@poll_meeting_zip?job_id={}".format(
            self.context.absolute_url(), self.job_id)

    def download_url(self):
        return "{}/@@download_meeting_zip?job_id={}".format(
            self.context.absolute_url(), self.job_id)

    def meeting_url(self):
        return self.model.get_url()

    def zip_export_url(self):
        return self.model.get_url(view='export-meeting-zip')

    def skip_unconverted_url(self):
        return "{}/@@skip_unconverted?job_id={}".format(
            self.context.absolute_url(), self.job_id)

    def is_manager(self):
        return utils.is_manager()


class MeetingZipExportOriginals(BrowserView):
    """Iterate over meeting contents and return results in a .zip archive."""

    def __init__(self, context, request):
        super(MeetingZipExportOriginals, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        response = self.request.response

        with ZipGenerator() as generator:
            zipper = MeetingDocumentZipper(self.model, generator)
            zip_file = zipper.get_zip_file()

            filename = '{}.zip'.format(normalize_path(self.model.title))
            set_attachment_content_disposition(self.request, filename)

            # the following headers must be set manually as
            # set_attachment_content_disposition expects a Named(Blob)File
            response.setHeader(
                'Content-type', 'application/zip')
            response.setHeader(
                'Content-Length', os.stat(zip_file.name).st_size)

            return filestream_iterator(zip_file.name, 'rb')


class MeetingSkipUnconverted(BrowserView):
    """View to skip unconveretd files in meeting Zip job."""

    def __init__(self, context, request):
        super(MeetingSkipUnconverted, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        job_id = require_job_id_parameter(self.request)
        job = require_job(self.request, self.model, job_id)

        exporter = MeetingZipExporter(self.model, job_id)
        exporter.mark_unconverted_docs_as_skipped()

        url = "{}/@@demand_meeting_zip?job_id={}".format(
            self.context.absolute_url(), job.job_id)
        return self.request.RESPONSE.redirect(url)
