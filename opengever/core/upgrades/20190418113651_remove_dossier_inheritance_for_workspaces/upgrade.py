from ftw.upgrade import UpgradeStep
from opengever.workspace.interfaces import IWorkspace


class RemoveDossierInheritanceForWorkspaces(UpgradeStep):
    """Remove dossier inheritance for workspaces.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.catalog_reindex_objects({'object_provides': IWorkspace.__identifier__})
