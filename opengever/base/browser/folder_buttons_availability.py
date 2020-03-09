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

    def _can_copy_between_workspace_and_dossier(self):
        """Only if the workspace_client_feature is enabled and
        the context is a main dossier with linked workspaces.
        """
        if not IDossierMarker.providedBy(self.context):
            return False

        if not is_workspace_client_feature_available():
            return False

        if self.context.is_subdossier():
            return False

        linked_workspaces_manager = ILinkedWorkspaces(self.context.get_main_dossier())
        return linked_workspaces_manager.has_linked_workspaces()

    def is_copy_documents_to_workspace_available(self):
        return self._can_copy_between_workspace_and_dossier()

    def is_copy_documents_from_workspace_available(self):
        return self._can_copy_between_workspace_and_dossier()
