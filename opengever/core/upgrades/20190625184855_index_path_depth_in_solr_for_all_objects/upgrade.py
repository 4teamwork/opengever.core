from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.queue import getQueue
from ftw.upgrade import UpgradeStep
from plone.dexterity.interfaces import IDexterityContent
from zope.component import getUtility


class IndexPathDepthInSolrForAllObjects(UpgradeStep):
    """Index path_depth in Solr for all DX objects.

    This upgrade step is considered deferrable. Until it's executed and
    path_depth has been indexed in Solr, any query to the @listing endpoint
    *that includes a `depth` limit* will return zero results.
    """

    deferrable = True

    def __call__(self):
        getQueue().hook()
        processor = getUtility(IIndexQueueProcessor, name='ftw.solr')
        for obj in self.objects(
                {'object_provides': IDexterityContent.__identifier__},
                'Reindex path_depth in Solr for all DX objs.'):
            processor.index(obj, ['path_depth'])
