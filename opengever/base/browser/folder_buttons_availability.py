from Products.Five import BrowserView
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone import api
from opengever.task.task import ITask


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
