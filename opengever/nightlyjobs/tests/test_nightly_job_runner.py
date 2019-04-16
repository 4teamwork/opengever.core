from datetime import datetime
from datetime import time
from ftw.testing.freezer import FreezedClock
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.nightlyjobs.interfaces import INightlyJobsSettings
from opengever.nightlyjobs.runner import NightlyJobRunner
from opengever.nightlyjobs.runner import SystemLoadCritical
from opengever.nightlyjobs.runner import TimeWindowExceeded
from opengever.nightlyjobs.tests.test_nightly_job_provider import DocumentTitleModifierJobProvider
from opengever.nightlyjobs.tests.test_nightly_job_provider import IWantToBeModified
from opengever.testing import IntegrationTestCase
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IBrowserRequest
import psutil


@adapter(IPloneSiteRoot, IBrowserRequest)
class DossierTitleModifierJobProvider(DocumentTitleModifierJobProvider):

    portal_type = 'opengever.dossier.businesscasedossier'
    provider_name = 'dossier-title'


@adapter(IPloneSiteRoot, IOpengeverBaseLayer)
class TickingDocumentTitleModifierJobProvider(DocumentTitleModifierJobProvider):

    def initialize(self):
        self.clock = self.request.clock
        super(TickingDocumentTitleModifierJobProvider, self).initialize()

    def post_job_run(self, job):
        self.clock.forward(seconds=3600)
        super(TickingDocumentTitleModifierJobProvider, self).post_job_run(job)


