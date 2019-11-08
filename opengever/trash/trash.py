from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import _checkPermission
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface
from zope.interface import noLongerProvides
from opengever.document.interfaces import ICheckinCheckoutManager
from zope.component import queryMultiAdapter


class ITrashable(Interface):
    """Interface proveded by trashable content.
    """


class ITrashableMarker(Interface):
    """Marker interface for the trashable behavior.
    """


class ITrashed(Interface):
    """All Objects wich provide that interfaces
    are "moved to trash" (special delete functionality)
    """


class ITrashedEvent(IObjectEvent):
    """Interface of an event which gets fired when moving a document to trash.
    """


class IUntrashedEvent(IObjectEvent):
    """Interface of an event which gets fired when ractivating a trashed document.
    """


class TrashedEvent(ObjectEvent):
    """The event which gets fired when moving a document to trash.
    """

    implements(ITrashedEvent)


class UntrashedEvent(ObjectEvent):
    """The event which gets fired when reactivating a trashed document.
    """

    implements(IUntrashedEvent)


class TrashError(Exception):
    """An error that occurs during a trash/untrash operation."""


class Trasher(object):
    """An object which handles trashing/untrashing documents.
    """

    def __init__(self, context):
        self.context = context

    def trash(self):
        # check that document can be trashed
        self.verify_may_trash()

        alsoProvides(self.context, ITrashed)

        # Trashed objects will be filtered from catalog search results by
        # default via a monkey patch somewhere in opengever.base.monkey
        self.reindex()
        notify(TrashedEvent(self.context))

    def untrash(self):
        self.verify_may_untrash()

        noLongerProvides(self.context, ITrashed)

        self.reindex()
        notify(UntrashedEvent(self.context))

    def verify_may_trash(self, raise_on_violations=True):
        if not self.check_trash_permission():
            if raise_on_violations:
                raise Unauthorized()
            return False

        if not self.is_trashable():
            if raise_on_violations:
                raise TrashError('Not trashable')
            return False

        if self.is_trashed():
            if raise_on_violations:
                raise TrashError('Already trashed')
            return False

        if self.is_checked_out():
            if raise_on_violations:
                raise TrashError('Document checked out')
            return False

        if self.is_returned_excerpt():
            if raise_on_violations:
                raise TrashError('The document has been returned as excerpt')
            return False

        return True

    def verify_may_untrash(self, raise_on_violations=True):
        if not self.check_untrash_permission():
            if raise_on_violations:
                raise Unauthorized()
            return False

        if not ITrashed.providedBy(self.context) or self.context.is_removed:
            if raise_on_violations:
                raise Unauthorized()
            return False

        return True

    def reindex(self):
        self.context.setModificationDate()
        self.context.reindexObject(idxs=['trashed', 'object_provides', 'modified'])

    def check_trash_permission(self):
        container = aq_parent(aq_inner(self.context))
        return all(_checkPermission('opengever.trash: Trash content', obj)
                   for obj in (self.context, container))

    def check_untrash_permission(self):
        container = aq_parent(aq_inner(self.context))
        return all((_checkPermission('opengever.trash: Untrash content', self.context),
                    _checkPermission('opengever.trash: Trash content', container)))

    def is_trashable(self):
        return ITrashableMarker.providedBy(self.context)

    def is_trashed(self):
        return ITrashed.providedBy(self.context)

    def is_checked_out(self):
        manager = queryMultiAdapter((self.context, self.context.REQUEST),
                                    ICheckinCheckoutManager)
        if manager and manager.get_checked_out_by():
            return True
        return False

    def is_returned_excerpt(self):
        return (self.context.get_proposal() is not None
                and self.context.get_proposal().get_excerpt() == self.context)
