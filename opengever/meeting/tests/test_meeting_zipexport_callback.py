from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import get_download_token
from ftw.testbrowser import browsing
from opengever.meeting.zipexport import MeetingZipExporter
from opengever.testing import IntegrationTestCase
from requests_toolbelt.multipart.encoder import MultipartEncoder


class TestReceiveDemandCallbackMeetingZip(IntegrationTestCase):

    features = ('meeting', 'bumblebee')
    maxDiff = None

    def do_callback_request(self, browser, fields):
        encoder = MultipartEncoder(fields=fields)
        data = encoder.to_string()
        headers = {'Content-Type': encoder.content_type}

        browser.open(
            self.meeting, view='receive_meeting_zip_pdf',
            method='POST', data=data, headers=headers)

    @browsing
    def test_get_method_is_disallowed(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        with browser.expect_http_error(405):
            browser.open(self.meeting, view='receive_meeting_zip_pdf')

    @browsing
    def test_successful_demand_response_callback(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        exporter = MeetingZipExporter(self.meeting.model)
        zip_job = exporter._prepare_zip_job_metadata()
        exporter._append_document_job_metadata(
            zip_job, self.taskdocument, 'converting')
        document_info = exporter._append_document_job_metadata(
            zip_job, self.document, 'converting')

        fields = {
            'token': get_download_token(),
            'status': 'success',
            'document': IBumblebeeDocument(self.document).get_checksum(),
            'opaque_id': exporter._get_opaque_id(self.document),
            'pdf': ('converted.pdf', 'the pdf', 'application/pdf'),
        }
        self.do_callback_request(browser, fields)

        self.assertEqual('finished', document_info['status'])
        self.assertEqual('the pdf', document_info['blob'].data)

    @browsing
    def test_zip_file_is_created_for_last_sucessful_callback(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        exporter = MeetingZipExporter(self.meeting.model)
        zip_job = exporter._prepare_zip_job_metadata()
        document_info = exporter._append_document_job_metadata(
            zip_job, self.document, 'converting')

        fields = {
            'token': get_download_token(),
            'status': 'success',
            'document': IBumblebeeDocument(self.document).get_checksum(),
            'opaque_id': exporter._get_opaque_id(self.document),
            'pdf': ('converted.pdf', 'the pdf', 'application/pdf'),
        }
        self.do_callback_request(browser, fields)

        self.assertEqual('zipped', document_info['status'])
        self.assertNotIn('blob', document_info)
        self.assertIn('zip_file', zip_job)

    @browsing
    def test_skipped_demand_response_callback(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        exporter = MeetingZipExporter(self.meeting.model)
        zip_job = exporter._prepare_zip_job_metadata()
        document_info = exporter._append_document_job_metadata(
            zip_job, self.document, 'converting')

        fields = {
            'token': get_download_token(),
            'status': 'skipped',
            'document': IBumblebeeDocument(self.document).get_checksum(),
            'opaque_id': exporter._get_opaque_id(self.document),
        }
        self.do_callback_request(browser, fields)

        self.assertEqual('skipped', document_info['status'])

    @browsing
    def test_failed_demand_response_callback(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        exporter = MeetingZipExporter(self.meeting.model)
        zip_job = exporter._prepare_zip_job_metadata()
        document_info = exporter._append_document_job_metadata(
            zip_job, self.document, 'converting')

        fields = {
            'token': get_download_token(),
            'status': 'failed',
            'document': IBumblebeeDocument(self.document).get_checksum(),
            'opaque_id': exporter._get_opaque_id(self.document),
        }
        self.do_callback_request(browser, fields)

        self.assertEqual('skipped', document_info['status'])
