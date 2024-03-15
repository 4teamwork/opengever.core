from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.bumblebee.interfaces import IBumblebeeServiceV3
from opengever.base.browser.edit_public_trial import is_edit_public_trial_status_available
from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document.behaviors import IBaseDocument
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IFileActions
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.inbox.inbox import IInbox
from opengever.meeting import is_meeting_feature_enabled
from opengever.private.dossier import IPrivateDossier
from opengever.private.folder import IPrivateFolder
from opengever.trash.trash import ITrasher
from opengever.workspace import is_workspace_feature_enabled
from opengever.workspace.utils import is_restricted_workspace_and_guest
from opengever.workspace.utils import is_within_workspace
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from zope.component import adapter
from zope.component import getMultiAdapter


class BaseDocumentListingActions(BaseListingActions):

    def is_attach_documents_available(self):
        return True

    def is_copy_items_available(self):
        return True

    def is_edit_items_available(self):
        return True

    def is_export_documents_available(self):
        return True

    def is_move_items_available(self):
        return True

    def is_trash_content_available(self):
        if not api.user.has_permission('opengever.trash: Trash content', obj=self.context):
            return False
        return not ITrasher(self.context).is_trashed()

    def is_zip_selected_available(self):
        return True

    def is_delete_available(self):
        if is_workspace_feature_enabled():
            # A workspace env provides its own delete action (is_delete_workspace_context_available)
            # for documents.
            return False
        return super(BaseDocumentListingActions, self).is_delete_available()


class RepositoryDocumentListingActions(BaseDocumentListingActions):

    def is_delete_available(self):
        return False

    def is_trash_content_available(self):
        return False


@adapter(IDossierMarker, IOpengeverBaseLayer)
class DossierDocumentListingActions(BaseDocumentListingActions):

    def is_copy_documents_to_workspace_available(self):
        if not self.context.is_open():
            return False
        if not is_workspace_client_feature_available():
            return False
        if not api.user.has_permission('Modify portal content', obj=self.context):
            return False
        if not api.user.has_permission('opengever.workspaceclient: Use Workspace Client'):
            return False

        linked_workspaces_manager = ILinkedWorkspaces(self.context.get_main_dossier())
        return linked_workspaces_manager.has_linked_workspaces()

    def is_create_task_available(self):
        return api.user.has_permission('opengever.task: Add task', obj=self.context)

    def is_create_proposal_available(self):
        return is_meeting_feature_enabled() and api.user.has_permission(
            'opengever.meeting: Add Proposal', obj=self.context)

    def is_delete_available(self):
        return False

    def is_edit_items_available(self):
        return self.context.is_open()

    def is_move_items_available(self):
        return self.context.is_open()


@adapter(IPrivateDossier, IOpengeverBaseLayer)
class PrivateDossierDocumentListingActions(BaseDocumentListingActions):
    pass


@adapter(IPrivateFolder, IOpengeverBaseLayer)
class PrivateFolderDocumentListingActions(BaseDocumentListingActions):

    def is_trash_content_available(self):
        return False


@adapter(IInbox, IOpengeverBaseLayer)
class InboxDocumentListingActions(BaseDocumentListingActions):

    def is_create_forwarding_available(self):
        return api.user.has_permission('opengever.inbox: Add Forwarding', obj=self.context)

    def is_delete_available(self):
        return False


class TemplateDocumentListingActions(BaseDocumentListingActions):

    def is_attach_documents_available(self):
        return False

    def is_trash_content_available(self):
        return False


class WorkspaceDocumentListingActions(BaseDocumentListingActions):

    def is_copy_items_available(self):
        return api.user.has_permission('Add portal content', obj=self.context)

    def is_edit_items_available(self):
        return api.user.has_permission('Modify portal content', obj=self.context)

    def is_move_items_available(self):
        return api.user.has_permission('Add portal content', obj=self.context)

    def is_delete_available(self):
        return False

    def is_attach_documents_available(self):
        return (super(WorkspaceDocumentListingActions, self).is_attach_documents_available()
                and not is_restricted_workspace_and_guest(self.context))

    def is_zip_selected_available(self):
        return (super(WorkspaceDocumentListingActions, self).is_zip_selected_available()
                and not is_restricted_workspace_and_guest(self.context))

    def is_export_documents_available(self):
        return (super(WorkspaceDocumentListingActions, self).is_export_documents_available()
                and not is_restricted_workspace_and_guest(self.context))


