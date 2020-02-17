from opengever.workspaceclient import is_workspace_client_feature_available
from opengever.workspaceclient.exceptions import WorkspaceClientFeatureNotEnabled
from opengever.workspaceclient.exceptions import WorkspaceURLMissing
from opengever.workspaceclient.session import WorkspaceSession
from plone import api
from zExceptions import Unauthorized
import os


class WorkspaceClient(object):
    """The client is used for communicating with a workspace through the
    REST API. It is instantiated for the current logged in user.
    """

    def __init__(self):
        if not is_workspace_client_feature_available():
            raise WorkspaceClientFeatureNotEnabled()

        if not self.workspace_url:
            raise WorkspaceURLMissing()

    @property
    def session(self):
        """We always need to invoke a new workspace-session. Otherwise it is
        possible to dispatch a request with another users session.
        """
        if not api.user.has_permission('opengever.workspaceclient: Use Workspace Client'):
            raise Unauthorized("User does not have permission to use the WorkspaceClient")
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

    def search(self, url_or_path='', **kwargs):
        """Dispatches a search request to the given url or path.
        """
        url_or_path = '{}/@search'.format(url_or_path.strip('/'))
        return self.request.get(url_or_path, params=kwargs).json()

    def get(self, url_or_path):
        """Proxy method to perform a get request.
        """
        return self.request.get(url_or_path).json()

    def post(self, url_or_path, *args, **kwargs):
        """Proxy method to perform a post request.
        """
        return self.request.post(url_or_path, *args, **kwargs).json()

    def patch(self, url_or_path, *args, **kwargs):
        """Proxy method to perform a patch request.
        """
        return self.request.patch(url_or_path, *args, **kwargs).json()

    def create_workspace(self, **data):
        """Crates a new workspace and returns the serialization of the new
        workspace
        """
        payload = data
        payload.update({
            '@type': 'opengever.workspace.workspace'
        })

        return self.request.post('/workspaces', json=payload).json()

    def lookup_url_by_uid(self, uid):
        """Searches on the remote system for an object having the given UID and
        returns the URL to this object.

        If no object is found with the given UID, it returns None.
        """
        items = self.search(UID=uid).get('items')

        if len(items) > 1:
            raise LookupError("Found multiple workspaces with the same UID")

        return items[0].get('@id') if items else None
