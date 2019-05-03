from zope import schema
from zope.interface import Interface
from datetime import timedelta


class INightlyJobsSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable nightly jobs feature',
        description=u'Whether nightly job execution is enabled',
        default=False)

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

    def __init__(self, context, request, logger):
        """Should adapt IPloneSiteRoot, IBrowserRequest and logging.Logger.

        `logger` will be a Python logger passed in by the runner that is properly
        set up to write all nightly job related logging to a dedicated file.
        Nightly job providers should therefore use this logger instead of
        creating their own.
        """

    def run_job(job, interrupt_if_necessary):
        """This method takes care of executing a given job.

        The `job` will be passed in by the runner, and is always a dictionary
        of job arguments, as returned by __iter__.

        `interrupt_if_necessary` is a function (no arguments) that will be
        passed in by the runner. If the JobProvider does a lot of work in
        a single job execution, it should make sure to regularly call this
        function. This will give the runner the chance to interrupt the
        execution of the job if necessary, by raising either
        TimeWindowExceeded or SystemLoadCritical exceptions.

        These will then be handled by the runner by aborting the transaction
        (therefore discarding the unfinished work of the job) and terminating
        the nightly run, in order to not go over the time window or satisfy
        load constraints.
        """

    def __iter__():
        """Returns an iterator of jobs.

        The individial jobs must be dictionaries with the arguments that
        uniquely define a job.

        The specific keys in that dictionary are in the domain of the job
        provider, and it needs to be able to make sense of them when those
        arguments are passed back in to run_job().
        """

    def __len__():
        """ Number of remaining jobs.
        """
