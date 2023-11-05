from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import ASSIGNMENT_VIA_DISPOSITION
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.delivery import STATUS_SCHEDULED
from opengever.disposition.delivery import STATUS_SUCCESS
from opengever.disposition.nightly_jobs import NightlyDossierJournalPDF
from opengever.disposition.nightly_jobs import NightlyDossierPermissionSetter
from opengever.disposition.nightly_jobs import NightlySIPDelivery
from opengever.disposition.tests.test_delivery import TestFilesystemTransportBase
from opengever.ogds.auth.testing import DisabledUserPlugins
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import CapturingLogHandler
from os.path import join as pjoin
from plone import api
import logging
import os


class TestNightlyDelivery(TestFilesystemTransportBase):

    def setUp(self):
        super(TestNightlyDelivery, self).setUp()
        with self.login(self.records_manager):
            self.sip_filename = self.disposition_with_sip.get_sip_filename()
            self.dst_path = pjoin(self.tempdir, self.sip_filename)

    def interrupt_if_necessary(self):
        """Stub out the runner's `interrupt_if_necessary` function.
        """

    def execute_nightly_jobs(self, expected=None, logger=None):
        if not logger:
            logger = logging.getLogger('opengever.nightlyjobs')
            logger.addHandler(logging.NullHandler())

        nightly_job_provider = NightlySIPDelivery(
            self.portal, self.request, logger)

        jobs = list(nightly_job_provider)
        if expected:
            self.assertEqual(expected, len(jobs))
            self.assertEqual(expected, len(nightly_job_provider))

        for job in jobs:
            nightly_job_provider.run_job(job, self.interrupt_if_necessary)

    def test_nightly_sip_delivery(self):
        self.login(self.records_manager)

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        statuses = scheduler.get_statuses()

        self.assertEqual({u'filesystem': STATUS_SCHEDULED}, statuses)
        self.execute_nightly_jobs(expected=1)
        self.assertEqual({u'filesystem': STATUS_SUCCESS}, statuses)

        self.assertEqual([self.sip_filename], os.listdir(self.tempdir))

    def test_transport_logging_propagates_up_to_nightly_log_handler(self):
        self.login(self.records_manager)

        # Create a logging setup similar to cronjob scenario
        nightly_logger = logging.getLogger('opengever.nightlyjobs')
        nightly_logger.setLevel(logging.INFO)
        nightly_log_handler = CapturingLogHandler()
        nightly_logger.addHandler(nightly_log_handler)

        self.execute_nightly_jobs(expected=1, logger=nightly_logger)

        logrecords = [(r.name, r.msg) for r in nightly_log_handler.records]

        expected = [
            ('opengever.nightlyjobs',
                "Delivering SIP for %r" % self.disposition_with_sip),

            ('opengever.disposition.delivery',
                "Delivering using transport 'filesystem'"),

            ('FilesystemTransport',
                "Transported %r to %r" % (self.sip_filename, self.dst_path)),

            ('opengever.disposition.delivery',
                "Successful delivery using transport 'filesystem'"),

            ('opengever.disposition.delivery',
                "Skip: Transport 'ftps' is disabled"),
        ]

        self.assertEqual(expected, logrecords,
                         "Expected log messages from DeliveryScheduler and "
                         "Transport to also show up in nightly logs")


