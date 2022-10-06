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

    def get_actions(self):
        super(TaskContextActions, self).get_actions()
        self.maybe_add_edit_description_action()
        self.maybe_add_edit_related_items_action()
        return self.actions

    def maybe_add_edit_description_action(self):
        if not self.context.is_editable:
            return False
        if api.user.has_permission('Modify portal content', obj=self.context):
            self.add_action(u'edit description')

    def maybe_add_edit_related_items_action(self):
        if not self.context.is_editable:
            return False
        if api.user.has_permission('Modify portal content', obj=self.context):
            self.add_action(u'edit relatedItems')

    def is_move_item_available(self):
        return api.user.has_permission('Copy or Move', obj=self.context)

    def is_edit_available(self):
        is_locked_for_current_user = self.context.restrictedTraverse(
            '@@plone_lock_info').is_locked_for_current_user()
        has_modify_permission = api.user.has_permission(
            'opengever.task: Edit task', obj=self.context)
        return has_modify_permission and not is_locked_for_current_user
