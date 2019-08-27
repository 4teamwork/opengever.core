from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.queue import getQueue
from ftw.upgrade import UpgradeStep
from opengever.task.task import ITask
from plone import api
from zope.component import getUtility


INDEX_NAME = 'is_subtask'


class ReplaceIsSubtaskFieldIndexWithABooleanIndex(UpgradeStep):
    """Replace is subtask field index with a boolean index.
    """

    deferrable = True

    def __call__(self):
        getQueue().hook()
        processor = getUtility(IIndexQueueProcessor, name='ftw.solr')
        query = {'object_provides': ITask.__identifier__}
        catalog = api.portal.get_tool('portal_catalog')

        index = self.portal.portal_catalog.Indexes.get(INDEX_NAME)
        if index.__class__.__name__ != 'BooleanIndex':
            self.catalog_remove_index(INDEX_NAME)
            self.catalog_add_index(INDEX_NAME, 'BooleanIndex')
            for obj in self.objects(query, 'Reindex is_subtask'):
                catalog.reindexObject(obj, idxs=[INDEX_NAME],
                                      update_metadata=False)
                processor.index(obj, [INDEX_NAME])
