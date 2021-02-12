from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.bumblebee.mimetypes import is_mimetype_supported
from opengever.api.lock import can_unlock_obj
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document.behaviors import IBaseDocument
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IFileActions
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from opengever.trash.trash import ITrashable
from opengever.wopi import is_wopi_feature_enabled
from opengever.wopi.lock import get_lock_token
from plone import api
from plone.locking.interfaces import ILockable
from zope.component import adapter
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

    def is_trash_document_available(self):
        trasher = ITrashable(self.context)
        return (
            trasher.verify_may_trash(raise_on_violations=False)
            and not self.context.is_inside_a_template_folder()
            )

    def is_untrash_document_available(self):
        trasher = ITrashable(self.context)
        return trasher.verify_may_untrash(raise_on_violations=False)

    def is_new_task_from_document_available(self):
        parent = aq_parent(aq_inner(self.context))
        is_inside_dossier = IDossierMarker.providedBy(parent)
        may_add_task = api.user.has_permission('opengever.task: Add task', obj=parent)
        return is_inside_dossier and may_add_task

    def is_unlock_available(self):
        lockable = ILockable(self.context)
        if not lockable.locked():
            return False
        info = lockable.lock_info()
        for lock in info:
            if can_unlock_obj(self.context, lock['type']):
                return True
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
            and not (manager.is_checked_out_by_another_user() and not has_version))

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
            and not self.context.is_inside_a_template_folder())

    def is_oneoffixx_retry_action_available(self):
        return self.context.is_oneoffixx_creatable()

    def is_docugate_retry_action_available(self):
        return self.context.is_docugate_creatable()

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
        # or if it's checked out by Office Online.
        if self.context.checked_out_by():
            if get_lock_token(self.context):
                return True
            else:
                return False
        if self.context.is_locked():
            return False
        return True
