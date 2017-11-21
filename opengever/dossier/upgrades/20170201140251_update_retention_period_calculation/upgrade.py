from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossierMarker


class UpdateRetentionPeriodCalculation(UpgradeStep):
    """Update retention period calculation.
    """

    def __call__(self):
        pass
        # Moved to 20170411113233@opengever.base:default
        # self.reindex_resolved_dossiers()

    def reindex_resolved_dossiers(self):
        for obj in self.objects(
                {'object_provides': IDossierMarker.__identifier__,
                 'review_state': 'dossier-state-resolved'},
                'Calculate retention expiration for resolved dossiers'):

            obj.reindexObject(idxs=['retention_expiration'])
