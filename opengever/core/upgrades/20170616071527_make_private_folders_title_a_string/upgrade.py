from ftw.upgrade import UpgradeStep
from opengever.private.folder import IPrivateFolder


class MakePrivateFoldersTitleAString(UpgradeStep):
    """Make PrivateFolders Title a string.
    """

    def __call__(self):
        self.install_upgrade_profile()

        query = {'object_provides': IPrivateFolder.__identifier__}
        for obj in self.objects(query, 'Reindex PrivateFolders title'):
            obj.reindexObject(idxs=['Title', 'sortable_title'])
