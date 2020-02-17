from persistent.list import PersistentList
from zope.annotation import IAnnotations


class LinkedWorkspacesStorage(object):
    """Storage for remote workspaces.
    """

    ANNOTATIONS_KEY = 'opengever.workspaceclient.linked_workspaces'

    def __init__(self, context):
        self.context = context
        self._initialize_storage()

    def __contains__(self, item):
        return item in self._storage

    def add(self, uid):
        """Add a workspace by its UID.
        """
        self._storage.append(uid)

    def list(self):
        """Returns the stored linked workspace UID's
        """
        return list(self._storage)

    def _initialize_storage(self):
        ann = IAnnotations(self.context)
        if self.ANNOTATIONS_KEY not in ann:
            ann[self.ANNOTATIONS_KEY] = PersistentList()

        self._storage = ann[self.ANNOTATIONS_KEY]
