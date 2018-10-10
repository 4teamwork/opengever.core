from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import get_download_token
from ftw.testbrowser import browsing
from opengever.meeting.zipexport import MeetingZipExporter
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from requests_toolbelt.multipart.encoder import MultipartEncoder


class TestReceiveDemandCallbackMeetingZip(IntegrationTestCase):

    features = ('meeting', 'bumblebee')
    maxDiff = None

    def do_callback_request(self, browser, fields):
        meeting = self.meeting
        encoder = MultipartEncoder(fields=fields)
        data = encoder.to_string()
        headers = {'Content-Type': encoder.content_type}

        with self.logout():
            browser.open(
                meeting, view='receive_meeting_zip_pdf',
                method='POST', data=data, headers=headers)

    def success_callback_fields(self, exporter, document):
        return {
            'token': get_download_token(),
            'status': 'success',
            'document': IBumblebeeDocument(document).get_checksum(),
            'opaque_id': exporter._get_opaque_id(document),
            'pdf': ('converted.pdf', 'the pdf', 'application/pdf'),
        }

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

        self.schedule_proposal(self.meeting, self.submitted_proposal)
        proposal_document = self.submitted_proposal.get_proposal_document()
        exporter = MeetingZipExporter(self.meeting.model)
        exporter.demand_pdfs()

        self.do_callback_request(
            browser,
            self.success_callback_fields(exporter, proposal_document))

        document_info = exporter.zip_job['documents'][IUUID(proposal_document)]
        self.assertEqual('finished', document_info['status'])
        self.assertEqual('the pdf', document_info['blob'].data)

    @browsing
    def test_zip_file_is_created_for_last_sucessful_callback(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        self.schedule_proposal(self.meeting, self.submitted_proposal)
        proposal_document = self.submitted_proposal.get_proposal_document()
        proposal_attachment = self.submitted_proposal.get_documents()[0]
        exporter = MeetingZipExporter(self.meeting.model)
        exporter.demand_pdfs()

        self.do_callback_request(
            browser,
            self.success_callback_fields(exporter, proposal_document))
        self.do_callback_request(
            browser,
            self.success_callback_fields(exporter, proposal_attachment))

        zip_job = exporter.zip_job
        self.assertIn('zip_file', zip_job)

        document_info = zip_job['documents'][IUUID(proposal_document)]
        self.assertEqual('zipped', document_info['status'])
        self.assertNotIn('blob', document_info)

        attachment_info = zip_job['documents'][IUUID(proposal_attachment)]
        self.assertEqual('zipped', attachment_info['status'])
        self.assertNotIn('blob', attachment_info)

    @browsing
    def test_skipped_demand_response_callback(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        self.schedule_proposal(self.meeting, self.submitted_proposal)
        proposal_document = self.submitted_proposal.get_proposal_document()
        exporter = MeetingZipExporter(self.meeting.model)
        exporter.demand_pdfs()

        fields = {
            'token': get_download_token(),
            'status': 'skipped',
            'document': IBumblebeeDocument(proposal_document).get_checksum(),
            'opaque_id': exporter._get_opaque_id(proposal_document),
        }
        self.do_callback_request(browser, fields)

        document_info = exporter.zip_job['documents'][IUUID(proposal_document)]
        self.assertEqual('skipped', document_info['status'])

    @browsing
    def test_failed_demand_response_callback(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        self.schedule_proposal(self.meeting, self.submitted_proposal)
        proposal_document = self.submitted_proposal.get_proposal_document()
        exporter = MeetingZipExporter(self.meeting.model)
        exporter.demand_pdfs()

        fields = {
            'token': get_download_token(),
            'status': 'failed',
            'document': IBumblebeeDocument(proposal_document).get_checksum(),
            'opaque_id': exporter._get_opaque_id(proposal_document),
        }
        self.do_callback_request(browser, fields)

        document_info = exporter.zip_job['documents'][IUUID(proposal_document)]
        self.assertEqual('skipped', document_info['status'])
