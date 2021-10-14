from BTrees.IIBTree import IITreeSet
from BTrees.OOBTree import OOTreeSet
from opengever.nightlyjobs.maintenance_jobs import FunctionNotFound
from opengever.nightlyjobs.maintenance_jobs import MaintenanceJob
from opengever.nightlyjobs.maintenance_jobs import MaintenanceJobType
from opengever.nightlyjobs.maintenance_jobs import MaintenanceQueuesManager
from opengever.nightlyjobs.maintenance_jobs import NightlyMaintenanceJobsProvider
from opengever.nightlyjobs.maintenance_jobs import QueueAlreadyExistsWithDifferentType
from opengever.nightlyjobs.maintenance_jobs import UnhashableArguments
from opengever.testing import IntegrationTestCase
from plone import api
from unittest import TestCase
from zope.annotation import IAnnotations
import logging


def return_args(variable_argument, **kwargs):
    output = {"variable_argument": variable_argument}
    output.update(kwargs)
    return output


return_args_dotted_name = "opengever.nightlyjobs.tests.test_maintenance_jobs.return_args"


class TestNightlyMaintenanceJobTypes(TestCase):

    def test_job_type_identifier(self):
        job_type = MaintenanceJobType(
            return_args_dotted_name, foo=1, bar="bar")
        self.assertEqual(
            ('opengever.nightlyjobs.tests.test_maintenance_jobs.return_args',
             (('bar', 'bar'), ('foo', 1))),
            job_type.job_type_identifier)

    def test_job_type_representation(self):
        job_type = MaintenanceJobType(
            return_args_dotted_name, foo=1, bar="bar")
        self.assertEqual(
            str(job_type),
            'MaintenanceJobType(return_args, foo=1, bar=bar)')

    def test_can_recreate_job_type_from_identifier(self):
        original = MaintenanceJobType(
            return_args_dotted_name, foo=1, bar="bar")
        recreated = MaintenanceJobType.from_identifier(
            original.job_type_identifier)
        self.assertEqual(original, recreated)

    def test_raises_if_function_dotted_name_cannot_be_resolved(self):
        with self.assertRaises(FunctionNotFound):
            MaintenanceJobType("unresolvable.function.name", foo=1)

    def test_raises_if_arguments_are_not_hashable(self):
        with self.assertRaises(UnhashableArguments):
            MaintenanceJobType(return_args_dotted_name, foo=[1])


class TestNightlyMaintenanceJobs(TestCase):

    def setUp(self):
        super(TestNightlyMaintenanceJobs, self).setUp()
        self.job_type = MaintenanceJobType(
            return_args_dotted_name, foo=1, bar="bar")

    def test_job_representation(self):
        job = MaintenanceJob(self.job_type, 123)
        self.assertEqual('return_args(123, foo=1, bar=bar)',
                         str(job))

    def test_execute_job(self):
        job = MaintenanceJob(self.job_type, 123)
        result = job.execute()
        self.assertEqual(
            result, {"variable_argument": 123, "foo": 1, "bar": "bar"})
        self.assertEqual(
            result, return_args(123, foo=1, bar="bar"))


