from ftw.bumblebee.tests.helpers import get_queue
from ftw.bumblebee.tests.helpers import reset_queue
from opengever.meeting import zipexport
from opengever.testing import IntegrationTestCase
from zope.annotation import IAnnotations
from ftw.bumblebee.interfaces import IBumblebeeDocument


class TestZipExporter(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    def test_zipexport_prepares_annotations_of_committee(self):
        self.login(self.meeting_user)

        zipexport.MeetingZipExporter(self.meeting.model, self.committee)

        annotations = IAnnotations(self.committee)
        self.assertIn(zipexport.ZIP_JOBS_KEY, annotations)

    def test_collect_meeting_documents(self):
        self.login(self.meeting_user)
        self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.schedule_ad_hoc(self.meeting, 'ad-hoc agenda item')

        exporter = zipexport.MeetingZipExporter(
            self.meeting.model, self.committee)

        self.assertEqual(3, len(exporter._collect_meeting_documents()))

    def test_queues_demand_pdf_jobs_and_prepares_for_callback(self):
        self.login(self.meeting_user)
        self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.schedule_ad_hoc(self.meeting, 'ad-hoc agenda item')
        reset_queue()

        exporter = zipexport.MeetingZipExporter(
            self.meeting.model, self.committee)
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
        doc_checksum = IBumblebeeDocument(doc).get_checksum()
        self.assertIn(doc_checksum, document_jobs)

        doc_job = document_jobs[doc_checksum]
        self.assertDictContainsSubset(
            {'status': 'converting',
             'folder': 'Agenda item 1',
             'title': u'Vertr\xe4ge'},
            doc_job)
