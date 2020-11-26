from opengever.workspace.workspace import IWorkspaceSchema
from plone.indexer import indexer


@indexer(IWorkspaceSchema)
def external_reference(obj):
    if obj.external_reference:
        return obj.external_reference
    return ''
