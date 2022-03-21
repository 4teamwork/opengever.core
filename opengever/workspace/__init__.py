from opengever.workspace.interfaces import IToDoSettings
from opengever.workspace.interfaces import IWorkspaceMeetingSettings
from plone import api
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('opengever.workspace')

WHITELISTED_TEAMRAUM_GLOBAL_SOURCES = set()


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
