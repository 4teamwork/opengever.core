from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository.interfaces import IRepositoryFolder


class AddABooleanIndexForBlockedLocalRoles(UpgradeStep):
    """Add BooleanIndex for blocked local roles (index only).
    """

    # An upgradestep which only adds the blocked_local_roles index, if the
    # index is not already existing. This allows us to register the
    # blocked_local_roles reindexing as an deferrable upgradestep.

    def __call__(self):
        if not self.catalog_has_index('blocked_local_roles'):
            self.catalog_add_index('blocked_local_roles', 'BooleanIndex')
