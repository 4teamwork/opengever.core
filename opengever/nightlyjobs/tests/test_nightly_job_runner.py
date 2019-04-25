from datetime import datetime
from datetime import time
from datetime import timedelta
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


@adapter(IPloneSiteRoot, IBrowserRequest)
class DossierTitleModifierJobProvider(DocumentTitleModifierJobProvider):

    portal_type = 'opengever.dossier.businesscasedossier'
    provider_name = 'dossier-title'


@adapter(IPloneSiteRoot, IOpengeverBaseLayer)
class TickingDocumentTitleModifierJobProvider(DocumentTitleModifierJobProvider):

    def __init__(self, context, request):
        super(TickingDocumentTitleModifierJobProvider, self).__init__(context, request)
        self.clock = self.request.clock

    def run_job(self, job, interrupt_if_necessary):
        super(TickingDocumentTitleModifierJobProvider, self).run_job(job, interrupt_if_necessary)
        self.clock.forward(seconds=3600)


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

    def get_load_controlled_runner(self, cpu_percent=50,
                                   virtual_memory_available=200 * 1024 * 1024):
        """ get a runner with controlled system load
        """
        runner = NightlyJobRunner()

        def get_system_load():
            return {'cpu_percent': cpu_percent,
                    'virtual_memory_available': virtual_memory_available}

        runner.get_system_load = get_system_load
        return runner

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

        runner = self.get_load_controlled_runner()
        self.assertEqual(2, runner.get_initial_jobs_count())
        document_title = self.document.title
        dossier_title = self.dossier.title

        exception = runner.execute_pending_jobs()
        self.assertIsNone(exception)
        self.assertEqual(2, runner.get_executed_jobs_count())
        self.assertEqual(u'Modified {}'.format(document_title), self.document.title)
        self.assertEqual(u'Modified {}'.format(dossier_title), self.dossier.title)

    def test_check_in_time_window(self):
        self.login(self.manager)
        runner = self.get_load_controlled_runner()
        self.assertEqual(timedelta(hours=1), runner.window_start)
        self.assertEqual(timedelta(hours=5), runner.window_end)

        # 22:00
        self.clock.backward(seconds=6 * 3600)
        self.assertEqual(time(22, 0), datetime.now().time())
        self.assertFalse(runner.check_in_time_window(datetime.now().time()))

        # 2:00
        self.clock.forward(seconds=4 * 3600)
        self.assertTrue(runner.check_in_time_window(datetime.now().time()))

        # 6:00
        self.clock.forward(seconds=4 * 3600)
        self.assertFalse(runner.check_in_time_window(datetime.now().time()))

    def test_check_in_time_window_handles_midnight_correctly(self):
        self.login(self.manager)
        api.portal.set_registry_record('start_time', timedelta(hours=22, minutes=30),
                                       interface=INightlyJobsSettings)
        api.portal.set_registry_record('end_time', timedelta(hours=29),
                                       interface=INightlyJobsSettings)
        runner = NightlyJobRunner()

        # 22:00
        self.clock.backward(seconds=6 * 3600)
        self.assertEqual(time(22, 0), datetime.now().time())
        self.assertFalse(runner.check_in_time_window(datetime.now().time()))

        # 23:00
        self.clock.forward(seconds=3600)
        self.assertTrue(runner.check_in_time_window(datetime.now().time()))

        # 3:00
        self.clock.forward(seconds=4 * 3600)
        self.assertTrue(runner.check_in_time_window(datetime.now().time()))

        # 6:00
        self.clock.forward(seconds=3 * 3600)
        self.assertFalse(runner.check_in_time_window(datetime.now().time()))

    def test_is_cpu_overloaded(self):
        self.login(self.manager)
        runner = NightlyJobRunner()

        cpu_percent_limit = runner.LOAD_LIMITS['cpu_percent']
        load = {'cpu_percent': cpu_percent_limit - 1}
        self.assertFalse(runner._is_cpu_overladed(load))

        load = {'cpu_percent': cpu_percent_limit + 1}
        self.assertTrue(runner._is_cpu_overladed(load))

    def test_is_memory_full(self):
        self.login(self.manager)
        runner = NightlyJobRunner()

        memory_limit = runner.LOAD_LIMITS['virtual_memory_available']
        load = {'virtual_memory_available': memory_limit + 1}
        self.assertFalse(runner._is_memory_full(load))

        load = {'virtual_memory_available': memory_limit - 1}
        self.assertTrue(runner._is_memory_full(load))

    def test_runner_aborts_when_not_in_time_window(self):
        self.login(self.manager)
        runner = NightlyJobRunner()
        runner.check_in_time_window = lambda now: False
        self.assertEqual(1, runner.get_initial_jobs_count())

        exception = runner.execute_pending_jobs()
        self.assertIsInstance(exception, TimeWindowExceeded)
        self.assertEqual(0, runner.get_executed_jobs_count())

    def test_runner_aborts_when_system_overloaded(self):
        self.login(self.manager)
        runner = self.get_load_controlled_runner(cpu_percent=100)
        self.assertEqual(1, runner.get_initial_jobs_count())

        exception = runner.execute_pending_jobs()
        self.assertIsInstance(exception, SystemLoadCritical)
        self.assertEqual(0, runner.get_executed_jobs_count())

    def test_runner_respects_time_window(self):
        self.login(self.manager)
        self.request.clock = self.clock

        self.portal.getSiteManager().registerAdapter(TickingDocumentTitleModifierJobProvider,
                                                     name='document-title')
        alsoProvides(self.subdocument, IWantToBeModified)
        alsoProvides(self.subsubdocument, IWantToBeModified)
        self.subdocument.reindexObject(idxs=["object_provides"])
        self.subsubdocument.reindexObject(idxs=["object_provides"])

        runner = self.get_load_controlled_runner()
        self.assertEqual(3, runner.get_initial_jobs_count())
        self.assertEqual(0, runner.get_executed_jobs_count())

        exception = runner.execute_pending_jobs()
        self.assertIsInstance(exception, TimeWindowExceeded)
        self.assertEqual(1, runner.get_executed_jobs_count())

    def test_timewindowexceeded_early_abort_message(self):
        self.login(self.manager)
        runner = self.get_load_controlled_runner()
        runner.check_in_time_window = lambda now: False
        exception = runner.execute_pending_jobs()
        expected_message = "TimeWindowExceeded('Time window exceeded. "\
                           "Window: 1:00:00-5:00:00. Current time: 04:00',)\n"\
                           "document-title executed 0 out of 1 jobs"
        self.assertEqual(expected_message,
                         runner.format_early_abort_message(exception))

    def test_systemoverloaded_early_abort_message(self):
        self.login(self.manager)
        runner = self.get_load_controlled_runner()
        runner.check_system_overloaded = lambda load: True
        exception = runner.execute_pending_jobs()
        expected_message = "SystemLoadCritical('System overloaded.\\n"\
                           "CPU load: 50; limit: 95\\n"\
                           "Available memory: 200MB; limit: 100MB',)\n"\
                           "document-title executed 0 out of 1 jobs"
        self.assertEqual(expected_message,
                         runner.format_early_abort_message(exception))
