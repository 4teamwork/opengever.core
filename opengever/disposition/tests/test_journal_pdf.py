from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.disposition.appraisal import IAppraisal
from opengever.document.interfaces import IDossierJournalPDFMarker
from opengever.dossier.behaviors.dossier import IDossier
from opengever.nightlyjobs.interfaces import INightlyJobProvider
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import logging


class JournalPDFTestHelper(object):

    def offer(self, dossier, browser=None):
        dossier.offer()
        IAppraisal(self.disposition).initialize(dossier)

    def retract(self, dossier, browser=None):
        dossier.retract()
        IAppraisal(self.disposition).drop(dossier)

    def assert_create_journal_pdf_jobs_pending(self, expected, dossiers):
        provider = getMultiAdapter(
            (self.portal, self.request, logging.getLogger()),
            INightlyJobProvider,
            name='create-dossier-journal-pdf',
        )
        for dossier in dossiers:
            intids = getUtility(IIntIds)
            int_id = intids.getId(dossier)
            self.assertEqual(expected, int_id in provider.get_queue())


class TestJournalPDFJobs(IntegrationTestCase, JournalPDFTestHelper):

    def interrupt_if_necessary(self):
        """Stub out the runner's `interrupt_if_necessary` function.
        """

    def execute_nightly_jobs(self, expected=None):
        """Run all pending journal PDF nightly jobs, and assert on the
        number of jobs.
        """
        null_logger = logging.getLogger('opengever.nightlyjobs')
        null_logger.addHandler(logging.NullHandler())

        nightly_job_provider = getMultiAdapter(
            (self.portal, self.request, null_logger),
            INightlyJobProvider,
            name='create-dossier-journal-pdf',
        )

        jobs = list(nightly_job_provider)
        if expected:
            self.assertEqual(expected, len(jobs))
            self.assertEqual(expected, len(nightly_job_provider))

        for job in jobs:
            nightly_job_provider.run_job(job, self.interrupt_if_necessary)

    @browsing
    def test_adds_journal_pdf_to_main_dossier_only(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.records_manager, browser)

        subdossier = create(Builder('dossier')
                            .within(self.expired_dossier)
                            .titled(u'Sub'))

        with self.observe_children(self.expired_dossier) as main_children:
            with self.observe_children(subdossier) as sub_children:
                with freeze(datetime(2016, 4, 25)):
                    self.offer(self.expired_dossier, browser)

        # Nothing happened yet, nightly job still pending for main dossier
        self.assertEqual(0, len(main_children['added']))
        self.assertEqual(0, len(sub_children['added']))

        self.assert_create_journal_pdf_jobs_pending(True, [self.expired_dossier])
        self.assert_create_journal_pdf_jobs_pending(False, [subdossier])

        # Now run the nightly jobs
        with self.observe_children(self.expired_dossier) as main_children:
            with self.observe_children(subdossier) as sub_children:
                with freeze(datetime(2016, 4, 25)):
                    self.execute_nightly_jobs(expected=1)

        self.assertEqual(1, len(main_children['added']))
        main_journal_pdf, = main_children['added']
        self.assertEqual(
            u'Journal of dossier Abgeschlossene Vertr\xe4ge, Apr 25, 2016 12:00 AM',
            main_journal_pdf.title)
        self.assertEqual(
            u'Journal of dossier Abgeschlossene Vertraege, Apr 25, 2016 12 00 AM.pdf',
            main_journal_pdf.file.filename)
        self.assertEqual(
            u'application/pdf',
            main_journal_pdf.file.contentType)
        self.assertTrue(IDossierJournalPDFMarker.providedBy(main_journal_pdf))
        self.assertFalse(main_journal_pdf.preserved_as_paper)

        self.assertEqual(
            0, len(sub_children['added']),
            'Journal PDF should only be created for main dossier')

        self.assert_create_journal_pdf_jobs_pending(
            False, [self.expired_dossier, subdossier])

    @browsing
    def test_sets_journal_pdf_document_date_to_dossier_end_date(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.records_manager, browser)

        with self.observe_children(self.expired_dossier) as main_children:
            with freeze(datetime(2016, 4, 25)):
                self.offer(self.expired_dossier, browser)

        # Nothing happened yet, create journal PDF job still pending
        self.assertEqual(0, len(main_children['added']))

        self.assert_create_journal_pdf_jobs_pending(
            True, [self.expired_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.expired_dossier) as main_children:
            with freeze(datetime(2016, 4, 30)):
                self.execute_nightly_jobs(expected=1)

        self.assertEqual(1, len(main_children['added']))
        main_journal_pdf, = main_children['added']
        self.assertTrue(IDossierJournalPDFMarker.providedBy(main_journal_pdf))

        self.assertEqual(
            IDossier(self.expired_dossier).end,
            main_journal_pdf.document_date,
            "Journal PDF date should be dossier end date")

        self.assert_create_journal_pdf_jobs_pending(
            False, [self.expired_dossier])

    @browsing
    def test_journal_pdf_gets_updated_when_dossier_is_offered_again(self, browser):
        self.activate_feature('journal-pdf')
        self.login(self.records_manager, browser)

        with self.observe_children(self.expired_dossier) as children:
            self.offer(self.expired_dossier, browser)

        # Nothing happened yet, journal PDF jobs still pending
        self.assertEqual(0, len(children['added']))

        self.assert_create_journal_pdf_jobs_pending(
            True, [self.expired_dossier])

        # Now run the nightly jobs
        with self.observe_children(self.expired_dossier) as children:
            self.execute_nightly_jobs(expected=1)

        self.assert_create_journal_pdf_jobs_pending(
            False, [self.expired_dossier])

        self.assertEqual(1, len(children['added']))
        journal_pdf, = children['added']
        self.assertEqual(0, journal_pdf.get_current_version_id(missing_as_zero=True))

        # Now retract and offer the dossier again
        self.retract(self.expired_dossier, browser)

        with self.observe_children(self.expired_dossier) as children:
            self.offer(self.expired_dossier, browser)

        # Nothing happened yet, journal PDF jobs still pending
        self.assert_create_journal_pdf_jobs_pending(
            True, [self.expired_dossier])

        # Run nightly jobs again
        with self.observe_children(self.expired_dossier) as children:
            self.execute_nightly_jobs(expected=1)

        # No new PDF has been created, instead the existing one got updated
        self.assertEqual(0, len(children['added']))
        self.assertEqual(1, journal_pdf.get_current_version_id(missing_as_zero=True))

        self.assert_create_journal_pdf_jobs_pending(
            False, [self.expired_dossier])

    @browsing
    def test_journal_pdf_is_disabled_by_default(self, browser):
        self.login(self.records_manager, browser)

        with self.observe_children(self.expired_dossier) as children:
            self.offer(self.expired_dossier, browser)

        self.assertEqual(0, len(children['added']))

        self.assert_create_journal_pdf_jobs_pending(
            False, [self.expired_dossier])
