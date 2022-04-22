from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyDossierCommentIndexer
from opengever.dossier.interfaces import IDossierMarker


class ReindexDossierComments(UpgradeStep):
    """Reindex dossier comments.
    """

    def __call__(self):
        self.install_upgrade_profile()

        query = {'object_provides': [IDossierMarker.__identifier__]}

        with NightlyDossierCommentIndexer(
                idxs=["SearchableText"], index_in_solr_only=True) as indexer:
            for brain in self.brains(
                    query, 'Index SearchableText for all dossiers'):
                indexer.add_by_brain(brain)
