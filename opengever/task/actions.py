from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.task.task import ITask
from plone import api
from zope.component import adapter


class TaskListingActions(BaseListingActions):

    def is_export_tasks_available(self):
        return True

    def is_pdf_taskslisting_available(self):
        return True


@adapter(IDossierMarker, IOpengeverBaseLayer)
class DossierTaskListingActions(TaskListingActions):

    def is_move_items_available(self):
        return self.context.is_open()


@adapter(ITask, IOpengeverBaseLayer)
class TaskContextActions(BaseContextActions):

    def is_move_item_available(self):
        return api.user.has_permission('Copy or Move', obj=self.context)
