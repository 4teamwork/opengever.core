from datetime import datetime
from datetime import time
from datetime import timedelta
from ftw.testing.freezer import FreezedClock
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.nightlyjobs.interfaces import INightlyJobsSettings
from opengever.nightlyjobs.runner import get_job_counts
from opengever.nightlyjobs.runner import get_nightly_run_timestamp
from opengever.nightlyjobs.runner import nightly_run_within_24h
from opengever.nightlyjobs.runner import SystemLoadCritical
from opengever.nightlyjobs.runner import TimeWindowExceeded
from opengever.nightlyjobs.testing import TestingNightlyJobRunner
from opengever.nightlyjobs.tests.test_nightly_job_provider import DocumentTitleModifierJobProvider
from opengever.nightlyjobs.tests.test_nightly_job_provider import IWantToBeModified
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.uuid.utils import uuidToObject
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IBrowserRequest
import logging


@adapter(IPloneSiteRoot, IBrowserRequest, logging.Logger)
class DossierTitleModifierJobProvider(DocumentTitleModifierJobProvider):

    portal_type = 'opengever.dossier.businesscasedossier'
    provider_name = 'dossier-title'


@adapter(IPloneSiteRoot, IOpengeverBaseLayer, logging.Logger)
class TickingDocumentTitleModifierJobProvider(DocumentTitleModifierJobProvider):

    def __init__(self, context, request, logger):
        super(TickingDocumentTitleModifierJobProvider, self).__init__(
            context, request, logger)
        self.clock = self.request.clock

    def run_job(self, job, interrupt_if_necessary):
        super(TickingDocumentTitleModifierJobProvider, self).run_job(job, interrupt_if_necessary)
        self.clock.forward(seconds=3600)


