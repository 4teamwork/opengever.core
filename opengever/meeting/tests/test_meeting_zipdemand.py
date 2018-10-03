from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.meeting.zipexport import MeetingZipExporter


class TestPollMeetingZip(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    @browsing
    def test_zip_polling_view_reports_converting(self, browser):
        self.login(self.meeting_user, browser)

        exporter = MeetingZipExporter(self.meeting, self.committee)
        zip_job = exporter._prepare_zip_job_metadata()
        exporter._append_document_job_metadata(
            zip_job, self.document, None, 'converting')

        browser.open(
            self.meeting,
            view='poll_meeting_zip?public_id={}'.format(exporter.public_id))
        self.assertEqual(
            {u'converting': 1, u'finished': 0, u'skipped': 0},
            browser.json)

    @browsing
    def test_zip_polling_view_reports_finished(self, browser):
        self.login(self.meeting_user, browser)

        exporter = MeetingZipExporter(self.meeting, self.committee)
        zip_job = exporter._prepare_zip_job_metadata()
        exporter._append_document_job_metadata(
            zip_job, self.document, None, 'finished')

        browser.open(
            self.meeting,
            view='poll_meeting_zip?public_id={}'.format(exporter.public_id))
        self.assertEqual(
            {u'converting': 0, u'finished': 1, u'skipped': 0},
            browser.json)

    @browsing
    def test_zip_polling_view_reports_skipped(self, browser):
        self.login(self.meeting_user, browser)

        exporter = MeetingZipExporter(self.meeting, self.committee)
        zip_job = exporter._prepare_zip_job_metadata()
        exporter._append_document_job_metadata(
            zip_job, self.document, None, 'skipped')

        browser.open(
            self.meeting,
            view='poll_meeting_zip?public_id={}'.format(exporter.public_id))
        self.assertEqual(
            {u'converting': 0, u'finished': 0, u'skipped': 1},
            browser.json)
