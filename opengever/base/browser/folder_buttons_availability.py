from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.task.task import ITask
from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from plone import api
from Products.Five import BrowserView


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

    def _is_main_dossier(self):
        if not IDossierMarker.providedBy(self.context):
            return False

        if self.context.is_subdossier():
            return False

        return True

    def _can_use_workspace_client(self):
        return (is_workspace_client_feature_available()
                and api.user.has_permission('opengever.workspaceclient: '
                                            'Use Workspace Client'))

    def _can_copy_between_workspace_and_dossier(self):
        """Only if the workspace_client_feature is enabled and
        the context is a main dossier with linked workspaces.
        """
        if not self._is_main_dossier():
            return False

        if not self._can_use_workspace_client():
            return False

        linked_workspaces_manager = ILinkedWorkspaces(self.context.get_main_dossier())
        return linked_workspaces_manager.has_linked_workspaces()

    def is_list_workspaces_available(self):
        return self._is_main_dossier() and self._can_use_workspace_client()

    def is_copy_documents_to_workspace_available(self):
        return self._can_copy_between_workspace_and_dossier()

    def is_copy_documents_from_workspace_available(self):
        return self._can_copy_between_workspace_and_dossier()
