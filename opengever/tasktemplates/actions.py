from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from plone import api
from zope.component import adapter


@adapter(ITaskTemplate, IOpengeverBaseLayer)
class TaskTemplateContextActions(BaseContextActions):

    def is_delete_available(self):
        return api.user.has_permission('Delete objects', obj=self.context)


@adapter(ITaskTemplateFolderSchema, IOpengeverBaseLayer)
class TaskTemplateFolderContextActions(BaseContextActions):

    def is_delete_available(self):
        return api.user.has_permission('Delete objects', obj=self.context)

    def is_move_item_available(self):
        return api.user.has_permission('Copy or Move', obj=self.context)
