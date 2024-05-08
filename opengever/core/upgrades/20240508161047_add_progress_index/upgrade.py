from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.dossier import is_dossier_checklist_feature_enabled
from opengever.dossier.behaviors.dossier import IDossierMarker


class AddProgressIndex(UpgradeStep):
    """Add progress index.
    """

    deferrable = True

    def __call__(self):
        if not is_dossier_checklist_feature_enabled():
            return

        query = {'object_provides': [
            IDossierMarker.__identifier__,
        ]}

        with NightlyIndexer(idxs=["progress"],
                            index_in_solr_only=True) as indexer:
            for obj in self.objects(query, 'Index progress in Solr'):
                indexer.add_by_obj(obj)
