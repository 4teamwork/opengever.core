from Acquisition import Implicit
from OFS.Traversable import Traversable
from opengever.locking.interfaces import ISQLLockable
from opengever.meeting.interfaces import IMeetingWrapper
from zope.interface import implements
import ExtensionClass


class MeetingWrapper(ExtensionClass.Base, Implicit, Traversable):

    implements(IMeetingWrapper, ISQLLockable)

    def __init__(self, model):
        self.model = model

    def absolute_url(self):
        return self.model.get_url(view=None)