class TestNightlyJobRunner(IntegrationTestCase):

    def setUp(self):
        super(TestNightlyJobRunner, self).setUp()
        self.portal = self.layer['portal']

        self.portal.getSiteManager().registerAdapter(DocumentTitleModifierJobProvider,
                                                     name='document-title')

        with self.login(self.regular_user):
            alsoProvides(self.document, IWantToBeModified)
            self.document.reindexObject(idxs=["object_provides"])

        self.clock = FreezedClock(datetime(2019, 1, 1, 4, 0), None).__enter__()

    def tearDown(self):
        self.clock.__exit__(None, None, None)

    def test_nightly_job_runner_finds_all_registered_providers(self):
        runner = NightlyJobRunner()
        expected = {'document-title': DocumentTitleModifierJobProvider}

        self.assertEqual(expected.keys(), runner.job_providers.keys())
        for name, klass in expected.items():
            self.assertIsInstance(runner.job_providers[name], klass)

        self.portal.getSiteManager().registerAdapter(DossierTitleModifierJobProvider,
                                                     name='dossier-title')
        expected['dossier-title'] = DossierTitleModifierJobProvider
        runner = NightlyJobRunner()

        self.assertEqual(expected.keys(), runner.job_providers.keys())
        for name, klass in expected.items():
            self.assertIsInstance(runner.job_providers[name], klass)

    def test_can_customize_nightly_job_provider(self):
        """ One can customize the JobProviders by registering one with the same
        name but more specific
        """
        self.request.clock = self.clock
        self.portal.getSiteManager().registerAdapter(TickingDocumentTitleModifierJobProvider,
                                                     name='document-title')
        runner = NightlyJobRunner()
        expected = {'document-title': TickingDocumentTitleModifierJobProvider}

        self.assertEqual(expected.keys(), runner.job_providers.keys())
        for name, klass in expected.items():
            self.assertIsInstance(runner.job_providers[name], klass)

    def test_nightly_job_runner_runs_jobs_for_all_providers(self):
        self.portal.getSiteManager().registerAdapter(DossierTitleModifierJobProvider,
                                                     name='dossier-title')
        self.login(self.manager)
        alsoProvides(self.dossier, IWantToBeModified)
        self.dossier.reindexObject(idxs=["object_provides"])

        runner = NightlyJobRunner()
        self.assertEqual(2, runner.njobs_total)
        document_title = self.document.title
        dossier_title = self.dossier.title

        exception = runner.execute_pending_jobs()
        self.assertIsNone(exception)
        self.assertEqual(2, runner.njobs_executed)
        self.assertEqual(u'Modified {}'.format(document_title), self.document.title)
        self.assertEqual(u'Modified {}'.format(dossier_title), self.dossier.title)

    def test_check_in_time_window(self):
        self.login(self.manager)
        runner = NightlyJobRunner()
        self.assertEqual(time(1, 0), runner.window_start)
        self.assertEqual(time(5, 0), runner.window_end)

        # 22:00
        self.clock.backward(seconds=6 * 3600)
        self.assertEqual(time(22, 0), datetime.now().time())
        self.assertFalse(runner.check_in_time_window())

        # 2:00
        self.clock.forward(seconds=4 * 3600)
        self.assertTrue(runner.check_in_time_window())

        # 6:00
        self.clock.forward(seconds=4 * 3600)
        self.assertFalse(runner.check_in_time_window())

    def test_check_in_time_window_handles_midnight_correctly(self):
        self.login(self.manager)
        api.portal.set_registry_record('start_time', time(22, 30),
                                       interface=INightlyJobsSettings)
        runner = NightlyJobRunner()

        # 22:00
        self.clock.backward(seconds=6 * 3600)
        self.assertEqual(time(22, 0), datetime.now().time())
        self.assertFalse(runner.check_in_time_window())

        # 23:00
        self.clock.forward(seconds=3600)
        self.assertTrue(runner.check_in_time_window())

        # 3:00
        self.clock.forward(seconds=4 * 3600)
        self.assertTrue(runner.check_in_time_window())

        # 6:00
        self.clock.forward(seconds=3 * 3600)
        self.assertFalse(runner.check_in_time_window())

    def test_is_cpu_overloaded(self):
        """ Hopefully not flaky
        """
        self.login(self.manager)
        runner = NightlyJobRunner()

        runner.CPU_LIMIT = 120
        self.assertFalse(runner._is_cpu_overladed())

        runner.CPU_LIMIT = - 1
        self.assertTrue(runner._is_cpu_overladed())

    def test_is_memory_full(self):
        """ Hopefully not flaky
        """
        self.login(self.manager)
        runner = NightlyJobRunner()

        runner.MEMORY_LIMIT = 0
        self.assertFalse(runner._is_memory_full())

        runner.MEMORY_LIMIT = 10 * psutil.virtual_memory().total
        self.assertTrue(runner._is_memory_full())

    def test_runner_aborts_when_not_in_time_window(self):
        self.login(self.manager)
        runner = NightlyJobRunner()
        runner.check_in_time_window = lambda: False
        self.assertEqual(1, runner.njobs_total)

        exception = runner.execute_pending_jobs()
        self.assertIsInstance(exception, TimeWindowExceeded)
        self.assertEqual(0, runner.njobs_executed)

    def test_runner_aborts_when_system_overloaded(self):
        self.login(self.manager)
        runner = NightlyJobRunner()
        runner.check_system_overloaded = lambda: True
        self.assertEqual(1, runner.njobs_total)

        exception = runner.execute_pending_jobs()
        self.assertIsInstance(exception, SystemLoadCritical)
        self.assertEqual(0, runner.njobs_executed)

    def test_runner_respects_time_window(self):
        self.login(self.manager)
        self.request.clock = self.clock

        self.portal.getSiteManager().registerAdapter(TickingDocumentTitleModifierJobProvider,
                                                     name='document-title')
        alsoProvides(self.subdocument, IWantToBeModified)
        alsoProvides(self.subsubdocument, IWantToBeModified)
        self.subdocument.reindexObject(idxs=["object_provides"])
        self.subsubdocument.reindexObject(idxs=["object_provides"])

        runner = NightlyJobRunner()
        self.assertEqual(3, runner.njobs_total)
        self.assertEqual(0, runner.njobs_executed)

        exception = runner.execute_pending_jobs()
        self.assertIsInstance(exception, TimeWindowExceeded)
        self.assertEqual(1, runner.njobs_executed)

    def test_timewindowexceeded_early_abort_message(self):
        self.login(self.manager)
        runner = NightlyJobRunner()
        runner.check_in_time_window = lambda: False
        exception = runner.execute_pending_jobs()
        expected_message = "TimeWindowExceeded('Time window exceeded. "\
                           "Window: 01:00-05:00. Current time: 04:00',)\n"\
                           "document-title executed 0 out of 1 jobs"
        self.assertEqual(expected_message,
                         runner.format_early_abort_message(exception))

    def test_systemoverloaded_early_abort_message(self):
        self.login(self.manager)
        runner = NightlyJobRunner()
        runner.check_system_overloaded = lambda: True
        exception = runner.execute_pending_jobs()
        message = runner.format_early_abort_message(exception)
        self.assertIn("SystemLoadCritical('System overloaded.", message)
        self.assertIn("document-title executed 0 out of 1 jobs", message)
