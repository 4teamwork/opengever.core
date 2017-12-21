from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from datetime import date
from datetime import datetime
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.events import ObjectBeforeCheckInEvent
from opengever.document.events import ObjectCheckedInEvent
from opengever.document.events import ObjectCheckedOutEvent
from opengever.document.events import ObjectCheckoutCanceledEvent
from opengever.document.events import ObjectRevertedToVersion
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.trash.trash import ITrashed
from plone import api
from plone.locking.interfaces import IRefreshableLockable
from plone.namedfile.file import NamedBlobFile
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


CHECKIN_CHECKOUT_ANNOTATIONS_KEY = 'opengever.document.checked_out_by'


@implementer(ICheckinCheckoutManager)
@adapter(IDocumentSchema, IBrowserRequest)
class CheckinCheckoutManager(object):
    """Document checkout flow management."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_checked_out_by(self):
        """If the document is checked out, this method returns the userid
        of the user who has checked out the document, otherwise it
        returns `None`.
        """
        return self.annotations.get(CHECKIN_CHECKOUT_ANNOTATIONS_KEY, None)

    def is_checked_out_by_current_user(self):
        return self.get_checked_out_by() == api.user.get_current().getId()

    def is_file_upload_allowed(self):
        return self.is_checked_out_by_current_user() and not self.is_locked()

    def is_checkout_allowed(self):
        """Checks whether checkout is allowed for the current user on the
        adapted document.
        """
        # is it already checked out?
        if self.get_checked_out_by():
            return False

        # does a user hold a lock?
        if self.is_locked():
            return False

        # is it versionable?
        if not self.versioner.is_versionable():
            return False

        # does the user have the necessary permission?
        if not self.check_permission('opengever.document: Checkout'):
            return False

        if not self.check_permission('Modify portal content'):
            return False

        # is it not trashed
        if ITrashed.providedBy(self.context):
            return False

        return True

    def checkout(self):
        """Checkout the adapted document.
        """
        # is the user allowed to checkout?
        if not self.is_checkout_allowed():
            raise Unauthorized

        # now remember who checked out the document
        user_id = getSecurityManager().getUser().getId()
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = user_id

        # finally, reindex the object
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(
            self.context,
            idxs=(
                'checked_out',
                ),
            update_metadata=True,
            )

        # fire the event
        notify(ObjectCheckedOutEvent(self.context, ''))

    def is_checkin_allowed(self):
        """Checks whether checkin is allowed for the current user on the
        adapted document.
        """
        # is it checked out?
        if not self.get_checked_out_by():
            return False

        # is it versionable?
        if not self.versioner.is_versionable():
            return False

        # Admins with Force Checkin permission may always check in
        if self.check_permission('opengever.document: Force Checkin'):
            return True

        # is the user able to write to the object?
        if not self.check_permission('Modify portal content'):
            return False

        # does the user have the necessary permission?
        if not self.check_permission('opengever.document: Checkin'):
            return False

        # is the user either the one who owns the checkout or
        # a manager?
        is_manager = self.check_permission('Manage portal')
        current_user_id = getSecurityManager().getUser().getId()
        if self.get_checked_out_by() == current_user_id or is_manager:
            return True
        else:
            return False

    def checkin(self, comment=''):
        """Checkin the adapted document, using the `comment` for the
        journal entry.
        """
        notify(ObjectBeforeCheckInEvent(self.context))

        # is the user allowed to checkin?
        if not self.is_checkin_allowed():
            raise Unauthorized

        # update document_date to current date
        self.context.document_date = date.today()

        # remember that we checked in
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = None

        # Clear any WebDAV locks left over by ExternalEditor if necessary
        self.clear_locks()

        # create new version in CMFEditions
        self.versioner.create_version(comment)

        # finally, reindex the object
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(
            self.context,
            idxs=(
                'checked_out',
                ),
            update_metadata=True,
            )

        # fire the event
        notify(ObjectCheckedInEvent(self.context, comment))

    def is_cancel_allowed(self):
        """Checks whether the user is able to cancel a checkout."""
        current_user_id = getSecurityManager().getUser().getId()
        current_checkout_id = self.get_checked_out_by()

        # is the document checked out?
        # is the document not locked?
        # is it versionable?
        # is the user allowed to cancel?
        # is the user either the one who owns the checkout or a manager?
        if (
                current_checkout_id
                and not IRefreshableLockable(self.context).locked()
                and self.versioner.is_versionable()
                and self.check_permission('opengever.document: Cancel')
                and bool(
                    current_checkout_id == current_user_id
                    or self.check_permission('Manage portal')
                    )
            ):
            return True

        return False

    def cancel(self):
        """Cancel the current checkout."""
        # is the user allowed to cancel?
        if not self.is_cancel_allowed():
            raise Unauthorized

        # revert to prior version (baseline) if a version exists.
        versioner = Versioner(self.context)
        if versioner.has_initial_version():
            self.revert_to_version(versioner.get_current_version_id(),
                                   create_version=False, force=True)

        # remember that we canceled in
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = None

        # finally, reindex the object
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(
            self.context,
            idxs=(
                'checked_out',
                ),
            update_metadata=True,
            )

        # Clear any WebDAV locks left over by ExternalEditor if necessary
        self.clear_locks()

        # fire the event
        notify(ObjectCheckoutCanceledEvent(self.context))

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
    def versioner(self):
        try:
            self._versioner
        except AttributeError:
            self._versioner = Versioner(self.context)

        return self._versioner

    def check_permission(self, permission):
        """Checks, whether the user has the `permission` on the adapted
        document or not.
        """
        return getSecurityManager().checkPermission(permission,
                                                    self.context)

    def is_revert_allowed(self):
        """Return wheter reverting a the document to a previous version is
        allowed.
        """
        # is it already checked out?
        if self.get_checked_out_by():
            return False

        # does a user hold a lock?
        if self.is_locked():
            return False

        # is it versionable?
        if not self.versioner.is_versionable():
            return False

        if not self.check_permission('Modify portal content'):
            return False

        # is it not trashed
        if ITrashed.providedBy(self.context):
            return False

        return True

    def revert_to_version(self, version_id, create_version=True, force=False):
        """Reverts the adapted document to a specific version. We only revert
        the file field, since we do not wan't to version the metadata on the
        document.
        If `create_version` is set to `True`, a new version is created after
        reverting.
        """
        if not force and not self.is_revert_allowed():
            raise Unauthorized()

        version = self.versioner.retrieve_version(version_id)
        old_obj = version.object
        if old_obj.file:
            # Create a new NamedBlobFile instance instead of using
            # a reference in order to avoid the version being reverted
            # to being overwritten later
            old_file_copy = NamedBlobFile(old_obj.file.data,
                                          filename=old_obj.file.filename,
                                          contentType=old_obj.file.contentType)

            self.context.file = old_file_copy
        else:
            self.context.file = None

        # update document_date to specific version creation date
        ts = version.sys_metadata['timestamp']
        self.context.document_date = datetime.fromtimestamp(ts).date()

        if create_version:
            # let's create a version
            msg = _(u'Reverted file to version ${version_id}.',
                    mapping=dict(version_id=version_id))
            comment = translate(msg, context=self.request)
            self.versioner.create_version(comment)

        # event
        notify(ObjectRevertedToVersion(self.context, version_id,
                                       create_version))

    def is_locked(self):
        """Returns True if a user has a WebDAV lock on the adapted
        document, False otherwise.
        """
        lockable = IRefreshableLockable(self.context)
        # List of all users that hold a lock on the document
        if lockable and lockable.locked():
            return True

        return False

    def clear_locks(self):
        """Clears any WebDAV locks on the adapted document left over by
        ExternalEditor.
        """
        lockable = IRefreshableLockable(self.context)
        if lockable and lockable.locked():
            lockable.clear_locks()
