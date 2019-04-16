from datetime import datetime
from datetime import timedelta
from opengever.base.sentry import log_msg_to_sentry
from opengever.nightlyjobs.interfaces import INightlyJobProvider
from opengever.nightlyjobs.interfaces import INightlyJobsSettings
from plone import api
from zope.component import getAdapters
from zope.globalrequest import getRequest
import transaction


class TimeWindowExceeded(Exception):

    message = "Time window exceeded. Window: {:%H:%M}-{:%H:%M}. "\
              "Current time: {:%H:%M}"

    def __init__(self, start, end):
        self.current_time = datetime.now().time()
        self.start = start
        self.end = end
        message = self.message.format(start, end, self.current_time)
        super(TimeWindowExceeded, self).__init__(message)


class SystemLoadCritical(Exception):
    pass


class NightlyJobRunner(object):
    """ This class is used to execute nightly jobs.
    It will try to execute all jobs provided by the registered
    nightly job providers (named multiadapters of INightlyJobProvider).
    It will stop execution when not in the defined timeframe or when
    the system load is too high.
    """

    def __init__(self):
        # retrieve window start and end times
        self.window_start = api.portal.get_registry_record(
            'start_time', interface=INightlyJobsSettings)
        self.window_end = api.portal.get_registry_record(
            'end_time', interface=INightlyJobsSettings)
        self.window_length = self._positive_timedelta(
            self.window_start, self.window_end)

        # retrieve all providers
        self.job_providers = {name: provider for name, provider
                              in getAdapters([api.portal.get(), getRequest()],
                                             INightlyJobProvider)}

    @staticmethod
    def _positive_timedelta(time1, time2):
        """ Returns the positive timedelta between two time objects (time2-time1).
        This is necessary to correctly handle timedeltas around midnight.
        """
        datetime1 = datetime(1900, 1, 1, time1.hour, time1.minute, time1.second)
        datetime2 = datetime(1900, 1, 1, time2.hour, time2.minute, time2.second)
        if datetime2 < datetime1:
            datetime2 += timedelta(1)
        return datetime2 - datetime1

    def get_jobs(self):
        for job_provider in self.job_providers.values():
            for job in job_provider:
                yield job

    def execute_pending_jobs(self):
        for job in self.get_jobs():
            try:
                self.interrupt_if_necessary()
                provider = self.job_providers.get(job.provider_name)
                provider.run_job(job, self.interrupt_if_necessary)
            except (TimeWindowExceeded, SystemLoadCritical) as exc:
                transaction.abort()
                message = self.format_early_abort_message(exc)
                self.log_to_sentry(message)
                return exc
            transaction.commit()

    def interrupt_if_necessary(self):
        if not self.check_in_time_window():
            raise TimeWindowExceeded(self.window_start, self.window_end)
        if self.check_system_overloaded():
            raise SystemLoadCritical()

    def check_in_time_window(self):
        current_time = datetime.now().time()
        current_timedelta = self._positive_timedelta(self.window_start, current_time)
        return current_timedelta < self.window_length

    def check_system_overloaded(self):
        return False

    def format_early_abort_message(self, exc):
        info = "\n".join("{} executed {} out of {} jobs".format(
            provider.provider_name, provider.njobs_executed, provider.njobs)
            for provider in self.job_providers.values())
        return "{}\n{}".format(repr(exc), info)

    def log_to_sentry(self, message):
        log_msg_to_sentry(message, request=getRequest())

    @property
    def njobs_remaining(self):
        if not self.job_providers:
            return 0
        return sum(len(provider) for provider in self.job_providers.values())

    @property
    def njobs_total(self):
        if not self.job_providers:
            return 0
        return sum(provider.njobs for provider in self.job_providers.values())

    @property
    def njobs_executed(self):
        if not self.job_providers:
            return 0
        return sum(provider.njobs_executed for provider in self.job_providers.values())
