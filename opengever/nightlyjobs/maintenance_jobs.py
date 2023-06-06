"""
This module provides a very flexible way to perform maintenance tasks overnight.
A MaintenanceJob allows to execute any function with any number of arguments.
Such MaintenanceJobs will get added to queues using the MaintenanceQueuesManager
and run overnight by the NightlyMaintenanceJobsProvider. MaintenanceJobs are
grouped by MaintenanceJobType in the queues (one queue per type) for efficiency.
"""

from BTrees.IIBTree import IITreeSet
from BTrees.OOBTree import OOTreeSet
from collections import Counter
from ftw.solr.interfaces import ISolrConnectionManager
from opengever.nightlyjobs.provider import NightlyJobProviderBase
from persistent.dict import PersistentDict
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.dottedname.resolve import resolve
import transaction


NIGHTLY_MAINTENANCE_JOB_QUEUES_KEY = 'NIGHTLY_MAINTENANCE_JOB_QUEUES'


class QueueAlreadyExistsWithDifferentType(Exception):
    """Raised when trying to add a queue with a key that already exists but
    a different type."""


class QueueIsMissing(Exception):
    """Raised when trying to add a job to a queue which does not exist"""


class JobIsMissing(Exception):
    """Raised when trying to remove a job not found in the queue"""


class FunctionNotFound(Exception):
    """Raised when the function of a maintenance job cannot be found"""


class UnhashableArguments(Exception):
    """Raised when the fixed_arguments are not hashable"""


class MaintenanceJobType(object):
    """A maintenance job type is composed of a function and a set of arguments
    (fixed_arguments).

    An instance of MaintenanceJobType is fully determined by its
    job_type_identifier which contains the fixed_arguments and the function's
    dotted name.

    The class contains a constructor from_identifier allowing to reconstruct a
    MaintenanceJobType from a job_type_identifier.
    """

    def __init__(self, function_dotted_name, **fixed_arguments):
        self.function_dotted_name = function_dotted_name
        self.fixed_arguments = fixed_arguments

        try:
            self.function = resolve(self.function_dotted_name)
        except ImportError:
            raise FunctionNotFound()

        try:
            hash(self.job_type_identifier)
        except TypeError:
            raise UnhashableArguments()

    def __eq__(self, other):
        return (self.function_dotted_name == other.function_dotted_name
                and self.fixed_arguments == other.fixed_arguments)

    def __repr__(self):
        return u'{}({}, {})'.format(
            self.__class__.__name__,
            self.function_name,
            ", ".join(["{}={}".format(name, value) for name, value in
                       self.fixed_arguments.items()]))

    @property
    def function_name(self):
        return self.function_dotted_name.rsplit(".", 1)[-1]

    @property
    def job_type_identifier(self):
        return (self.function_dotted_name,
                tuple(sorted(self.fixed_arguments.items())))

    @classmethod
    def from_identifier(cls, job_type_identifier):
        function_dotted_name, fixed_args_tuple = job_type_identifier
        fixed_arguments = dict(fixed_args_tuple)
        return cls(function_dotted_name, **fixed_arguments)


class MaintenanceJob(object):
    """A maintenance job is composed of a job_type (MaintenanceJobType) and
    a variable_argument, so that MaintenanceJobs of the same type only differ
    by their variable_argument. This allows for more efficient storage when
    adding many MaintenanceJobs with the same job_type, as the job_type needs
    to be saved only once and an associated queue can simply store the value of
    the variable_argument for each MaintenanceJob (see MaintenanceQueuesManager)
    """
    def __init__(self, job_type, variable_argument):
        self.job_type = job_type
        self.variable_argument = variable_argument

    def __repr__(self):
        return u'{}({}, {})'.format(
            self.function.__name__,
            self.variable_argument,
            ", ".join(["{}={}".format(name, value) for name, value in
                       self.fixed_arguments.items()]))

    def __eq__(self, other):
        return (self.job_type == other.job_type
                and self.variable_argument == other.variable_argument)

    @property
    def function(self):
        return self.job_type.function

    @property
    def fixed_arguments(self):
        return self.job_type.fixed_arguments

    def execute(self):
        return self.function(self.variable_argument, **self.fixed_arguments)


