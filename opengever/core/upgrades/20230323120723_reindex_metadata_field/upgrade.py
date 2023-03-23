from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.document.behaviors import IBaseDocument


class ReindexMetadataField(UpgradeStep):
    """Reindex metadata field.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': IBaseDocument.__identifier__}

        with NightlyIndexer(idxs=["metadata"], index_in_solr_only=True) as indexer:
            for brain in self.brains(query, 'Queueing metadata reindexing jobs.'):
                indexer.add_by_brain(brain)
