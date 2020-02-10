from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.storage import LinkedWorkspacesStorage
from plone import api
from plone.memoize import ram
from time import time


CACHE_TIMEOUT = 24 * 60 * 60


def list_cache_key(linked_workspaces_instance):
    """Cache key builder with the current user, a timeout and an additional
    string or list to append to the key.
    """

    uid = linked_workspaces_instance.context.UID()
    linked_workspace_uids = '-'.join(linked_workspaces_instance.storage.list())
    userid = api.user.get_current().getId()
    timeout_key = str(time() // CACHE_TIMEOUT if CACHE_TIMEOUT > 0 else str(time()))
    return '-'.join(('linked_workspaces_storage', userid, uid, linked_workspace_uids,
                    str(CACHE_TIMEOUT), timeout_key))


class LinkedWorkspaces(object):
    """Manages linked workspaces for an object.
    """

    def __init__(self, context):
        self.client = WorkspaceClient()
        self.storage = LinkedWorkspacesStorage(context)
        self.context = context

    @ram.cache(lambda method, context: list_cache_key(context))
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
