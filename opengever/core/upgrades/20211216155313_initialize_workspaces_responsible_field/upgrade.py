from ftw.upgrade import UpgradeStep
from opengever.workspace.workspace import IWorkspace
from opengever.workspace.workspace import IWorkspaceSchema


class InitializeWorkspacesResponsibleField(UpgradeStep):
    """Initialize workspaces responsible field.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'object_provides': IWorkspace.__identifier__}
        for workspace in self.objects(query, 'Initialize workspace resonsible'):
            IWorkspaceSchema(workspace).responsible = workspace.Creator()
            workspace.reindexObject(idxs='responsible')
