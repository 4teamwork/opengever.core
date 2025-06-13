from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.document.behaviors import IBaseDocument


class AddDocumentVersionCountIndex(UpgradeStep):
    """Add document version count index.
    """

    def __call__(self):
        query = {'object_provides': [
            IBaseDocument.__identifier__,
        ]}

        with NightlyIndexer(idxs=["document_version_count"],
                            index_in_solr_only=True) as indexer:
            for brain in self.brains(query, 'Index document version count in Solr'):
                indexer.add_by_brain(brain)
