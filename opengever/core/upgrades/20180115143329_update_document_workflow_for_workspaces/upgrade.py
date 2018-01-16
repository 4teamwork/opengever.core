from ftw.upgrade import UpgradeStep
from ftw.upgrade.helpers import update_security_for


class UpdateDocumentWorkflowForWorkspaces(UpgradeStep):
    """Update document workflow for workspaces.

    This workflow update does only update documents in workspaces.
    The reason is that a full document update is too expensive and the change
    is not relevant for non-workspace-roles.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_security_for_workspace_documents()

    def update_security_for_workspace_documents(self):
        for obj in self.workspace_documents():
            update_security_for(obj, reindex_security=True)

    def workspace_documents(self):
        workspace_root_paths = [brain.getPath() for brain in self.catalog_unrestricted_search(
            {'portal_type': 'opengever.workspace.root'})]
        if not workspace_root_paths:
            return ()

        query = {'path': workspace_root_paths,
                 'portal_type': 'opengever.document.document'}
        return self.objects(query, 'Update document workflow for workspaces.')