class TestMaintenanceQueuesManager(IntegrationTestCase):

    def setUp(self):
        super(TestMaintenanceQueuesManager, self).setUp()
        self.queue_manager = MaintenanceQueuesManager(api.portal.get())
        self.job_type = MaintenanceJobType(
            return_args_dotted_name, foo=1, bar="bar")

    def test_queue_key_is_job_type_identifier(self):
        self.assertEqual(self.queue_manager.queue_key_for_job_type(self.job_type),
                         self.job_type.job_type_identifier)

    def test_adding_queue(self):
        self.assertFalse(self.queue_manager.get_queues())
        key, queue = self.queue_manager.add_queue(self.job_type, IITreeSet)
        self.assertIn(self.job_type.job_type_identifier,
                      self.queue_manager.get_queues())
        self.assertEqual(
            self.queue_manager.get_queues(),
            {self.job_type.job_type_identifier: queue})

    def test_adding_invalid_queue_raises(self):
        with self.assertRaises(AssertionError) as exc:
            self.queue_manager.add_queue(self.job_type, list)
        self.assertEqual("Invalid queue type", exc.exception.message)

    def test_adding_already_existing_queue_is_ignored(self):
        self.queue_manager.add_queue(self.job_type, IITreeSet)
        job = MaintenanceJob(self.job_type, 1)
        self.queue_manager.add_job(job)
        self.assertEqual(1, len(self.queue_manager.get_queues()))
        self.assertEqual(1, self.queue_manager.get_jobs_count())

        self.queue_manager.add_queue(self.job_type, IITreeSet)
        self.assertEqual(1, len(self.queue_manager.get_queues()))
        self.assertEqual(1, self.queue_manager.get_jobs_count())

    def test_adding_queue_with_same_key_but_different_type_raises(self):
        self.queue_manager.add_queue(self.job_type, IITreeSet)
        with self.assertRaises(QueueAlreadyExistsWithDifferentType):
            self.queue_manager.add_queue(self.job_type, OOTreeSet)

    def test_only_variable_job_argument_is_stored_in_queue(self):
        self.queue_manager.add_queue(self.job_type, IITreeSet)
        job = MaintenanceJob(self.job_type, 123)
        self.queue_manager.add_job(job)
        queue = self.queue_manager.get_queue(self.job_type)
        self.assertEqual([123], list(queue['queue']))

    def test_returns_jobs_from_all_queues(self):
        job1 = MaintenanceJob(self.job_type, 1)
        job2 = MaintenanceJob(self.job_type, 2)
        self.queue_manager.add_queue(self.job_type, IITreeSet)
        self.queue_manager.add_job(job1)
        self.queue_manager.add_job(job2)

        job_type2 = MaintenanceJobType(
            return_args_dotted_name, foo=2, bar="bar")
        job3 = MaintenanceJob(job_type2, 1)
        self.queue_manager.add_queue(job_type2, IITreeSet)
        self.queue_manager.add_job(job3)

        jobs = list(self.queue_manager.jobs)
        self.assertEqual(3, len(jobs))
        self.assertIn(job1, jobs)
        self.assertIn(job2, jobs)
        self.assertIn(job3, jobs)

    def test_dupplicate_job_is_not_added(self):
        job = MaintenanceJob(self.job_type, 123)
        self.queue_manager.add_queue(self.job_type, IITreeSet)
        self.queue_manager.add_job(job)
        self.assertEqual(1, self.queue_manager.get_jobs_count())

        self.queue_manager.add_job(job)
        self.assertEqual(1, self.queue_manager.get_jobs_count())


class TestNightlyMaintenanceJobsProvider(IntegrationTestCase):

    maxDiff = None

    write_args_dotted_name = "opengever.nightlyjobs.tests.test_maintenance_jobs"\
        ".TestNightlyMaintenanceJobsProvider.write_args_to_portal"

    @staticmethod
    def write_args_to_portal(variable_argument, **kwargs):
        output = {"variable_argument": variable_argument}
        output.update(kwargs)
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        if 'jobs_run' not in annotations:
            annotations['jobs_run'] = []
        annotations['jobs_run'].append(output)

    def execute_nightly_jobs(self):
        nightly_logger = logging.getLogger('opengever.nightlyjobs')

        nightly_job_provider = NightlyMaintenanceJobsProvider(
            self.portal, self.request, nightly_logger)

        jobs = list(nightly_job_provider)

        for job in jobs:
            nightly_job_provider.run_job(job, None)
            nightly_job_provider.maybe_commit(job)

    def test_runs_maintenance_jobs_and_clears_queues(self):
        self.queue_manager = MaintenanceQueuesManager(api.portal.get())
        annotations = IAnnotations(api.portal.get())

        job_type1 = MaintenanceJobType(
            self.write_args_dotted_name, foo=1, bar="bar")
        job_type2 = MaintenanceJobType(
            self.write_args_dotted_name, foo=2, bar="bar")

        job1 = MaintenanceJob(job_type1, 1)
        job2 = MaintenanceJob(job_type1, 2)
        self.queue_manager.add_queue(job_type1, IITreeSet)
        self.queue_manager.add_job(job1)
        self.queue_manager.add_job(job2)

        job3 = MaintenanceJob(job_type2, 1)
        self.queue_manager.add_queue(job_type2, IITreeSet)
        self.queue_manager.add_job(job3)

        self.assertEqual(2, len(list(self.queue_manager.get_queues())))
        self.assertEqual(3, len(list(self.queue_manager.jobs)))
        self.assertNotIn('jobs_run', annotations)

        self.execute_nightly_jobs()
        self.assertEqual(0, len(list(self.queue_manager.jobs)))
        self.assertEqual(0, len(list(self.queue_manager.get_queues())))
        self.assertIn('jobs_run', annotations)
        self.assertEqual([{'variable_argument': 1, 'bar': 'bar', 'foo': 1},
                          {'variable_argument': 2, 'bar': 'bar', 'foo': 1},
                          {'variable_argument': 1, 'bar': 'bar', 'foo': 2}],
                         annotations['jobs_run'])
