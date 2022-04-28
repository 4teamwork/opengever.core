from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.inbox.inbox import IInbox
from opengever.meeting import is_meeting_feature_enabled
from opengever.private.dossier import IPrivateDossier
from opengever.private.folder import IPrivateFolder
from opengever.trash.trash import ITrasher
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from zope.component import adapter


class BaseDocumentListingActions(BaseListingActions):

    def is_attach_documents_available(self):
        return True

    def is_copy_items_available(self):
        return True

    def is_delete_available(self):
        return api.user.has_permission('Delete objects', obj=self.context)

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

    def is_delete_available(self):
        return False
