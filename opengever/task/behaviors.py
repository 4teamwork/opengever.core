from opengever.base.interfaces import ISequenceNumber
from plone.app.content.interfaces import INameFromTitle
from zope.component import getUtility
from zope.interface import implementer


class ITaskNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


@implementer(ITaskNameFromTitle)
class TaskNameFromTitle(object):
    """Speical name from title behavior for letting the normalizing name
    chooser choose the ID like want it to be.
    The of a task should be in the format: "task-{sequence number}"
    """

    format = u'task-%i'

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format % seq_number
