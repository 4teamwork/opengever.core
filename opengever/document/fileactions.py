from ftw.bumblebee.mimetypes import is_mimetype_supported
from opengever.api.lock import can_unlock_obj
from opengever.base.interfaces import IDeleter
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document.behaviors import IBaseDocument
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IFileActions
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from opengever.trash.trash import ITrashed
from opengever.trash.trash import ITrasher
from opengever.wopi import is_wopi_feature_enabled
from opengever.workspace import is_workspace_feature_enabled
from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.utils import is_restricted_workspace_and_guest
from plone import api
from plone.locking.interfaces import ILockable
from zExceptions import Forbidden
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IFileActions)
@adapter(IBaseDocument, Interface)
class BaseDocumentFileActions(object):
    """Define availability for actions and action sets on IBaseDocument.
    This adapter defines the availability for mails, as it is overwritten
    by DocumentFileActions for documents.

    Methods should return availability for one single action.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_versioned(self):
        return False

    def is_edit_metadata_action_available(self):
        return api.user.has_permission(
            'Modify portal content',
            obj=self.context)

    def is_any_checkout_or_edit_available(self):
        return False

    def is_office_online_edit_action_available(self):
        return False

    def is_oc_view_action_available(self):
        return self.context.has_file()

    def is_oc_direct_checkout_action_available(self):
        return False

    def is_oc_direct_edit_action_available(self):
        return False

    def is_oc_zem_checkout_action_available(self):
        return False

    def is_oc_zem_edit_action_available(self):
        return False

    def is_oc_unsupported_file_checkout_action_available(self):
        return False

    def is_checkin_without_comment_available(self):
        return False

    def is_checkin_with_comment_available(self):
        return False

    def is_cancel_checkout_action_available(self):
        return False

    def is_download_copy_action_available(self):
        return self.context.has_file()

    def is_attach_to_email_action_available(self):
        return (
            is_officeconnector_attach_feature_enabled()
            and self.context.has_file())

    def is_oneoffixx_retry_action_available(self):
        return False

    def is_docugate_retry_action_available(self):
        return False

    def is_open_as_pdf_action_available(self):
        if not is_bumblebee_feature_enabled():
            return False

        if not self.context.has_file():
            return False

        mime_type_item = self.context.get_mimetype()
        if not mime_type_item:
            return False

        return is_mimetype_supported(mime_type_item[0])

    def is_revert_to_version_action_available(self):
        return False

    def is_trash_context_action_available(self):
        trasher = ITrasher(self.context)
        return (
            trasher.verify_may_trash(raise_on_violations=False)
            and not self.context.is_inside_a_template_folder()
        )

    def is_untrash_context_action_available(self):
        trasher = ITrasher(self.context)
        return trasher.verify_may_untrash(raise_on_violations=False)

    def is_new_task_from_document_available(self):
        dossier = self.context.get_parent_dossier()
        if not IDossierMarker.providedBy(dossier):
            return False
        return api.user.has_permission('opengever.task: Add task', obj=dossier)

    def is_unlock_available(self):
        lockable = ILockable(self.context)
        if not lockable.locked():
            return False
        info = lockable.lock_info()
        for lock in info:
            if can_unlock_obj(self.context, lock['type']):
                return True
        return False

    def is_delete_workspace_context_action_available(self):
        if is_workspace_feature_enabled():
            return IDeleter(self.context).is_delete_allowed()
        return False


@implementer(IFileActions)
@adapter(IDocumentSchema, Interface)
class DocumentFileActions(BaseDocumentFileActions):

    def is_versioned(self):
        version_id = self.request.get('version_id', '')

        if isinstance(version_id, basestring):
            return version_id.isdigit()

        try:
            int(version_id)
        except ValueError:
            return False
        else:
            return True

    def is_any_checkout_or_edit_available(self):
        return (
            not self.is_versioned()
            and self.context.has_file()
            and self.context.is_checkout_and_edit_available())

    def is_edit_metadata_action_available(self):
        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        return (
            super(DocumentFileActions, self).is_edit_metadata_action_available()
            and not self.is_versioned()
            and not manager.is_locked()
            and not manager.is_checked_out_by_another_user())

    def is_office_online_edit_action_available(self):
        return (is_wopi_feature_enabled()
                and self.context.is_checkout_permitted()
                and self.context.is_office_online_editable()
                and self._can_edit_with_office_online())

    def is_oc_view_action_available(self):
        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        return (
            self.context.has_file()
            and not manager.is_checked_out_by_current_user()
            and not is_restricted_workspace_and_guest(self.context)
        )

    def is_oc_direct_checkout_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and self.context.is_office_connector_editable()
                and not self.context.is_checked_out()
                and is_officeconnector_checkout_feature_enabled())

    def is_oc_direct_edit_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and self.context.is_office_connector_editable()
                and self.context.is_checked_out()
                and is_officeconnector_checkout_feature_enabled())

    def is_oc_zem_checkout_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and self.context.is_office_connector_editable()
                and not self.context.is_checked_out()
                and not is_officeconnector_checkout_feature_enabled())

    def is_oc_zem_edit_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and self.context.is_office_connector_editable()
                and self.context.is_checked_out()
                and not is_officeconnector_checkout_feature_enabled())

    def is_oc_unsupported_file_checkout_action_available(self):
        return (self.is_any_checkout_or_edit_available()
                and not self.context.is_office_connector_editable()
                and not self.context.is_checked_out())

    def is_checkin_without_comment_available(self):
        return (not self.is_versioned()
                and self.is_checkin_with_comment_available()
                and not self.context.is_locked())

    def is_checkin_with_comment_available(self):
        return (not self.is_versioned()
                and self.context.has_file()
                and self.context.is_checkin_allowed())

    def is_cancel_checkout_action_available(self):
        if not self.context.has_file():
            return False

        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        return manager.is_cancel_allowed()

    def is_download_copy_action_available(self):
        """Disable downloading copies when the document is checked out by
        another user and document doesn't have any version.
        """
        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        has_version = self.context.get_current_version_id() is not None

        return (
            super(DocumentFileActions, self).is_download_copy_action_available()
            and not (manager.is_checked_out_by_another_user() and not has_version)
            and not is_restricted_workspace_and_guest(self.context))

    def is_attach_to_email_action_available(self):
        """Disable attaching documents to email when the document is checked out by
        another user and mail doesn't have any version.
        """
        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        has_version = self.context.get_current_version_id() is not None

        return (
            super(DocumentFileActions, self).is_attach_to_email_action_available()
            and not (manager.is_checked_out_by_another_user() and not has_version)
            and not self.context.is_inside_a_template_folder()
            and not is_restricted_workspace_and_guest(self.context))

    def is_oneoffixx_retry_action_available(self):
        return self.context.is_oneoffixx_creatable()

    def is_docugate_retry_action_available(self):
        return self.context.is_docugate_creatable()

    def is_open_as_pdf_action_available(self):
        return (
            super(DocumentFileActions, self).is_open_as_pdf_action_available()
            and not is_restricted_workspace_and_guest(self.context))

    def is_revert_to_version_action_available(self):
        manager = getMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        return (self.is_versioned()
                and self.context.has_file()
                and not self.context.is_checked_out()
                and manager.is_checkout_allowed())

    def _can_edit_with_office_online(self):
        # Office Online allows collaborative editing
        # Thus a document is editable by Office Online if it's not checked out and not locked
        # or if it's collaboratively checked out.
        # If the document is trashed, then it's not editable.
        if ITrashed.providedBy(self.context):
            return False
        if self.context.checked_out_by():
            return self.context.is_collaborative_checkout()
        if self.context.is_locked():
            return False
        return True


@implementer(IFileActions)
@adapter(IWorkspaceFolder, Interface)
class WorkspaceFolderFileActions(object):
    """Define availability for actions and action sets on IWorkspaceFolder.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_trash_context_action_available(self):
        trasher = getAdapter(self.context, ITrasher)
        return trasher.verify_may_trash(raise_on_violations=False)

    def is_untrash_context_action_available(self):
        trasher = getAdapter(self.context, ITrasher)
        return trasher.verify_may_untrash(raise_on_violations=False)

    def is_delete_workspace_context_action_available(self):
        deleter = IDeleter(self.context)
        try:
            deleter.verify_may_delete()
            return True
        except Forbidden:
            return False
