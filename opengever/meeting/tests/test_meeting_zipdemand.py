from ftw.testbrowser import browsing
from opengever.meeting.zipexport import MeetingZipExporter
from opengever.meeting.zipexport import ZipJobManager
from opengever.testing import IntegrationTestCase
from plone.namedfile.file import NamedBlobFile
from plone.uuid.interfaces import IUUID


class TestPollMeetingZip(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    @browsing
    def test_zip_polling_view_reports_converting(self, browser):
        self.login(self.meeting_user, browser)

        job_manager = ZipJobManager(self.meeting.model)
        zip_job = job_manager.create_job()
        zip_job.add_doc_status(IUUID(self.document), {'status': 'converting'})

        browser.open(
            self.meeting,
            view='poll_meeting_zip?job_id={}'.format(zip_job.job_id),
            method='POST')
        self.assertEqual(1, browser.json['converting'])

    @browsing
    def test_zip_polling_view_creates_zip_when_all_finished(self, browser):
        self.login(self.meeting_user, browser)

        job_manager = ZipJobManager(self.meeting.model)
        zip_job = job_manager.create_job()
        zip_job.add_doc_status(
            IUUID(self.document),
            {'status': 'finished', 'blob': NamedBlobFile(data='foo')})

        browser.open(
            self.meeting,
            view='poll_meeting_zip?job_id={}'.format(zip_job.job_id),
            method='POST')
        self.assertEqual(1, browser.json['zipped'], browser.json)

    @browsing
    def test_zip_polling_view_reports_skipped(self, browser):
        self.login(self.meeting_user, browser)

        job_manager = ZipJobManager(self.meeting.model)
        zip_job = job_manager.create_job()
        zip_job.add_doc_status(IUUID(self.document), {'status': 'skipped'})

        browser.open(
            self.meeting,
            view='poll_meeting_zip?job_id={}'.format(zip_job.job_id),
            method='POST')
        self.assertEqual(1, browser.json['skipped'])


class TestDownloadMeetingZip(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    @browsing
    def test_download_meeting_zip(self, browser):
        self.login(self.meeting_user, browser)

        exporter = MeetingZipExporter(self.meeting.model)
        exporter.zip_job = exporter.job_manager.create_job()
        exporter.zip_job.add_doc_status(
            IUUID(self.document), {'status': 'converting'})

        doc_in_job_id = exporter.zip_job._get_doc_in_job_id(self.document)
        exporter.receive_pdf(doc_in_job_id,
                             'application/pdf',
                             'i am a apdf.')
        exporter.generate_zipfile()

        browser.open(
            self.meeting,
            view='download_meeting_zip?job_id={}'.format(exporter.zip_job.job_id))
        self.assertEquals('application/zip', browser.contenttype)
