from interfaces import IWorkspaceSettings
from plone import api
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.workspace')


def is_workspace_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', interface=IWorkspaceSettings)
