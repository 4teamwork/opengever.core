from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.document.document import IDocumentSchema
from opengever.dossier.interfaces import IDossierMarker
from opengever.workspaceclient import is_workspace_client_feature_enabled
from opengever.workspaceclient.interfaces import ILinkedWorkspaces


class ReindexIsLockedByCopyToWorkspace(UpgradeStep):
    """Reindex is locked by copy to workspace.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()
        if not is_workspace_client_feature_enabled():
            return
        self.reindex()

    def reindex(self):
        query = {'object_provides': IDossierMarker.__identifier__, 'is_subdossier': False}
        linked_dossier_paths = []

        # To improve performance, we'll only reindex documents within dossiers linked to a
        # workspace.
        for dossier in self.objects(query, "Search for dossiers linked to a workspace"):
            if ILinkedWorkspaces(dossier).number_of_linked_workspaces():
                linked_dossier_paths.append('/'.join(dossier.getPhysicalPath()))

        query = {'object_provides': IDocumentSchema.__identifier__, 'path': {'query': linked_dossier_paths}}
        with NightlyIndexer(idxs=["is_locked_by_copy_to_workspace"],
                            index_in_solr_only=True) as indexer:
            for brain in self.brains(query, 'Index is_locked_by_copy_to_workspace in Solr'):
                indexer.add_by_brain(brain)
