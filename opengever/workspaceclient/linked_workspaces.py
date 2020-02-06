from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.storage import LinkedWorkspacesStorage


class LinkedWorkspaces(object):
    """Manages linked workspaces for an object.
    """

    def __init__(self, context):
        self.client = WorkspaceClient()
        self.storage = LinkedWorkspacesStorage(context)
        self.context = context

    def list(self):
        """Returns a JSON summary-representation of all stored workspaces.
        This function lookups all UIDs on the remote system by dispatching a
        search requests to the remote system.
        This means, unauthorized objects or not existing UIDs will be skipped
        automatically.
        """
        uids = self.storage.list()
        if not uids:
            return uids

        return self.client.search(
            UID=uids,
            portal_type="opengever.workspace.workspace").get('items')