@adapter(IBaseDocument, IOpengeverBaseLayer)
class BaseDocumentContextActions(BaseContextActions):

    def __init__(self, context, request):
        super(BaseDocumentContextActions, self).__init__(context, request)
        self.file_actions = getMultiAdapter((self.context, self.request), IFileActions)
        self.is_trashed = ITrasher(self.context).is_trashed()

    def is_attach_to_email_available(self):
        if self.is_trashed:
            return False
        return self.file_actions.is_attach_to_email_action_available()

    def is_copy_item_available(self):
        if self.is_trashed:
            return False
        if self.context.is_checked_out():
            return False
        return api.user.has_permission('Copy or Move', obj=self.context)

    def is_create_forwarding_available(self):
        if self.is_trashed:
            return False
        return api.user.has_permission('opengever.inbox: Add Forwarding', obj=self.context)

    def is_delete_available(self):
        if is_workspace_feature_enabled():
            # A workspace env provides its own delete action (is_delete_workspace_context_available)
            # for documents.
            return False
        return super(BaseDocumentContextActions, self).is_delete_available()

    def is_delete_workspace_context_available(self):
        return self.file_actions.is_delete_workspace_context_action_available()

    def is_download_copy_available(self):
        if self.is_trashed:
            return False
        return self.file_actions.is_download_copy_action_available()

    def is_edit_available(self):
        if self.is_trashed:
            return False
        return super(BaseDocumentContextActions, self).is_edit_available()

    def is_edit_public_trial_status_available(self):
        if self.is_trashed:
            return False
        return is_edit_public_trial_status_available(self.context)

    def is_move_item_available(self):
        if self.is_trashed:
            return False
        if self.context.is_checked_out():
            return False
        if not api.user.has_permission('Copy or Move', obj=self.context):
            return False
        return self.context.is_movable()

    def is_new_task_from_document_available(self):
        if self.is_trashed:
            return False
        return self.file_actions.is_new_task_from_document_available()

    def is_open_as_pdf_available(self):
        if self.is_trashed:
            return False
        return self.file_actions.is_open_as_pdf_action_available()

    def is_revive_bumblebee_preview_available(self):
        if not is_bumblebee_feature_enabled():
            return False
        if not api.user.has_permission('opengever.bumblebee: Revive Preview', obj=self.context):
            return False
        return IBumblebeeable.providedBy(self.context)

    def is_share_content_available(self):
        return is_within_workspace(self.context)

    def is_trash_context_available(self):
        return self.file_actions.is_trash_context_action_available()

    def is_untrash_context_available(self):
        return self.file_actions.is_untrash_context_action_available()

    def is_unlock_available(self):
        return self.file_actions.is_unlock_available()


@adapter(IDocumentSchema, IOpengeverBaseLayer)
class DocumentSchemaContextActions(BaseDocumentContextActions):

    def is_cancel_checkout_available(self):
        return self.file_actions.is_cancel_checkout_action_available()

    def is_checkin_with_comment_available(self):
        return self.file_actions.is_checkin_with_comment_available()

    def is_checkin_without_comment_available(self):
        return self.file_actions.is_checkin_without_comment_available()

    def is_checkout_document_available(self):
        if self.context.digitally_available:
            manager = getMultiAdapter((self.context, self.request), ICheckinCheckoutManager)
            return manager.is_checkout_allowed()
        return False

    def is_docugate_retry_available(self):
        return self.file_actions.is_docugate_retry_action_available()

    def is_oc_direct_checkout_available(self):
        return self.file_actions.is_oc_direct_checkout_action_available()

    def is_oc_direct_edit_available(self):
        return self.file_actions.is_oc_direct_edit_action_available()

    def is_oc_view_available(self):
        return self.file_actions.is_oc_view_action_available()

    def is_office_online_edit_available(self):
        return self.file_actions.is_office_online_edit_action_available()

    def is_oneoffixx_retry_available(self):
        return self.file_actions.is_oneoffixx_retry_action_available()

    def is_save_document_as_pdf_available(self):
        if self.is_trashed:
            return False
        is_convertable = IBumblebeeServiceV3(self.request).is_convertable(self.context)
        return not self.context.is_checked_out() and is_convertable
