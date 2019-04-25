
class NightlyJob(object):
    """ Class implementing nightly jobs.

    provider_name: should be the name of the JobProvider (i.e. name of the
                   named adapter, so that the runner can find with
                   which JobProvider to execute the job)

    data: contains the data necessary for the provider to execute the job.
          data should be kept simple to make sure it is compatible with
          possible future queuing systems (no complex python objects).
    """

    def __init__(self, provider_name, data):
        self.provider_name = provider_name
        self.data = data
