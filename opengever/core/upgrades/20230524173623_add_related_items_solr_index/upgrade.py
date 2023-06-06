from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.document import IDocumentSchema
from opengever.task.task import ITask


class AddRelatedItemsSolrIndex(UpgradeStep):
    """Add related items solr index.
    """

    deferrable = True

    def __call__(self):
        query_tasks = {'object_provides': ITask.__identifier__}
        query_docs = {'object_provides': IDocumentSchema.__identifier__}

        with NightlyIndexer(idxs=["related_items"],
                            index_in_solr_only=True) as indexer:
            for obj in self.objects(query_tasks, 'Index related_items in Solr for tasks'):
                if ITask(obj).relatedItems:
                    indexer.add_by_obj(obj)

            for obj in self.objects(query_docs, 'Index related_items in Solr for documents'):
                if IRelatedDocuments(obj).relatedItems:
                    indexer.add_by_obj(obj)
