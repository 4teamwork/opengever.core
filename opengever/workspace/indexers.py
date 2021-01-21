from opengever.workspace.workspace import IWorkspaceSchema
from opengever.workspace.interfaces import IWorkspaceMeeting
from plone.indexer import indexer


@indexer(IWorkspaceSchema)
def external_reference(obj):
    if obj.external_reference:
        return obj.external_reference
    return ''


@indexer(IWorkspaceMeeting)
def participations(obj):
    return obj.participants
