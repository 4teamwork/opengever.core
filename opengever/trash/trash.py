from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.document.behaviors import IBaseDocument
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.workspace.interfaces import IWorkspaceFolder
from plone.dexterity.interfaces import IDexterityContent
from plone.locking.interfaces import ILockable
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getAdapter
from zope.component import queryMultiAdapter
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
from zope.interface import noLongerProvides


# XXX: Deprecated interface.
class ITrashable(Interface):
    """Interface proveded by trashable content.
    """


# XXX: Deprecated interface.
class ITrashableMarker(Interface):
    """Marker interface for the trashable behavior.
    """


class ITrasher(Interface):
    """Interface for the Trasher adapter.
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


@implementer(ITrasher)
@adapter(IDexterityContent)
class DefaultContentTrasher(object):

    def __init__(self, context):
        self.context = context

    def trash(self):
        self.verify_may_trash()
        self._trash()

    def _trash(self):
        if ITrashed.providedBy(self.context):
            return
        alsoProvides(self.context, ITrashed)
        self.reindex()
        notify(TrashedEvent(self.context))

    def untrash(self):
        self.verify_may_untrash()
        self._untrash()

    def _untrash(self):
        noLongerProvides(self.context, ITrashed)
        self.reindex()
        notify(UntrashedEvent(self.context))

    def verify_may_trash(self, raise_on_violations=True):
        if self.is_trashed():
            if raise_on_violations:
                raise TrashError('Already trashed')
            return False
        return self._verify_may_trash(raise_on_violations)

    def _verify_may_trash(self, raise_on_violations=True):
        if not self.is_trashable():
            if raise_on_violations:
                raise TrashError('Not trashable')
            return False

        if not self.check_trash_permission():
            if raise_on_violations:
                raise Unauthorized()
            return False

        if self.is_locked():
            if raise_on_violations:
                raise TrashError('The document is locked')
            return False

        return True

    def verify_may_untrash(self, raise_on_violations=True):
        if self.is_parent_trashed():
            if raise_on_violations:
                raise Unauthorized()
            return False
        return self._verify_may_untrash(raise_on_violations)

    def _verify_may_untrash(self, raise_on_violations=True):
        if not self.check_untrash_permission():
            if raise_on_violations:
                raise Unauthorized()
            return False

        if not self.is_trashed() or self.is_removed():
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
        return False

    def is_trashed(self):
        return ITrashed.providedBy(self.context)

    def is_locked(self):
        return ILockable(self.context).locked()

    def is_removed(self):
        return False

    def is_parent_trashed(self):
        container = aq_parent(aq_inner(self.context))
        trasher = getAdapter(container, ITrasher)
        return trasher.is_trashed()


@implementer(ITrasher)
@adapter(IPloneSiteRoot)
class PloneSiteRootTrasher(DefaultContentTrasher):

    def verify_may_trash(self, raise_on_violations=True):
        if raise_on_violations:
            raise Unauthorized()
        return False

    def verify_may_untrash(self, raise_on_violations=True):
        if raise_on_violations:
            raise Unauthorized()
        return False


@adapter(IBaseDocument)
class DocumentTrasher(DefaultContentTrasher):
    """An object which handles trashing/untrashing documents.
    """

    def _verify_may_trash(self, raise_on_violations=True):
        if not super(DocumentTrasher, self)._verify_may_trash(raise_on_violations):
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

    def is_trashable(self):
        return True

    def is_removed(self):
        return self.context.is_removed

    def is_checked_out(self):
        manager = queryMultiAdapter((self.context, self.context.REQUEST),
                                    ICheckinCheckoutManager)
        if manager and manager.get_checked_out_by():
            return True
        return False

    def is_returned_excerpt(self):
        submitted_proposal = self.context.get_submitted_proposal(
            check_security=False)
        if not submitted_proposal:
            return False

        return submitted_proposal.get_excerpt() == self.context


@adapter(IWorkspaceFolder)
class WorkspaceFolderTrasher(DefaultContentTrasher):
    """An object which handles trashing/untrashing workspace folders.
    """

    def _trash(self):
        super(WorkspaceFolderTrasher, self)._trash()
        for obj in self.context.objectValues():
            trasher = ITrasher(obj)
            trasher._verify_may_trash()
            trasher._trash()

    def _untrash(self):
        super(WorkspaceFolderTrasher, self)._untrash()
        for obj in self.context.objectValues():
            trasher = ITrasher(obj)
            trasher._verify_may_untrash()
            trasher._untrash()

    def is_trashable(self):
        return True
