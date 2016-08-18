from plone import api
from Products.CMFEditions.utilities import dereference


class Archeologist(object):
    """Dig up a mutable, archived version of an object.
    Warning: Returned object may be incomplete!

    Parameters:
    obj - the current plone object for which you want to access the archived
          object
    version_data - a VersionData instance as returned by `portal_repository`

    The layers of abstraction that are involved (in order of appearance):

    CopyModifyMergeRepositoryTool - `portal_repository`:
    Stores versions in `portal_archivist`. Data is associated with an object
    based on a `history_id` (provided by `portal_historyidhandler`) and a
    `selector` for the version (an auto-incremented version_id).

    ArchivistTool - `portal_archivist`:
    Stores versions in `portal_historiesstorage` based on the `history_id`
    and `selector` provided by `portal_repository`.

    ZVCStorageTool - `portal_historiesstorage`:
    Stores versions in a ZopeRepository, based on a different history_id and
    selector. Maintains a mapping between these two different sets of
    identifiers.

    ZopeRepository:
    Actually stores data in ZopeVersionHistory (contains the history for each
    versioned object) and ZopeVersion (contains the archived version of an
    object).

    """
    def __init__(self, obj, version_data):
        self.obj, self.history_id = dereference(obj)
        self.selector = version_data.version_id
        self.version_data = version_data
        self.storage = api.portal.get_tool('portal_historiesstorage')

    def excavate(self):
        """Return a reference to the archived object.

        Bypass all the copies made by the different layers of abstraction and
        dig up a reference to the archived object.

        Warning: objects returned by excavate may be incomplete and may
        not contain all their attributes/references. Use at your own risk.

        """
        # the following comment and code is based on ZVCStorageTool.purge:
        #
        # digging into ZVC internals:
        # Get a reference to the version stored in the ZVC history storage
        #
        # ZVCs ``getVersionOfResource`` is quite more complex. But as we
        # do not use labeling and branches it is not a problem to get the
        # version in the following simple way.
        zvc_repo = self.storage._getZVCRepo()
        zvc_histid, zvc_selector = self.storage._getZVCAccessInfo(
            self.history_id, self.selector, countPurged=True)

        zvc_history = zvc_repo.getVersionHistory(zvc_histid)
        version = zvc_history.getVersionById(zvc_selector)
        archived_obj = version._data._object.object
        return archived_obj
