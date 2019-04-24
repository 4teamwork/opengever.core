
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



    """

