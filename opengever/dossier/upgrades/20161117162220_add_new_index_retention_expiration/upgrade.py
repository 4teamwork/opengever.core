from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker


class AddNewIndexRetentionExpiration(UpgradeStep):
    """Add new index retention_expiration.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.catalog_add_index('retention_expiration', 'DateIndex')
        self.reindex_resolved_dossiers()

    def reindex_resolved_dossiers(self):
        for obj in self.objects(
                {'object_provides': IDossierMarker.__identifier__,
                 'review_state': 'dossier-state-resolved'},
                'Enable exclude from navigation for files'):

            obj.reindexObject(idxs=['retention_expiration'])
