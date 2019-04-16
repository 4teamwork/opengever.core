
class NightlyJob(object):
    """ Baseclass for specific implementations of nightly jobs.
    Derived classes should be kept simple to make sure they are compatible
    with possible future queuing systems (no complex python objects in the
    args and kwargs).
    provider_name should be the name of the JobProvider (i.e. name of the named
    adapter, so that the runner can find with which JobProvider to execute the
    job)
    """
    provider_name = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class BaseJobProvider(object):
    """ Serves as baseclass for specific implementations of nightly
    job provider which should be multiadapters of 'IPloneSiteRoot' and
    'IBrowserRequest' implementing 'INightlyJobProvider'.
    'initialize' and 'execute_job' have to be defined in the subclasses

    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.initialize()
        self.njobs_executed = 0
        self.running_job = None

    def initialize(self):
        """ This method should prepare the list of jobs in 'self._jobs'
        and save the number of jobs in 'self.njobs'.
        'self._jobs' needs to be an iterable of 'NightlyJob'.
        """
        raise NotImplementedError()

    def execute_job(job, interrupt_if_necessary):
        """ This method takes care of executing a given job.
        """
        raise NotImplementedError()

    def __iter__(self):
        return self

    def next(self):
        return next(self._jobs)

    def __len__(self):
        """ Number of remaining jobs.
        """
        return self.njobs - self.njobs_executed

    def run_job(self, job, interrupt_if_necessary):
        self.pre_job_run(job)
        self.execute_job(job, interrupt_if_necessary)
        self.post_job_run(job)

    def pre_job_run(self, job):
        self.running_job = job

    def post_job_run(self, job):
        self.njobs_executed += 1
        self.running_job = None
