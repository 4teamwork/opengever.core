from opengever.workspaceclient.interfaces import IWorkspaceClientSettings
from plone import api
import logging

logger = logging.getLogger('opengever.workspaceclient')


def is_workspace_client_feature_enabled():
    return api.portal.get_registry_record(
        'is_feature_enabled', IWorkspaceClientSettings, False)


def is_workspace_client_feature_available():
    """The feature is available if:

    - the feature-flag is set to True
    - the logged in user is not the zopemaster
    """
    def is_zopemaster():
        if api.user.get_current().getId() == 'zopemaster':
            # ftw.tokenauth does not work with zope root users.
            # https://github.com/4teamwork/ftw.tokenauth/blob/master/ftw/tokenauth/pas/plugin.py#L255
            logger.warning(
                "The 'zopemaster' is not supported to make requests to the "
                "remote system. Please use another user.")
            return True
        return False

    return is_workspace_client_feature_enabled() and not is_zopemaster()
