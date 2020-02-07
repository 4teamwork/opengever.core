from opengever.workspaceclient import is_workspace_client_feature_enabled
from opengever.workspaceclient.exceptions import WorkspaceClientFeatureNotEnabled
from opengever.workspaceclient.exceptions import WorkspaceURLMissing
from opengever.workspaceclient.session import WorkspaceSession
from plone import api
import os


class WorkspaceClient(object):
    """The client is used for communicating with a workspace through the
    REST API. It is instantiated for the current logged in user.
    """

    def __init__(self):
        if not is_workspace_client_feature_enabled():
            raise WorkspaceClientFeatureNotEnabled()

        if not self.workspace_url:
            raise WorkspaceURLMissing()

    @property
    def session(self):
        """We always need to invoke a new workspace-session. Otherwise it is
        possible to dispatch a reqeust with another users session.
        """
        return WorkspaceSession(self.workspace_url,
                                api.user.get_current().getId())

    @property
    def request(self):
        """Returns the request object from the current session.
        """
        return self.session.request

    @property
    def workspace_url(self):
        """Retruns the configured workspace url in the env variable.
        """
        return os.environ.get('TEAMRAUM_URL', '').strip('/')
