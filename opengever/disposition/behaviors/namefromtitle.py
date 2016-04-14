from opengever.base.interfaces import ISequenceNumber
from plone.app.content.interfaces import INameFromTitle
from zope.component import getUtility
from zope.interface import implements


class IDispositionNameFromTitle(INameFromTitle):
    """Special name from title behavior for letting the normalizing name
    chooser choose the ID.
    The id of a Dispostion should be in the format:
    "disposition-{sequence number}"
    """


class DispositionNameFromTitle(object):
    implements(IDispositionNameFromTitle)

    format = u'disposition-{}'

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format.format(seq_number)
