from AccessControl import getSecurityManager, Unauthorized
from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.events import ObjectCheckedInEvent
from opengever.document.events import ObjectCheckedOutEvent
from opengever.document.events import ObjectCheckoutCanceledEvent
from opengever.document.events import ObjectRevertedToVersion
from opengever.document.interfaces import ICheckinCheckoutManager
from plone.locking.interfaces import IRefreshableLockable
from plone.locking.interfaces import LockType
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.event import notify
from zope.publisher.interfaces.browser import IBrowserRequest


CHECKIN_CHECKOUT_ANNOTATIONS_KEY = 'opengever.document.checked_out_by'

DOCUMENT_CHECKOUT_LOCK = LockType(u'opengever.document.checkout_lock',
                                  stealable=False,
                                  user_unlockable=True)


class CheckinCheckoutManager(grok.MultiAdapter):
    grok.provides(ICheckinCheckoutManager)
    grok.adapts(IDocumentSchema, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def checked_out(self):
        """If the document is checked out, this method returns the userid
        of the user who has checked out the document, otherwise it
        returns `None`.
        """
        return self.annotations.get(CHECKIN_CHECKOUT_ANNOTATIONS_KEY, None)

    def is_checkout_allowed(self):
        """Checks whether checkout is allowed for the current user on the
        adapted document.
        """

        # is it already checked out?
        if self.checked_out():
            return False

        # is it versionable?
        if not self.repository.isVersionable(self.context):
            return False

        # does the user have the necessary permission?
        if not self.check_permission('opengever.document: Checkout'):
            return False

        # is the object already locked?
        if self.locking.locked():
            return False

        return True


    def checkout(self):
        """Checkout the adapted document.
        """

        # is the user allowed to checkout?
        if not self.is_checkout_allowed():
            raise Unauthorized

        # first let's lock the object for this user
        self.locking.lock(lock_type=DOCUMENT_CHECKOUT_LOCK)

        # now remember who checked out the document
        user_id = getSecurityManager().getUser().getId()
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = user_id

        # finally, reindex the object
        self.context.reindexObject()

        # fire the event
        notify(ObjectCheckedOutEvent(self.context, ''))

    def is_checkin_allowed(self):
        """Checks whether checkin is allowed for the current user on the
        adapted document.
        """

        # is it checked out?
        if not self.checked_out():
            return False

        # is it versionable?
        if not self.repository.isVersionable(self.context):
            return False

        # is the user able to write to the object?
        if not self.check_permission('cmf.ModifyPortalContent'):
            return False

        # does the user have the necessary permission?
        if not self.check_permission('opengever.document: Checkin'):
            return False

        # is the user able to steal the lock?
        if not self.locking.can_safely_unlock(
            lock_type=DOCUMENT_CHECKOUT_LOCK):
            return False

        # is the user either the one who owns the checkout or
        # a manager?
        is_manager = self.check_permission('Manage portal')
        current_user_id = getSecurityManager().getUser().getId()
        if self.checked_out() == current_user_id or is_manager:
            return True
        else:
            return False


    def checkin(self, comment=''):
        """Checkin the adapted document, using the `comment` for the
        journal entry.
        """

        # is the user allowed to checkin?
        if not self.is_checkin_allowed():
            raise Unauthorized

        # create new version in CMFEditions
        self.repository.save(obj=self.context, comment=comment)

        # unlock the object
        self.locking.unlock(lock_type=DOCUMENT_CHECKOUT_LOCK)

        # remember that we checked in
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = None

        # finally, reindex the object
        self.context.reindexObject()

        # fire the event
        notify(ObjectCheckedInEvent(self.context, comment))


    def is_cancel_allowed(self):
        """Checks whether the user is able to cancel a checkout.
        """

        # is the document checked out?
        if not self.checked_out():
            return False

        # is it versionable?
        if not self.repository.isVersionable(self.context):
            return False

        # is the user allowed to cancel?
        if not self.check_permission('opengever.document: Cancel'):
            return False

        # is the user able to steal the lock?
        if not self.locking.can_safely_unlock(
            lock_type=DOCUMENT_CHECKOUT_LOCK):
            return False

        # is the user either the one who owns the checkout or
        # a manager?
        is_manager = self.check_permission('Manage portal')
        current_user_id = getSecurityManager().getUser().getId()
        if self.checked_out() == current_user_id or is_manager:
            return True
        else:
            return False

    def cancel(self):
        """Cancel the current checkout.
        """

        # is the user allowed to cancel?
        if not self.is_cancel_allowed():
            raise Unauthorized

        # revert to prior version (baseline)
        baseline = self.repository.getHistory(self.context)[0]
        self.revert_to_version(baseline.version_id, create_version=False)

        # unlock the object
        self.locking.unlock(lock_type=DOCUMENT_CHECKOUT_LOCK)

        # remember that we canceled in
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = None

        # finally, reindex the object
        self.context.reindexObject()

        # fire the event
        notify(ObjectCheckoutCanceledEvent(self.context))


    @property
    def locking(self):
        """The TTWLockable adapter of the current document.
        """
        return getAdapter(self.context, IRefreshableLockable)

    @property
    def annotations(self):
        """Annotations of the current object.
        """
        try:
            self._annotations
        except AttributeError:
            self._annotations = IAnnotations(self.context)
        return self._annotations

    @property
    def repository(self):
        """The portal_repository tool
        """
        try:
            self._portal_repository
        except AttributeError:
            self._portal_repository = getToolByName(self.context,
                                                    'portal_repository')
        return self._portal_repository

    def check_permission(self, permission):
        """Checks, whether the user has the `permission` on the adapted
        document or not.
        """
        return getSecurityManager().checkPermission(permission,
                                                    self.context)

    def revert_to_version(self, version_id, create_version=True):
        """Reverts the adapted document to a specific version. We only revert
        the file field, since we do not wan't to version the metadata on the
        document.
        If `create_version` is set to `True`, a new version is created after
        reverting.
        """
        version = self.repository.retrieve(self.context, version_id)
        old_obj = version.object
        self.context.file = old_obj.file

        if create_version:
            # let's create a version
            comment = _(u'Reverted file to version ${version_id}',
                        mapping=dict(version_id=version_id))
            self.repository.save(obj=self.context, comment=comment)

        # event
        notify(ObjectRevertedToVersion(self.context, version_id,
                                       create_version))
