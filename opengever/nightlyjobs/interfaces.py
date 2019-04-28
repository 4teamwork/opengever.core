from zope import schema
from zope.interface import Interface
from datetime import timedelta


class INightlyJobsSettings(Interface):

    start_time = schema.Timedelta(
        title=u'Nightly jobs window start time',
        description=u'Execution of nightly jobs will only be allowed after '
                    u'this time. Should be between 0:00 and 24:00',
        default=timedelta(hours=1))

    end_time = schema.Timedelta(
        title=u'Nightly jobs window end time',
        description=u'Execution of nightly jobs will only be allowed before '
                    u'this time. Has to be larger than start_time and can be '
                    u'larger than 24:00',
        default=timedelta(hours=5))


class INightlyJobProvider(Interface):
    """ This interface should be provided by specific nightly job providers,
    which should be multiadapters of 'IPloneSiteRoot' and 'IBrowserRequest'.
    """

    def run_job(job, interrupt_if_necessary):
        """This method takes care of executing a given job.

        The `job` will be passed in by the runner, and is always a dictionary
        of job arguments, as returned by __iter__.
        """

    def __iter__():
        """Returns an iterator of jobs.

        The individial jobs must be dictionaries with the arguments that
        uniquely define a job.

        The specific keys in that dictionary are in the domain of the job
        provider, and it needs be able to make sense of them when those
        arguments are passed back in to run_job().
        """

    def __len__():
        """ Number of remaining jobs.
        """
