from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from datetime import date
from datetime import datetime
from opengever.base.handlers import ObjectTouchedEvent
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.events import ObjectBeforeCheckInEvent
from opengever.document.events import ObjectCheckedInEvent
from opengever.document.events import ObjectCheckedOutEvent
from opengever.document.events import ObjectCheckoutCanceledEvent
from opengever.document.events import ObjectRevertedToVersion
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.ogds.base.actor import Actor
from opengever.trash.trash import ITrashed
from persistent.list import PersistentList
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
COLLABORATORS_ANNOTATIONS_KEY = 'opengever.document.collaborators'


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

    def is_checked_out_by_another_user(self):
        return bool(self.get_checked_out_by()) and not self.is_checked_out_by_current_user()

    def is_checked_out_by_current_user(self):
        return self.get_checked_out_by() == api.user.get_current().getId()

    def is_file_upload_allowed(self):
        return self.is_checked_out_by_current_user() and not self.is_locked()

    def is_checkoutable(self):
        return bool(not self.get_checked_out_by() and not self.is_locked())

    def is_checkout_permitted(self):
        return bool(
            self.check_permission('opengever.document: Checkout')
            and self.check_permission('Modify portal content')
            )

    def is_not_trashed(self):
        return bool(not ITrashed.providedBy(self.context))

    def is_checkout_allowed(self):
        """Checks whether checkout is allowed for the current user on the
        adapted document.
        """
        return bool(
            self.is_checkoutable()
            and self.versioner.is_versionable()
            and self.is_checkout_permitted()
            and self.is_not_trashed()
            )

    def checkout(self, collaborative=False):
        """Checkout the adapted document.
        """
        # is the user allowed to checkout?
        if not self.is_checkout_allowed():
            raise Unauthorized

        # now remember who checked out the document
        user_id = getSecurityManager().getUser().getId()
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = user_id

        if collaborative:
            self.add_collaborator(user_id)

        # update last modified timestamp for recently modified menu
        self.context.setModificationDate()

        self.context.reindexObject(idxs=['checked_out', 'modified'])

        # fire the event
        notify(ObjectCheckedOutEvent(self.context, ''))
        notify(ObjectTouchedEvent(self.context))

    def add_collaborator(self, collaborator):
        if COLLABORATORS_ANNOTATIONS_KEY not in self.annotations:
            self.annotations[COLLABORATORS_ANNOTATIONS_KEY] = PersistentList()

        if collaborator not in self.annotations[COLLABORATORS_ANNOTATIONS_KEY]:
            self.annotations[COLLABORATORS_ANNOTATIONS_KEY].append(collaborator)

    def get_collaborators(self):
        return self.annotations.get(COLLABORATORS_ANNOTATIONS_KEY, [])

    def is_simple_checkin_allowed(self):
        return self.is_checkin_allowed() and not self.is_locked()

    def is_only_force_checkin_allowed(self):
        if self.is_checkin_allowed() and self.is_locked():
            return True
        return False

    def is_collaborative_checkout(self):
        """Whether this is a collaborative checkout or not.

        Collaborative checkouts are currently intended to be used by the
        Office Online WOPI view. They behave slightly differently
        than regular checkouts:

        - For collaborative checkouts, collaborators are tracked
        - They may only be checked in with checkin(collaborative=True)
          (Except force checkin)
        - Any of the collaborators may check in a collaborative checkout,
          not just the user that initially checked out the document.
        - On checkin, the list of collaborators gets written to the version
          and journal comments.
        """
        return bool(self.get_collaborators())

    def is_checkin_allowed(self, collaborative=False):
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

        if self.is_collaborative_checkout() and not collaborative:
            # If collaboratively checked out, only checkin(collaborative=True)
            # is allowed (via the WOPI View for now)
            return False

        current_user_id = getSecurityManager().getUser().getId()

        if collaborative:
            # For collaborative checkouts, any of the collaborators are
            # allowed to check in
            return current_user_id in self.get_collaborators()

        return self.get_checked_out_by() == current_user_id

    def checkin(self, comment='', collaborative=False):
        """Checkin the adapted document, using the `comment` for the
        journal entry.
        """
        notify(ObjectBeforeCheckInEvent(self.context))

        # is the user allowed to checkin?
        if not self.is_checkin_allowed(collaborative=collaborative):
            raise Unauthorized

        # remember that we checked in
        self.annotations[CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = None
        collaborators = self.annotations.pop(COLLABORATORS_ANNOTATIONS_KEY, None)

        # Clear any WebDAV locks left over by ExternalEditor if necessary
        self.clear_locks()

        if collaborators:
            # Replace user provided comment with list of collaborators
            collaborator_list = u', '.join(
                Actor.lookup(user_id).get_label()
                for user_id in collaborators)

            # XXX: The comment is translated in the site language here. We
            # should eventually change this so we can translate parametrized
            # messages during display time in the user's language.
            site_language = api.portal.get_default_language()
            comment = translate(
                _(u'label_document_collaborators',
                  default=u'Collaborators: ${collaborators}',
                  mapping={'collaborators': collaborator_list}),
                target_language=site_language.split('-')[0])

        # create new version in CMFEditions
        self.versioner.create_version(comment)

        # update last modified timestamp for recently modified menu
        self.context.setModificationDate()

        self.context.reindexObject(idxs=['checked_out', 'modified'])

        # fire the event
        notify(ObjectCheckedInEvent(self.context, comment))
        notify(ObjectTouchedEvent(self.context))

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
        self.context.reindexObject(idxs=['checked_out'])

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
        """Return wheter reverting the document to a previous version is
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
            # Avoid plone.protect unnecessarily jumping in
            self.request.response.setHeader('content-type', 'text/plain')
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
