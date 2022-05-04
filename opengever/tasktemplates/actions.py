from opengever.base.context_actions import BaseContextActions
from plone import api


class TaskTemplateContextActions(BaseContextActions):

    def is_delete_available(self):
        return api.user.has_permission('Delete objects', obj=self.context)
