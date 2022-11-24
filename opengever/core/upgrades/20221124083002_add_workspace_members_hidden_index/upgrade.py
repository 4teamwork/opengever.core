from ftw.upgrade import UpgradeStep
from opengever.workspace.interfaces import IWorkspace


class AddWorkspaceMembersHiddenIndex(UpgradeStep):
    """Add workspace_members_hidden index.
    """

    index_name = 'workspace_members_hidden'

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        if not self.catalog_has_index(self.index_name):
            self.catalog_add_index(self.index_name, 'BooleanIndex')

        query = {'object_provides': IWorkspace.__identifier__}
        for obj in self.objects(
                query, u'Reindex workspace_members_hidden for workspaces'):

            obj.reindexObject(idxs=[self.index_name])
