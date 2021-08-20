"""
This module provides a very flexible way to perform maintenance tasks overnight.
A MaintenanceJob allows to execute any function with any number of arguments.
Such MaintenanceJobs will get added to queues using the MaintenanceQueuesManager
and run overnight by the NightlyMaintenanceJobsProvider. MaintenanceJobs are
grouped by MaintenanceJobType in the queues (one queue per type) for efficiency.
"""

from opengever.nightlyjobs.interfaces import INightlyJobProvider
from persistent.dict import PersistentDict
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import importlib
import logging


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


class MaintenanceJobType(object):
    """A maintenance job type is composed of a function and a set of arguments
    (fixed_arguments).

    An instance of MaintenanceJobType is fully determined by its
    job_type_identifier which contains the fixed_arguments and the information
    needed to import the function.

    The class contains a constructor from_identifier allowing to reconstruct a
    MaintenanceJobType from a job_type_identifier.
    """

    def __init__(self, function, **fixed_arguments):
        self.function = function
        self.fixed_arguments = fixed_arguments

    def __eq__(self, other):
        return (self.function == other.function and
                self.fixed_arguments == other.fixed_arguments)

    @property
    def module_dotted_name(self):
        return self.function.__module__

    @property
    def function_name(self):
        return self.function.__name__

    @property
    def job_type_identifier(self):
        return (self.function_name,
                self.module_dotted_name,
                tuple(sorted(self.fixed_arguments.items())))

    @classmethod
    def from_identifier(cls, job_type_identifier):
        function_name, module_dotted_name, fixed_args_tuple = job_type_identifier
        module = importlib.import_module(module_dotted_name)
        function = getattr(module, function_name)
        if function is None:
            raise FunctionNotFound()
        fixed_arguments = dict(fixed_args_tuple)
        return cls(function, **fixed_arguments)


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
        return (self.job_type == other.job_type and
                self.variable_argument == other.variable_argument)

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
    """
    def __init__(self, context):
        self.context = context

    def add_queue(self, job_type, queue_type):
        ann = IAnnotations(self.context)
        if NIGHTLY_MAINTENANCE_JOB_QUEUES_KEY not in ann:
            ann[NIGHTLY_MAINTENANCE_JOB_QUEUES_KEY] = PersistentDict()

        queue_key = self.queue_key_for_job_type(job_type)
        queues = self.get_queues()
        if queue_key in queues:
            if not isinstance(queues[queue_key], queue_type):
                raise QueueAlreadyExistsWithDifferentType
        else:
            queues[queue_key] = queue_type()
        return queue_key, queues[queue_key]

    def remove_queue(self, job_type):
        self.get_queues().pop(self.queue_key_for_job_type(job_type))

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
        queue = self.get_queue(job.job_type)
        queue.add(job.variable_argument)

    def remove_job(self, job, remove_queue_if_empty=True):
        queue = self.get_queue(job.job_type)
        if job.variable_argument not in queue:
            raise JobIsMissing()
        queue.remove(job.variable_argument)
        if remove_queue_if_empty and len(queue) == 0:
            self.remove_queue(job.job_type)

    @property
    def jobs(self):
        queues = self.get_queues()
        for queue_key, queue in queues.items():
            job_type = MaintenanceJobType.from_identifier(queue_key)

            # Avoid list size changing during iteration
            job_arguments = list(queue)

            for variable_argument in job_arguments:
                yield MaintenanceJob(job_type, variable_argument)

    def get_jobs_count(self):
        return sum(len(queue) for queue in self.get_queues().values())


@implementer(INightlyJobProvider)
@adapter(IPloneSiteRoot, IBrowserRequest, logging.Logger)
class NightlyMaintenanceJobsProvider(object):
    """This provider is used to run MaintenanceJobs over night which have
    previously been added in a queue using the MaintenanceQueuesManager.
    """

    def __init__(self, context, request, logger):
        self.context = context
        self.request = request
        self.logger = logger
        self.queues_manager = MaintenanceQueuesManager(context)

    def __iter__(self):
        return self.queues_manager.jobs

    def __len__(self):
        return self.queues_manager.get_jobs_count()

    def run_job(self, job, interrupt_if_necessary):
        """Run the job.
        """
        self.logger.info('Executing maintenance job: %r' % job)

        job.execute()
        self.queues_manager.remove_job(job)
