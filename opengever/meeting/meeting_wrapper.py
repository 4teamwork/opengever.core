from Acquisition import Implicit
from OFS.Traversable import Traversable
from opengever.locking.interfaces import ISQLLockable
from opengever.meeting.interfaces import IMeetingWrapper
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from zope.interface import implements
import ExtensionClass


class MeetingWrapper(ExtensionClass.Base, Implicit, Traversable):

    implements(IMeetingWrapper, ISQLLockable, IHideFromBreadcrumbs)

    def __init__(self, model):
        self.model = model

    def absolute_url(self):
        return self.model.get_url(view=None)

    def __before_publishing_traverse__(self, arg1, arg2=None):
        """Implements default-view behavior for meetings.

        Means that if a meeting gets accessed directly without a view,
        the pre-traversal hook make sure that the `view` gets displayed.
        """

        # XXX hack around a bug(?) in BeforeTraverse.MultiHook
        # see Products.CMFCore.DynamicType.__before_publishing_traverse__
        REQUEST = arg2 or arg1

        stack = REQUEST['TraversalRequestNameStack']
        if stack == []:
            stack.append('view')
            REQUEST._hacked_path = 1