class MaintenanceQueuesManager(object):
    """Queues for MaintenanceJobs are stored in the annotations on the plone
    site root. We make one queue per job type, corresponding to a function and
    a set of fixed arguments, so that only the variable argument of the job
    needs to be stored in the actual queue (e.g. the object's IntId).

    A queue should be a TreeSet, for example an IITreeSet to store IntIds.

    For each queue, i.e. for each job type, we also store a commit_batch_size,
    i.e. the number of jobs of that type which should be run
    between commits, as well as the commit_to_solr flag which indicates
    whether we need to specifically commit to solr in addition to normal
    calls to transaction.commit. This is typically necessary when indexing only
    in solr directly using the solr index handlers.
    """
    supported_queue_types = (IITreeSet, OOTreeSet)

    def __init__(self, context):
        self.context = context

    def add_queue(self, job_type, queue_type=IITreeSet,
                  commit_batch_size=1000, commit_to_solr=False):
        self.assert_queue_type_is_valid(queue_type)
        ann = IAnnotations(self.context)
        if NIGHTLY_MAINTENANCE_JOB_QUEUES_KEY not in ann:
            ann[NIGHTLY_MAINTENANCE_JOB_QUEUES_KEY] = PersistentDict()

        queue_key = self.queue_key_for_job_type(job_type)
        queues = self.get_queues()
        if queue_key in queues:
            if not isinstance(queues[queue_key]['queue'], queue_type):
                raise QueueAlreadyExistsWithDifferentType()
        else:
            queues[queue_key] = PersistentDict(
                {'queue': queue_type(),
                 'commit_batch_size': commit_batch_size,
                 'commit_to_solr': commit_to_solr})

        return queue_key, queues[queue_key]

    def assert_queue_type_is_valid(self, queue_type):
        assert queue_type in self.supported_queue_types, "Invalid queue type"

    def remove_queue(self, job_type):
        return self.get_queues().pop(self.queue_key_for_job_type(job_type))

    def get_queues(self):
        ann = IAnnotations(self.context)
        queues = ann.get(NIGHTLY_MAINTENANCE_JOB_QUEUES_KEY, {})
        return queues

    def queue_key_for_job_type(self, job_type):
        return job_type.job_type_identifier

    def get_queue(self, job_type):
        key = self.queue_key_for_job_type(job_type)
        queue = self.get_queues().get(key)
        if queue is None:
            raise QueueIsMissing()
        return queue

    def add_job(self, job):
        queue = self.get_queue(job.job_type)['queue']
        queue.add(job.variable_argument)

    def remove_job(self, job):
        queue = self.get_queue(job.job_type)['queue']
        if job.variable_argument not in queue:
            raise JobIsMissing()
        queue.remove(job.variable_argument)

    @property
    def jobs(self):
        queues = self.get_queues()
        for queue_key, queue in queues.items():
            job_type = MaintenanceJobType.from_identifier(queue_key)

            # Avoid list size changing during iteration
            job_arguments = list(queue['queue'])

            for variable_argument in job_arguments:
                yield MaintenanceJob(job_type, variable_argument)

    def get_jobs_count(self, queue_key=None):
        if queue_key:
            return len(self.get_queues()[queue_key]['queue'])
        return sum(len(queue['queue']) for queue in self.get_queues().values())


class NightlyMaintenanceJobsProvider(NightlyJobProviderBase):
    """This provider is used to run MaintenanceJobs over night which have
    previously been added in a queue using the MaintenanceQueuesManager.
    """

    def __init__(self, context, request, logger):
        super(NightlyMaintenanceJobsProvider, self).__init__(context, request, logger)
        self.queues_manager = MaintenanceQueuesManager(context)
        self.job_counter = Counter()
        self.current_job_type = None

    def __iter__(self):
        return self.queues_manager.jobs

    def __len__(self):
        return self.queues_manager.get_jobs_count()

    def run_job(self, job, interrupt_if_necessary):
        """Run the job.
        """
        key = self.queues_manager.queue_key_for_job_type(job.job_type)
        self.job_counter[key] += 1

        if key != self.current_job_type:
            self.current_job_type = key
            self.logger.info('Starting execution of {} jobs with key {}'.format(
                self.queues_manager.get_jobs_count(key), key))

        job.execute()
        self.queues_manager.remove_job(job)

        if self.job_counter[key] % 5000 == 0:
            self.logger.info('{}: Done {}, {} remaining'.format(
                key,
                self.job_counter[key],
                self.queues_manager.get_jobs_count(key)))
            self.logger.info('Total: Done {}, {} remaining'.format(
                sum(self.job_counter.values()),
                self.queues_manager.get_jobs_count()))

    def maybe_commit(self, job):
        key = self.queues_manager.queue_key_for_job_type(job.job_type)
        queue = self.queues_manager.get_queue(job.job_type)

        # If it is the last job of a queue, we remove the queue and commit
        force = False
        if len(queue['queue']) == 0:
            self.queues_manager.remove_queue(job.job_type)
            force = True

        if self.job_counter[key] % queue['commit_batch_size'] == 0 or force:
            if queue['commit_to_solr']:
                manager = getUtility(ISolrConnectionManager)
                manager.connection.commit(after_commit=False)
            transaction.commit()
