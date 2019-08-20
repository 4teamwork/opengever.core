from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.delivery import STATUS_SCHEDULED
from opengever.disposition.delivery import STATUS_SUCCESS
from opengever.disposition.nightly_jobs import NightlySIPDelivery
from opengever.disposition.tests.test_delivery import TestFilesystemTransportBase
from opengever.testing.helpers import CapturingLogHandler
from os.path import join as pjoin
import logging
import os


class TestNightlyDelivery(TestFilesystemTransportBase):

    features = ('nightly-jobs', )

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
