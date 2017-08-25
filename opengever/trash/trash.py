from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import _checkPermission
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.event import notify
from zope.interface import implements
from zope.interface import Interface, alsoProvides, noLongerProvides


class ITrashable(Interface):
    pass


class ITrashableMarker(Interface):
    pass


class ITrashed(Interface):
    """
    All Objects wich provide that interfaces
    are "moved to trash" (special delete functionality)
    """
    pass


#Events
class ITrashedEvent(IObjectEvent):
    pass


class IUntrashedEvent(IObjectEvent):
    pass


class TrashedEvent(ObjectEvent):
    implements(ITrashedEvent)


class UntrashedEvent(ObjectEvent):
    implements(IUntrashedEvent)


class Trasher(object):

    def __init__(self, context):
        self.context = context

    def trash(self):
        folder = aq_parent(aq_inner(self.context))
        # check trash permission
        if not _checkPermission('opengever.trash: Trash content', folder):
            raise Unauthorized()

        alsoProvides(self.context, ITrashed)

        # Trashed objects will be filtered from catalog search results by
        # default via a monkey patch somewhere in opengever.base.monkey
        self.context.reindexObject()
        notify(TrashedEvent(self.context))

    def untrash(self):
        #XXX check Permission
        folder = aq_parent(aq_inner(self.context))
        if not _checkPermission('opengever.trash: Trash content', folder):
            raise Unauthorized()
        noLongerProvides(self.context, ITrashed)
        self.context.reindexObject()
        notify(UntrashedEvent(self.context))
