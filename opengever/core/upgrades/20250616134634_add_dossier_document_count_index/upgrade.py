from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.dossier.behaviors.dossier import IDossierMarker


class AddDossierDocumentCountIndex(UpgradeStep):
    """Add Dossier Document Coutn Index.
    """

    def __call__(self):
        query = {
            'object_provides': [IDossierMarker.__identifier__],
        }

        with NightlyIndexer(
            idxs=["document_count"],
            index_in_solr_only=True
        ) as indexer:
            for brain in self.brains(query, 'Index dossier document count in Solr'):
                indexer.add_by_brain(brain)
