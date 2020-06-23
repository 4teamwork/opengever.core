from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from plone.indexer import indexer


@indexer(ITaskTemplate)
def period(obj):
    return obj.deadline
