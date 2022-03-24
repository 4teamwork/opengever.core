from Acquisition import aq_chain
from Acquisition import aq_inner
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.templatefolder.interfaces import ITemplateFolder
from opengever.meeting import is_meeting_feature_enabled
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.task.task import ITask
from opengever.trash.trash import ITrasher
from opengever.workspaceclient import is_linking_enabled
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from Products.Five import BrowserView
from zope.component import getAdapter


class FolderButtonsAvailabilityView(BrowserView):
    """Define availability for folder_button actions.

    Methods should return availability for one single action.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_create_task_available(self):
        is_dossier = IDossierMarker.providedBy(self.context)
        is_task = ITask.providedBy(self.context)
        may_add_task = api.user.has_permission('opengever.task: Add task',
                                               obj=self.context)
        return (is_dossier or is_task) and may_add_task

    def is_create_proposal_available(self):
        is_dossier = IDossierMarker.providedBy(self.context)
        may_add_proposal = api.user.has_permission('opengever.meeting: Add Proposal',
                                                   obj=self.context)
        return is_meeting_feature_enabled() and is_dossier and may_add_proposal

    def _is_main_dossier(self):
        if not IDossierMarker.providedBy(self.context):
            return False

        if self.context.is_subdossier():
            return False

        return True

    def _is_dossier(self):
        return IDossierMarker.providedBy(self.context)

    def _is_open_dossier(self):
        if not self._is_dossier():
            return False

        return self.context.is_open()

    def _is_template_area(self):
        for obj in [self.context] + aq_chain(aq_inner(self.context)):
            if ITemplateFolder.providedBy(obj):
                return True
        return False

    def _is_repository_folder(self):
        return IRepositoryFolder.providedBy(self.context)

    def _is_repository_root(self):
        return IRepositoryRoot.providedBy(self.context)

    def _can_modify_dossier(self):
        return api.user.has_permission(
            'Modify portal content', obj=self.context)

    def _can_add_content_to_dossier(self):
        return api.user.has_permission(
            'Add portal content', obj=self.context)

    def _can_unlink_workspace(self):
        return api.user.has_permission(
            'opengever.workspaceclient: Unlink Workspace', obj=self.context)

    def _can_use_workspace_client(self):
        return (is_workspace_client_feature_available()
                and api.user.has_permission('opengever.workspaceclient: '
                                            'Use Workspace Client'))

    def _is_linking_enabled(self):
        return is_linking_enabled()

    def _can_copy_between_workspace_and_dossier(self):
        """Only if the workspace_client_feature is enabled and
        the main dossier is open with linked workspaces.
        """
        if not self._is_open_dossier():
            return False

        if not self._can_use_workspace_client():
            return False

        linked_workspaces_manager = ILinkedWorkspaces(self.context.get_main_dossier())
        return linked_workspaces_manager.has_linked_workspaces()

    def is_list_workspaces_available(self):
        return self._is_main_dossier() and self._can_use_workspace_client()

    def is_copy_documents_to_workspace_available(self):
        return (
            self._can_copy_between_workspace_and_dossier()
            and self._can_modify_dossier()
        )

    def is_copy_documents_from_workspace_available(self):
        return (
            self._is_main_dossier()
            and self._can_copy_between_workspace_and_dossier()
            and self._can_add_content_to_dossier()
        )

    def is_create_linked_workspace_available(self):
        return (self._is_main_dossier()
                and self._is_open_dossier()
                and self._can_use_workspace_client()
                and self._can_modify_dossier())

    def is_link_to_workspace_available(self):
        return (self._is_main_dossier()
                and self._is_open_dossier()
                and self._can_use_workspace_client()
                and self._is_linking_enabled()
                and self._can_modify_dossier())

    def is_unlink_workspace_available(self):
        return (self._is_main_dossier()
                and self._can_unlink_workspace()
                and self._has_linked_workspaces())

    def is_move_items_available(self):
        if self._is_dossier() and not self._is_open_dossier():
            return False
        return True

    def is_send_as_email_available(self):
        return not self._is_template_area()

    def is_trash_available(self):
        """Trash action should only be shown on dossier level, as we otherwise
        don't know whether the documents can be trashed (they could be in an
        inactive or resolved dossier).
        The action also does not need to be available on trashed contents.
        """
        trasher = getAdapter(self.context, ITrasher)
        if trasher.is_trashed():
            return False
        return (not self._is_repository_folder()
                and not self._is_repository_root()
                and not self._is_template_area())

    def is_untrash_available(self):
        """Untrash action should only be shown on dossier level, as we otherwise
        don't know whether the documents can be untrashed (they could be in an
        inactive or resolved dossier).
        Also untrashing content in a trashed container is not allowed.
        """
        trasher = getAdapter(self.context, ITrasher)
        if trasher.is_trashed():
            return False
        return (not self._is_repository_folder()
                and not self._is_repository_root()
                and not self._is_template_area())

    def is_folder_delete_available(self):
        return not self._is_repository_folder()

    def is_attach_documents_available(self):
        return not self._is_template_area()

    def _has_linked_workspaces(self):
        if not self._can_use_workspace_client():
            return False

        linked_workspaces_manager = ILinkedWorkspaces(self.context.get_main_dossier())
        return linked_workspaces_manager.has_linked_workspaces()
