from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.document.document import IDocumentSchema
from opengever.task.task import ITask


class AddRelatedItemsSolrIndex(UpgradeStep):
    """Add related items solr index.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': [IDocumentSchema.__identifier__,
                                     ITask.__identifier__]}

        with NightlyIndexer(idxs=["related_items"],
                            index_in_solr_only=True) as indexer:
            for brain in self.brains(query, 'Index related_items in Solr'):
                indexer.add_by_brain(brain)
