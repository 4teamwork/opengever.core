from zope import schema
from zope.interface import Interface
from datetime import time


class INightlyJobsSettings(Interface):

    start_time = schema.Time(
        title=u'Nightly jobs window start time',
        description=u'Execution of nightly jobs will only be allowed after this time',
        default=time(1, 0))

    end_time = schema.Time(
        title=u'Nightly jobs window end time',
        description=u'Execution of nightly jobs will only be allowed before this time',
        default=time(5, 0))
