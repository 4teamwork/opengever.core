from opengever.workspace.interfaces import IToDoSettings
from opengever.workspace.interfaces import IWorkspaceMeetingSettings
from plone import api
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('opengever.workspace')

WHITELISTED_TEAMRAUM_GLOBAL_SOURCES = set()

WHITELISTED_TEAMRAUM_PORTAL_TYPES = {
    'ftw.mail.mail',
    'opengever.document.document',
    'opengever.workspace.folder',
    'opengever.workspace.meetingagendaitem',
    'opengever.workspace.root',
    'opengever.workspace.todo',
    'opengever.workspace.todolist',
    'opengever.workspace.workspace',
}


def is_workspace_feature_enabled():
    from opengever.workspace.interfaces import IWorkspaceSettings
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IWorkspaceSettings)


def is_workspace_meeting_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IWorkspaceMeetingSettings)


def is_todo_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IToDoSettings)
