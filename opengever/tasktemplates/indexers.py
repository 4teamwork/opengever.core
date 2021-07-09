from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.content.templatefoldersschema import ITaskTemplateFolderSchema
from plone.indexer import indexer


@indexer(ITaskTemplate)
def period(obj):
    return obj.deadline


@indexer(ITaskTemplateFolderSchema)
def sequence_type(obj):
    return obj.sequence_type
