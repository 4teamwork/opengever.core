from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker


class AddDossierTypeIndex(UpgradeStep):
    """Add dossier type index.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        query = {'object_provides': [
            IDossierMarker.__identifier__,
            IDossierTemplateMarker.__identifier__,
        ]}

        with NightlyIndexer(idxs=["dossier_type"],
                            index_in_solr_only=True) as indexer:
            for brain in self.brains(query, 'Index dossier_type in Solr'):
                indexer.add_by_brain(brain)
