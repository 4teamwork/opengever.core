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
        """ This method takes care of executing a given job.
        """

    def __iter__():
        """ needs to return an iterable
        """

    def __len__():
        """ Number of remaining jobs.
        """
