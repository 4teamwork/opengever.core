from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyLocalRolesLookupUpdater


class ReindexLocalRolesLookupTable(UpgradeStep):
    """Reindex local roles lookup table.
    """

    def __call__(self):
        query = {'portal_type': [
            'opengever.dossier.businesscasedossier',
            'opengever.repository.repositoryfolder',
            'opengever.repository.repositoryroot',
            'opengever.workspace.folder',
            'opengever.workspace.workspace',
        ]}

        with NightlyLocalRolesLookupUpdater() as local_roles_modification_updater:
            for brain in self.brains(query, 'Queueing local roles lookup jobs'):
                local_roles_modification_updater.add_by_brain(brain)