@adapter(IPloneSiteRoot, IOpengeverBaseLayer, logging.Logger)
class RaisingDocumentTitleModifierJobProvider(DocumentTitleModifierJobProvider):

    counter = 0

    def execute_job(self, job, interrupt_if_necessary):
        interrupt_if_necessary()
        self.counter += 1
        if self.counter % 2 == 1:
            raise AttributeError()
        obj = uuidToObject(job['uid'])
        obj.title = u'Modified {}'.format(obj.title)


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

    def get_load_controlled_runner(self,
                                   virtual_memory_available=200 * 1024 * 1024,
                                   virtual_memory_percent=50,
                                   force_execution=False):
        """ get a runner with controlled system load
        """
        runner = TestingNightlyJobRunner(force_execution=force_execution)

        def get_system_load():
            return {'virtual_memory_available': virtual_memory_available,
                    'virtual_memory_percent': virtual_memory_percent}

        runner.get_system_load = get_system_load
        return runner

    def test_nightly_job_runner_finds_all_registered_providers(self):
        runner = TestingNightlyJobRunner()
        expected = {'document-title': DocumentTitleModifierJobProvider}

        self.assertEqual(expected.keys(), runner.job_providers.keys())
        for name, klass in expected.items():
            self.assertIsInstance(runner.job_providers[name], klass)

        self.portal.getSiteManager().registerAdapter(DossierTitleModifierJobProvider,
                                                     name='dossier-title')
        expected['dossier-title'] = DossierTitleModifierJobProvider
        runner = TestingNightlyJobRunner()

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
        runner = TestingNightlyJobRunner()
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
        runner = TestingNightlyJobRunner()

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

    def test_is_memory_full(self):
        self.login(self.manager)
        runner = TestingNightlyJobRunner()

        memory_limit = runner.LOAD_LIMITS['virtual_memory_available']
        load = {'virtual_memory_percent': 50}
        load['virtual_memory_available'] = memory_limit + 1
        self.assertFalse(runner._is_memory_full(load))

        load['virtual_memory_available'] = memory_limit - 1
        self.assertTrue(runner._is_memory_full(load))

    def test_runner_aborts_when_not_in_time_window(self):
        self.login(self.manager)
        runner = TestingNightlyJobRunner()
        runner.check_in_time_window = lambda now: False
        self.assertEqual(1, runner.get_initial_jobs_count())

        exception = runner.execute_pending_jobs(early_check=False)
        self.assertIsInstance(exception, TimeWindowExceeded)
        self.assertEqual(0, runner.get_executed_jobs_count())

    def test_runner_aborts_immediately_when_not_in_time_window(self):
        # Runner should not even bother collecting jobs when invoked at
        # the wrong time, and raise an exception that is not caught
        self.login(self.manager)
        runner = TestingNightlyJobRunner()
        runner.check_in_time_window = lambda now: False

        with self.assertRaises(TimeWindowExceeded):
            runner.execute_pending_jobs()

    def test_runner_ignores_time_window_when_force_execution_true(self):
        # When force_execution is set to True, the runner should not
        # abort even when outside the time window
        self.login(self.manager)
        runner = TestingNightlyJobRunner(force_execution=True)
        runner.check_in_time_window = lambda now: False

        runner.execute_pending_jobs()

    def test_runner_aborts_when_available_memory_too_low(self):
        self.login(self.manager)
        runner = self.get_load_controlled_runner(virtual_memory_available=0)
        self.assertEqual(1, runner.get_initial_jobs_count())

        exception = runner.execute_pending_jobs(early_check=False)
        self.assertIsInstance(exception, SystemLoadCritical)
        self.assertEqual(0, runner.get_executed_jobs_count())

    def test_runner_aborts_immediately_when_available_memory_too_low(self):
        # Runner should not even bother collecting jobs when invoked
        # during times of high system load, and raise an exception
        self.login(self.manager)
        runner = self.get_load_controlled_runner(virtual_memory_available=0)

        with self.assertRaises(SystemLoadCritical):
            runner.execute_pending_jobs()

    def test_runner_ignores_memory_too_low_when_force_execution_true(self):
        # When force_execution is set to True, the runner should not
        # abort even when available memory is too low
        self.login(self.manager)
        runner = self.get_load_controlled_runner(virtual_memory_available=0,
                                                 force_execution=True)
        runner.execute_pending_jobs()

    def test_runner_aborts_when_percent_memory_too_high(self):
        self.login(self.manager)
        runner = self.get_load_controlled_runner(virtual_memory_percent=100)
        self.assertEqual(1, runner.get_initial_jobs_count())

        exception = runner.execute_pending_jobs(early_check=False)
        self.assertIsInstance(exception, SystemLoadCritical)
        self.assertEqual(0, runner.get_executed_jobs_count())

    def test_runner_ignores_percent_memory_when_force_execution_true(self):
        # When force_execution is set to True, the runner should not
        # abort even when percent virtual memory is too high
        self.login(self.manager)
        runner = self.get_load_controlled_runner(virtual_memory_percent=100,
                                                 force_execution=True)
        runner.execute_pending_jobs()

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

        # One job gets executed at 4:00 and one just on the window
        # edge at 5:00, then it raises TimeWindowExceeded
        exception = runner.execute_pending_jobs()
        self.assertIsInstance(exception, TimeWindowExceeded)
        self.assertEqual(2, runner.get_executed_jobs_count())

    def test_timewindowexceeded_early_abort_message(self):
        self.login(self.manager)
        runner = self.get_load_controlled_runner()
        runner.check_in_time_window = lambda now: False
        exception = runner.execute_pending_jobs(early_check=False)
        expected_message = "TimeWindowExceeded('Time window exceeded. "\
                           "Window: 1:00:00-5:00:00. Current time: 04:00',)\n"\
                           "document-title executed 0 out of 1 jobs"
        self.assertEqual(expected_message,
                         runner.format_early_abort_message(exception))

    def test_systemoverloaded_early_abort_message(self):
        self.login(self.manager)
        runner = self.get_load_controlled_runner()
        runner.check_system_overloaded = lambda load: True
        exception = runner.execute_pending_jobs(early_check=False)
        expected_message = "SystemLoadCritical('System overloaded.\\n"\
                           "Available memory: 200MB; limit: 100MB\\n"\
                           "Percent memory: 50; limit: 95',)\n"\
                           "document-title executed 0 out of 1 jobs"
        self.assertEqual(expected_message,
                         runner.format_early_abort_message(exception))

    def test_runner_continues_when_exception_is_raised(self):
        self.portal.getSiteManager().registerAdapter(RaisingDocumentTitleModifierJobProvider,
                                                     name='document-title')
        with self.login(self.regular_user):
            alsoProvides(self.empty_document, IWantToBeModified)
            alsoProvides(self.subdocument, IWantToBeModified)
            alsoProvides(self.subsubdocument, IWantToBeModified)
            self.empty_document.reindexObject(idxs=["object_provides"])
            self.subdocument.reindexObject(idxs=["object_provides"])
            self.subsubdocument.reindexObject(idxs=["object_provides"])
        self.login(self.manager)
        runner = self.get_load_controlled_runner()
        self.assertEqual(4, runner.get_initial_jobs_count())

        runner.execute_pending_jobs(early_check=False)
        self.assertEqual(2, runner.get_executed_jobs_count())
        self.assertEqual(2, runner.get_remaining_jobs_count())

    def test_nightly_job_runner_updates_last_run_timestamp(self):
        self.login(self.manager)

        runner = self.get_load_controlled_runner()
        exception = runner.execute_pending_jobs()

        self.assertIsNone(exception)

        timestamp = IAnnotations(self.portal).get('last_nightly_run')
        self.assertEqual(datetime(2019, 1, 1, 4, 0), timestamp)

    def test_get_nightly_run_timestamp(self):
        self.login(self.manager)

        ann = IAnnotations(self.portal)

        self.assertIsNone(get_nightly_run_timestamp())

        ann['last_nightly_run'] = datetime(2021, 5, 17, 12, 45)
        self.assertEqual(
            datetime(2021, 5, 17, 12, 45), get_nightly_run_timestamp())

    def test_nightly_run_within_24h_helper(self):
        self.login(self.manager)

        ann = IAnnotations(self.portal)

        ann['last_nightly_run'] = datetime.now() - timedelta(hours=23)
        self.assertTrue(nightly_run_within_24h())

        # Margin of error (24h + 4h + 1h)
        ann['last_nightly_run'] = datetime.now() - timedelta(hours=28)
        self.assertTrue(nightly_run_within_24h())

        ann['last_nightly_run'] = datetime.now() - timedelta(hours=30)
        self.assertFalse(nightly_run_within_24h())

        ann['last_nightly_run'] = None
        self.assertFalse(nightly_run_within_24h())

        ann.pop('last_nightly_run')
        self.assertFalse(nightly_run_within_24h())

    def test_get_job_counts(self):
        self.login(self.manager)

        expected = {
            u'create-dossier-journal-pdf': 0,
            u'deliver-sip-packages': 0,
            u'document-title': 1,
            u'execute-after-resolve-jobs': 0,
            u'maintenance-jobs': 0,
            u'update-disposition-permissions': 2
        }

        self.assertEqual(expected, get_job_counts())

        self.portal.getSiteManager().registerAdapter(
            DossierTitleModifierJobProvider, name='dossier-title')

        alsoProvides(self.dossier, IWantToBeModified)
        self.dossier.reindexObject(idxs=["object_provides"])

        expected['dossier-title'] = 1
        self.assertEqual(expected, get_job_counts())
