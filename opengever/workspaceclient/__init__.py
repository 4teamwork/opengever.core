from opengever.workspaceclient.interfaces import IWorkspaceClientSettings
from plone import api
import logging

logger = logging.getLogger('opengever.workspaceclient')


def is_workspace_client_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', IWorkspaceClientSettings, False)
