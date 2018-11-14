from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import get_demand_callback_access_token
from ftw.testbrowser import browsing
from opengever.meeting.zipexport import MeetingZipExporter
from opengever.testing import IntegrationTestCase
from plone.namedfile.file import NamedBlobFile
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
        doc_in_job_id = exporter.zip_job._get_doc_in_job_id(document)
        return {
            'token': get_demand_callback_access_token(),
            'status': 'success',
            'document': IBumblebeeDocument(document).get_checksum(),
            'opaque_id': doc_in_job_id,
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

        document_id = IUUID(proposal_document)
        doc_status = exporter.zip_job.get_doc_status(document_id)
        self.assertEqual('finished', doc_status['status'])
        self.assertEqual('the pdf', doc_status['blob'].data)

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

        self.assertIn('zip_file', zip_job._data)
        zip_file = zip_job.get_zip_file()
        self.assertIsInstance(zip_file, NamedBlobFile)

        document_id = IUUID(proposal_document)
        doc_status = zip_job.get_doc_status(document_id)
        self.assertEqual('zipped', doc_status['status'])
        self.assertNotIn('blob', doc_status)

        attachment_doc_id = IUUID(proposal_attachment)
        attachment_doc_status = zip_job.get_doc_status(attachment_doc_id)
        self.assertEqual('zipped', attachment_doc_status['status'])
        self.assertNotIn('blob', attachment_doc_status)

    @browsing
    def test_skipped_demand_response_callback(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        self.schedule_proposal(self.meeting, self.submitted_proposal)
        proposal_document = self.submitted_proposal.get_proposal_document()
        exporter = MeetingZipExporter(self.meeting.model)
        exporter.demand_pdfs()

        doc_in_job_id = exporter.zip_job._get_doc_in_job_id(proposal_document)
        fields = {
            'token': get_demand_callback_access_token(),
            'status': 'skipped',
            'document': IBumblebeeDocument(proposal_document).get_checksum(),
            'opaque_id': doc_in_job_id,
        }
        self.do_callback_request(browser, fields)

        document_id = IUUID(proposal_document)
        doc_status = exporter.zip_job.get_doc_status(document_id)
        self.assertEqual('skipped', doc_status['status'])

    @browsing
    def test_failed_demand_response_callback(self, browser):
        # don't login in browser as the view is public
        self.login(self.meeting_user)

        self.schedule_proposal(self.meeting, self.submitted_proposal)
        proposal_document = self.submitted_proposal.get_proposal_document()
        exporter = MeetingZipExporter(self.meeting.model)
        # XXX: return zib_job here?
        exporter.demand_pdfs()

        doc_in_job_id = exporter.zip_job._get_doc_in_job_id(proposal_document)
        fields = {
            'token': get_demand_callback_access_token(),
            'status': 'failed',
            'document': IBumblebeeDocument(proposal_document).get_checksum(),
            'opaque_id': doc_in_job_id,
        }
        self.do_callback_request(browser, fields)

        document_id = IUUID(proposal_document)
        doc_status = exporter.zip_job.get_doc_status(document_id)
        self.assertEqual('skipped', doc_status['status'])