class TestNightlyDossierJournalPDF(IntegrationTestCase):

    def setUp(self):
        super(TestNightlyDossierJournalPDF, self).setUp()
        logger = logging.getLogger('opengever.nightlyjobs')
        logger.addHandler(logging.NullHandler())

        self.nightly_job_provider = NightlyDossierJournalPDF(
            self.portal, self.request, logger)

    def interrupt_if_necessary(self):
        """Stub out the runner's `interrupt_if_necessary` function.
        """

    def execute_nightly_jobs(self, expected=None):
        jobs = list(self.nightly_job_provider)
        if expected:
            self.assertEqual(expected, len(jobs))
            self.assertEqual(expected, len(self.nightly_job_provider))

        for job in jobs:
            self.nightly_job_provider.run_job(job, self.interrupt_if_necessary)

    def test_creates_dossier_journal_pdf(self):
        self.login(self.regular_user)

        nightly_job_provider = NightlyDossierJournalPDF(
            self.portal, self.request, None)

        nightly_job_provider.queue_journal_pdf_job(self.empty_dossier)
        with self.observe_children(self.empty_dossier) as children, freeze(datetime(2016, 4, 25)):
            self.execute_nightly_jobs(1)

        self.assertEqual(0, len(self.nightly_job_provider))
        self.assertEqual(1, len(children['added']))
        journal_pdf = children['added'].pop()
        self.assertEqual(
            u'Journal of dossier An empty dossier, Apr 25, 2016 12:00 AM',
            journal_pdf.title)

    def test_handles_deleted_dossier(self):
        self.login(self.regular_user)

        nightly_job_provider = NightlyDossierJournalPDF(
            self.portal, self.request, None)

        nightly_job_provider.queue_journal_pdf_job(self.empty_dossier)

        with self.login(self.manager):
            api.content.delete(self.empty_dossier)

        self.execute_nightly_jobs(1)

        self.assertEqual(0, len(self.nightly_job_provider))


