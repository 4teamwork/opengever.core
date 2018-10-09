from datetime import datetime
from ftw.bumblebee.tests.helpers import get_queue
from ftw.bumblebee.tests.helpers import reset_queue
from ftw.testing import freeze
from opengever.meeting import zipexport
from opengever.meeting.zipexport import MeetingZipExporter
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations
import pytz


class TestZipExporter(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    def test_zipexport_prepares_annotations_of_committee(self):
        self.login(self.meeting_user)

        zipexport.MeetingZipExporter(self.meeting.model)

        annotations = IAnnotations(self.committee)
        self.assertIn(zipexport.ZIP_JOBS_KEY, annotations)

    def test_collect_meeting_documents(self):
        self.login(self.meeting_user)
        self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.schedule_ad_hoc(self.meeting, 'ad-hoc agenda item')

        exporter = zipexport.MeetingZipExporter(self.meeting.model)

        self.assertEqual(3, len(exporter._collect_meeting_documents()))

    def test_queues_demand_pdf_jobs_and_prepares_for_callback(self):
        self.login(self.meeting_user)
        self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.schedule_ad_hoc(self.meeting, 'ad-hoc agenda item')
        reset_queue()

        exporter = zipexport.MeetingZipExporter(self.meeting.model)
        public_id = exporter.demand_pdfs()
        queue = get_queue()
        self.assertEqual(3, len(queue.queue))

        annotations = IAnnotations(self.committee)
        zip_jobs = annotations[zipexport.ZIP_JOBS_KEY]
        self.assertIn(public_id, zip_jobs)

        zip_job_metadata = zip_jobs[public_id]
        internal_id = zip_job_metadata['internal_id']
        self.assertIn(internal_id, zip_jobs)
        self.assertEqual(public_id, zip_job_metadata['public_id'])
        self.assertTrue(public_id != internal_id)
        self.assertEqual(2, len(zip_jobs.values()),
            'Expected zip job to be registered under public and internal id')
        self.assertEqual(zip_jobs[public_id], zip_jobs[internal_id],
            'Expected same zip job instance to be used')

        self.assertIn('documents', zip_job_metadata)
        document_jobs = zip_job_metadata['documents']
        self.assertEqual(3, len(document_jobs))

        doc = self.submitted_proposal.get_proposal_document()
        document_id = IUUID(doc)
        self.assertIn(document_id, document_jobs)

        doc_job = document_jobs[document_id]
        self.assertDictContainsSubset(
            {'status': 'converting'},
            doc_job)

    def test_zipexport_removes_expired_jobs(self):
        self.login(self.meeting_user)
        annotations = IAnnotations(self.committee)

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            exporter = MeetingZipExporter(self.meeting.model)
            old_public_id = exporter.demand_pdfs()
        zip_jobs = annotations[zipexport.ZIP_JOBS_KEY]
        old_zip_job = zip_jobs[old_public_id]

        with freeze(datetime(2017, 10, 18, 1, 0, tzinfo=pytz.utc)):
            new_exporter = MeetingZipExporter(self.meeting.model)
            new_public_id = new_exporter.demand_pdfs()
        new_zip_job = zip_jobs[new_public_id]

        self.assertEqual(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc),
                         old_zip_job['timestamp'])
        self.assertEqual(datetime(2017, 10, 18, 1, 0, tzinfo=pytz.utc),
                         new_zip_job['timestamp'])
        self.assertNotIn(old_public_id, zip_jobs)
        self.assertIn(new_public_id, zip_jobs)
