from collective.taskqueue.interfaces import ITaskQueue
from collective.taskqueue.interfaces import ITaskQueueLayer
from collective.taskqueue.taskqueue import LocalVolatileTaskQueue
from datetime import datetime
from datetime import timedelta
from opengever.base.sentry import log_msg_to_sentry
from opengever.nightlyjobs.interfaces import INightlyJobProvider
from opengever.nightlyjobs.interfaces import INightlyJobsSettings
from plone import api
from plone.subrequest import subrequest
from zope.component import getAdapters
from zope.component import provideUtility
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
import logging
import psutil
import transaction


def nightly_jobs_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=INightlyJobsSettings)


class TimeWindowExceeded(Exception):

    message = "Time window exceeded. Window: {}-{}. "\
              "Current time: {:%H:%M}"

    def __init__(self, now, start, end):
        self.current_time = now
        self.start = start
        self.end = end
        message = self.message.format(start, end, self.current_time)
        super(TimeWindowExceeded, self).__init__(message)


class SystemLoadCritical(Exception):

    message = "System overloaded.\n"\
              "Available memory: {}MB; limit: {}MB\n"\
              "Percent memory: {}; limit: {}"

    def __init__(self, load, limits):
        self.load = load
        self.limits = limits
        message = self.message.format(load['virtual_memory_available'] / 1024 / 1024,
                                      limits['virtual_memory_available'] / 1024 / 1024,
                                      load['virtual_memory_percent'],
                                      limits['virtual_memory_percent'])
        super(SystemLoadCritical, self).__init__(message)


class NightlyJobRunner(object):
    """ This class is used to execute nightly jobs.
    It will try to execute all jobs provided by the registered
    nightly job providers (named multiadapters of INightlyJobProvider).
    It will stop execution when not in the defined timeframe or when
    the system load is too high, except if force_exectution is set
    to True
    """

    LOAD_LIMITS = {'virtual_memory_available': 100 * 1024 * 1024,
                   'virtual_memory_percent': 95}

    def __init__(self, setup_own_task_queue=False, force_execution=False,
                 logger=None):
        self.force_execution = force_execution

        if logger is None:
            logger = logging.getLogger('opengever.nightlyjobs')
        self.log = logger

        # retrieve window start and end times
        self.window_start = api.portal.get_registry_record(
            'start_time', interface=INightlyJobsSettings)
        self.window_end = api.portal.get_registry_record(
            'end_time', interface=INightlyJobsSettings)

        # retrieve all providers
        self.job_providers = self.get_job_providers()

        self.initial_jobs_count = {name: len(provider) for name, provider
                                   in self.job_providers.items()}

        # The regular task queue from bumblebee isn't available when
        # invoked as a bin/instance zopectl_cmd or script. For that case,
        # we need to set up our own queue to catch all queued jobs, and then
        # process them using plone.subrequest
        self.setup_own_task_queue = setup_own_task_queue
        if setup_own_task_queue:
            self._task_queue = self.setup_task_queue()

    def get_job_providers(self):
        return {name: provider for name, provider
                in getAdapters([api.portal.get(), getRequest(), self.log],
                               INightlyJobProvider)}

    def execute_pending_jobs(self, early_check=True):
        if early_check:
            # When invoked from a cron job, we first check that time window
            # and system load are acceptable. Otherwise cron job is misconfigured.
            self.interrupt_if_necessary()

        for provider_name, provider in self.job_providers.items():
            self.log.info('Executing jobs for provider %r' % provider_name)
            for job in provider:
                try:
                    self.interrupt_if_necessary()
                    provider.run_job(job, self.interrupt_if_necessary)
                except (TimeWindowExceeded, SystemLoadCritical) as exc:
                    transaction.abort()
                    message = self.format_early_abort_message(exc)
                    self.log_to_sentry(message)
                    return exc
                transaction.commit()

                # If we set up our own task queue, process its jobs.
                # This must happen after the transaction has been committed.
                if self.setup_own_task_queue:
                    self.process_task_queue()

    def setup_task_queue(self):
        task_queue = LocalVolatileTaskQueue()
        provideUtility(task_queue, ITaskQueue, name='default')
        return task_queue

    def process_task_queue(self):
        queue = self._task_queue.queue

        self.log.info('Processing %d task queue jobs...' % queue.qsize())
        request = getRequest()
        alsoProvides(request, ITaskQueueLayer)

        while not queue.empty():
            job = queue.get()

            # Process job using plone.subrequest
            response = subrequest(job['url'])
            assert response.status == 200

            # XXX: We don't currently handle the user that is supposed to be
            # authenticated, and the task ID, both of which c.taskqueue
            # provides in the job.

        noLongerProvides(request, ITaskQueueLayer)
        self.log.info('All task queue jobs processed.')

    def interrupt_if_necessary(self):
        if self.force_execution:
            return
        now = datetime.now().time()
        if not self.check_in_time_window(now):
            raise TimeWindowExceeded(now, self.window_start, self.window_end)

        load = self.get_system_load()
        if self.check_system_overloaded(load):
            raise SystemLoadCritical(load, self.LOAD_LIMITS)

    def check_in_time_window(self, now):
        current_time = timedelta(hours=now.hour, minutes=now.minute)
        if current_time - self.window_start < timedelta():
            current_time += timedelta(hours=24)
        return self.window_start <= current_time <= self.window_end

    def _is_memory_full(self, load):
        return (load['virtual_memory_available'] < self.LOAD_LIMITS['virtual_memory_available']
                or load['virtual_memory_percent'] > self.LOAD_LIMITS['virtual_memory_percent'])

    def get_system_load(self):
        return {'virtual_memory_available': psutil.virtual_memory().available,
                'virtual_memory_percent': psutil.virtual_memory().percent}

    def check_system_overloaded(self, load):
        return self._is_memory_full(load)

    def format_early_abort_message(self, exc):
        info = "\n".join("{} executed {} out of {} jobs".format(
                            provider_name,
                            self.get_executed_jobs_count(provider_name),
                            self.get_initial_jobs_count(provider_name))
                         for provider_name, provider in self.job_providers.items())
        return "{}\n{}".format(repr(exc), info)

    def log_to_sentry(self, message):
        log_msg_to_sentry(message, request=getRequest())

    def get_initial_jobs_count(self, provider_name=None):
        if not provider_name:
            return sum(self.initial_jobs_count.values())
        return self.initial_jobs_count.get(provider_name)

    def get_remaining_jobs_count(self, provider_name=None):
        if not provider_name:
            return sum(len(provider) for provider in self.job_providers.values())
        return len(self.job_providers[provider_name])

    def get_executed_jobs_count(self, provider_name=None):
        return (self.get_initial_jobs_count(provider_name) -
                self.get_remaining_jobs_count(provider_name))
