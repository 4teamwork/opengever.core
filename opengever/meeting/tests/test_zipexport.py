from datetime import datetime
from ftw.bumblebee.tests.helpers import get_queue
from ftw.bumblebee.tests.helpers import reset_queue
from ftw.testing import freeze
from opengever.meeting.zipexport import MeetingZipExporter
from opengever.meeting.zipexport import ZIP_JOBS_KEY
from opengever.meeting.zipexport import ZipJob
from opengever.meeting.zipexport import ZipJobManager
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations
import pytz


class TestZipExporter(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    def test_collect_meeting_documents(self):
        self.login(self.meeting_user)
        self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.schedule_ad_hoc(self.meeting, 'ad-hoc agenda item')

        exporter = MeetingZipExporter(self.meeting.model)

        self.assertEqual(3, len(exporter._collect_meeting_documents()))

    def test_queues_demand_pdf_jobs_and_prepares_for_callback(self):
        self.login(self.meeting_user)
        self.schedule_proposal(self.meeting, self.submitted_proposal)
        self.schedule_ad_hoc(self.meeting, 'ad-hoc agenda item')
        reset_queue()

        exporter = MeetingZipExporter(self.meeting.model)
        job = exporter.demand_pdfs()
        queue = get_queue()
        self.assertEqual(3, len(queue.queue))

        annotations = IAnnotations(self.committee)
        zip_jobs = annotations[ZIP_JOBS_KEY]
        self.assertIn(job.job_id, zip_jobs)

        zip_job_metadata = zip_jobs[job.job_id]

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


class TestZipJobManager(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    def test_create_job_creates_new_job(self):
        self.login(self.meeting_user)

        job_manager = ZipJobManager(self.meeting.model)
        with freeze(datetime(2017, 10, 18, 1, 0, tzinfo=pytz.utc)):
            job = job_manager.create_job()

        self.assertIsInstance(job, ZipJob)

        job_id = job.job_id
        self.assertIn(job_id, job_manager._zip_jobs)
        self.assertItemsEqual(
            ['timestamp', 'documents', 'job_id'],
            set(job._data.keys()))

        self.assertEqual(job_id, job._data['job_id'])
        self.assertEqual(
            datetime(2017, 10, 18, 1, 0, tzinfo=pytz.utc),
            job._data['timestamp'])

        self.assertEqual({}, dict(job._data['documents']))

    def test_create_job_prepares_annotations(self):
        self.login(self.meeting_user)

        annotations = IAnnotations(self.committee)

        self.assertNotIn(ZIP_JOBS_KEY, annotations)
        ZipJobManager(self.meeting.model).create_job()
        self.assertIn(ZIP_JOBS_KEY, annotations)

    def test_create_job_cleans_old_jobs(self):
        self.login(self.meeting_user)

        job_manager = ZipJobManager(self.meeting.model)

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            old_job = job_manager.create_job()

        with freeze(datetime(2017, 10, 18, 1, 0, tzinfo=pytz.utc)):
            new_job = job_manager.create_job()

        self.assertEqual(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc),
                         old_job.timestamp)
        self.assertEqual(datetime(2017, 10, 18, 1, 0, tzinfo=pytz.utc),
                         new_job.timestamp)
        self.assertNotIn(old_job.job_id, job_manager._zip_jobs)
        self.assertIn(new_job.job_id, job_manager._zip_jobs)

    def test_get_job_returns_job_instance(self):
        self.login(self.meeting_user)

        job_manager = ZipJobManager(self.meeting.model)
        new_job_id = job_manager.create_job().job_id

        job = job_manager.get_job(new_job_id)
        self.assertIsInstance(job, ZipJob)

    def test_get_job_raises_key_error_for_nonexistent_job(self):
        self.login(self.meeting_user)

        job_manager = ZipJobManager(self.meeting.model)
        with self.assertRaises(KeyError):
            job_manager.get_job('doesnt-exist')

    def test_remove_job_deletes_job(self):
        self.login(self.meeting_user)

        job_manager = ZipJobManager(self.meeting.model)
        job = job_manager.create_job()

        self.assertIn(job.job_id, job_manager._zip_jobs)
        job_manager.remove_job(job.job_id)
        self.assertNotIn(job.job_id, job_manager._zip_jobs)

    def test_remove_job_raises_key_error_for_nonexistent_job(self):
        self.login(self.meeting_user)

        job_manager = ZipJobManager(self.meeting.model)
        with self.assertRaises(KeyError):
            job_manager.remove_job('doesnt-exist')


class TestZipJob(IntegrationTestCase):

    features = ('meeting', 'bumblebee')

    def setUp(self):
        super(TestZipJob, self).setUp()
        self.login(self.meeting_user)
        self.job_manager = ZipJobManager(self.meeting.model)
        self.job = self.job_manager.create_job()

    def test_exposes_job_id(self):
        self.assertIsInstance(self.job.job_id, str)
        self.assertEqual(self.job._data['job_id'], self.job.job_id)

    def test_exposes_timestamp(self):
        self.assertIsInstance(self.job.job_id, str)
        self.assertEqual(self.job._data['timestamp'], self.job.timestamp)

    def test_add_and_get_doc_status(self):
        document_id = IUUID(self.meeting_document)
        self.job.add_doc_status(document_id, {'status': 'converting'})
        doc_status = self.job.get_doc_status(document_id)
        self.assertEqual({'status': 'converting'}, dict(doc_status))

    def test_update_doc_status(self):
        document_id = IUUID(self.meeting_document)
        self.job.add_doc_status(document_id, {'status': 'converting'})
        self.job.update_doc_status(document_id, {'status': 'finished'})
        doc_status = self.job.get_doc_status(IUUID(self.meeting_document))
        self.assertEqual({'status': 'finished'}, dict(doc_status))

    def test_lists_document_ids(self):
        document_id = IUUID(self.meeting_document)
        self.job.add_doc_status(document_id, {'status': 'converting'})
        self.assertEqual([document_id],
                         self.job.list_document_ids())

    def test_is_finished_returns_true_if_zipfile_blob_present(self):
        self.assertFalse(self.job.is_finished())
        self.job.set_zip_file('ZIP')
        self.assertTrue(self.job.is_finished())

    def test_get_zip_file_returns_zip_file_blob(self):
        self.job.set_zip_file('ZIP')
        self.assertEqual('ZIP', self.job.get_zip_file())

    def test_get_doc_in_job_id_returns_combined_job_and_doc_id(self):
        document_id = IUUID(self.meeting_document)
        self.job.add_doc_status(document_id, {'status': 'converting'})
        self.assertEqual(
            '{}:{}'.format(self.job.job_id, document_id),
            self.job._get_doc_in_job_id(self.meeting_document))

    def test_get_progress_returns_summary_of_doc_statuses(self):
        self.job.add_doc_status(IUUID(self.meeting_document), {'status': 'converting'})
        self.job.add_doc_status(IUUID(self.document), {'status': 'finished'})
        self.job.add_doc_status(IUUID(self.subdocument), {'status': 'skipped'})
        self.job.add_doc_status(IUUID(self.taskdocument), {'status': 'zipped'})
        self.assertEqual(
            {'converting': 1,
             'finished': 1,
             'skipped': 1,
             'is_finished': False,
             'zipped': 1},
            self.job.get_progress())