class TestNightlyDossierPermissionSetter(IntegrationTestCase):

    def setUp(self):
        # XXX: Move this onto the layer once remaining tests are fixed.

        # Disable userEnumeration for source_users to avoid MultiplePrincipalError.
        self.disabled_source_users = DisabledUserPlugins(self.layer['portal'].acl_users)
        self.disabled_source_users.__enter__()
        super(TestNightlyDossierPermissionSetter, self).setUp()

    def tearDown(self):
        super(TestNightlyDossierPermissionSetter, self).tearDown()
        self.disabled_source_users.__exit__(None, None, None)

    def interrupt_if_necessary(self):
        """Stub out the runner's `interrupt_if_necessary` function.
        """

    def execute_nightly_jobs(self, expected=None, logger=None):
        if not logger:
            logger = logging.getLogger('opengever.nightlyjobs')
            logger.addHandler(logging.NullHandler())

        nightly_job_provider = NightlyDossierPermissionSetter(
            self.portal, self.request, logger)

        jobs = list(nightly_job_provider)
        if expected:
            self.assertEqual(expected, len(jobs))
            self.assertEqual(expected, len(nightly_job_provider))

        for job in jobs:
            nightly_job_provider.run_job(job, self.interrupt_if_necessary)

    def get_assignments_via_disposition(self, obj):
        manager = RoleAssignmentManager(obj)
        return manager.get_assignments_by_cause(ASSIGNMENT_VIA_DISPOSITION)

    def test_sets_permissions_for_dossiers_with_missing_permissions(self):
        self.login(self.records_manager)
        self.disposition_with_sip.dossiers_with_missing_permissions = []

        self.assertTrue(self.disposition.has_dossiers_with_pending_permissions_changes)
        self.assertItemsEqual(
            [self.offered_dossier_to_archive.UID(),
             self.offered_dossier_to_destroy.UID()],
            self.disposition.dossiers_with_missing_permissions)
        self.assertEqual([], self.disposition.dossiers_with_extra_permissions)

        self.assertEqual(
            [], self.get_assignments_via_disposition(self.offered_dossier_to_archive))
        self.assertEqual(
            [], self.get_assignments_via_disposition(self.offered_dossier_to_destroy))

        self.execute_nightly_jobs(expected=1)

        self.assertFalse(self.disposition.has_dossiers_with_pending_permissions_changes)

        assignments = self.get_assignments_via_disposition(self.offered_dossier_to_archive)
        self.assertEqual(1, len(assignments))
        self.assertEqual(
            {'cause': 7,
             'roles': ['Reader'],
             'reference': Oguid.for_object(self.disposition).id,
             'principal': 'jurgen.fischer'},
            assignments[0])

        assignments = self.get_assignments_via_disposition(self.offered_dossier_to_destroy)
        self.assertEqual(1, len(assignments))
        self.assertEqual(
            {'cause': 7,
             'roles': ['Reader'],
             'reference': Oguid.for_object(self.disposition).id,
             'principal': 'jurgen.fischer'},
            assignments[0])

        self.execute_nightly_jobs(expected=0)

    def test_removes_permissions_for_dossiers_with_extra_permissions(self):
        self.login(self.records_manager)
        self.disposition_with_sip.dossiers_with_missing_permissions = []
        self.execute_nightly_jobs()

        archive_manager = RoleAssignmentManager(self.offered_dossier_to_archive)
        destroy_manager = RoleAssignmentManager(self.offered_dossier_to_destroy)

        self.assertEqual(
            1, len(self.get_assignments_via_disposition(self.offered_dossier_to_archive)))
        self.assertEqual(
            1, len(self.get_assignments_via_disposition(self.offered_dossier_to_destroy)))

        self.assertFalse(self.disposition.has_dossiers_with_pending_permissions_changes)
        self.disposition.dossiers = [el for el in self.disposition.dossiers
                                     if el.to_object != self.offered_dossier_to_archive]
        self.assertTrue(self.disposition.has_dossiers_with_pending_permissions_changes)

        self.execute_nightly_jobs(expected=1)
        self.assertEqual(
            0, len(self.get_assignments_via_disposition(self.offered_dossier_to_archive)))
        self.assertEqual(
            1, len(self.get_assignments_via_disposition(self.offered_dossier_to_destroy)))

    def test_handles_subdossiers_with_blocked_role_inheritance(self):
        self.login(self.records_manager)
        self.disposition_with_sip.dossiers_with_missing_permissions = []

        protected_subdossier = create(Builder('dossier').within(self.offered_dossier_to_archive))
        protected_subdossier.__ac_local_roles_block__ = True
        protected_subdossier.reindexObject()
        unprotected_subdossier = create(Builder('dossier').within(self.offered_dossier_to_archive))
        protected_subsubdossier = create(Builder('dossier').within(unprotected_subdossier))
        protected_subsubdossier.__ac_local_roles_block__ = True
        protected_subsubdossier.reindexObject()

        self.assertEqual(
            0, len(self.get_assignments_via_disposition(self.offered_dossier_to_archive)))
        self.assertEqual(
            0, len(self.get_assignments_via_disposition(protected_subdossier)))
        self.assertEqual(
            0, len(self.get_assignments_via_disposition(unprotected_subdossier)))
        self.assertEqual(
            0, len(self.get_assignments_via_disposition(protected_subsubdossier)))

        self.execute_nightly_jobs(expected=1)
        self.assertEqual(
            1, len(self.get_assignments_via_disposition(self.offered_dossier_to_archive)))
        self.assertEqual(
            1, len(self.get_assignments_via_disposition(protected_subdossier)))
        self.assertEqual(
            0, len(self.get_assignments_via_disposition(unprotected_subdossier)))
        self.assertEqual(
            1, len(self.get_assignments_via_disposition(protected_subsubdossier)))

        protected_subsubdossier.__ac_local_roles_block__ = False
        protected_subsubdossier.reindexObject()
        self.disposition.dossiers = [el for el in self.disposition.dossiers
                                     if el.to_object != self.offered_dossier_to_archive]
        self.execute_nightly_jobs(expected=1)
        self.assertEqual(
            0, len(self.get_assignments_via_disposition(self.offered_dossier_to_archive)))
        self.assertEqual(
            0, len(self.get_assignments_via_disposition(protected_subdossier)))
        self.assertEqual(
            0, len(self.get_assignments_via_disposition(unprotected_subdossier)))
        self.assertEqual(
            0, len(self.get_assignments_via_disposition(protected_subsubdossier)))
