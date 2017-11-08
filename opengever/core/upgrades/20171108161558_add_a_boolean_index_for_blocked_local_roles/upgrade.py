from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository.interfaces import IRepositoryFolder


class AddABooleanIndexForBlockedLocalRoles(UpgradeStep):
    """Add BooleanIndex for blocked local roles.
    """

    def __call__(self):
        self.catalog_add_index('blocked_local_roles', 'BooleanIndex')
        self.index_blocked_local_roles_in_repository_folders()
        self.index_blocked_local_roles_in_dossiers()

    def index_blocked_local_roles_in_repository_folders(self):
        query = {
            'object_provides': IRepositoryFolder.__identifier__,
            }

        for container in self.objects(
                query, 'Index blocked local roles in repository folders'):

            container.reindexObject(idxs=['blocked_local_roles'])

    def index_blocked_local_roles_in_dossiers(self):
        query = {
            'object_provides': IDossierMarker.__identifier__,
            }

        for container in self.objects(
                query, 'Index blocked local roles in dossiers'):

            container.reindexObject(idxs=['blocked_local_roles'])
