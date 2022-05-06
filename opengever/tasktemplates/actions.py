from opengever.base.context_actions import BaseContextActions
from plone import api
from opengever.base.interfaces import IOpengeverBaseLayer
from zope.component import adapter
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate


@adapter(ITaskTemplate, IOpengeverBaseLayer)
class TaskTemplateContextActions(BaseContextActions):

    def is_delete_available(self):
        return api.user.has_permission('Delete objects', obj=self.context)


@adapter(ITaskTemplateFolderSchema, IOpengeverBaseLayer)
class TaskTemplateFolderContextActions(BaseContextActions):

    def is_delete_available(self):
        return api.user.has_permission('Delete objects', obj=self.context)
