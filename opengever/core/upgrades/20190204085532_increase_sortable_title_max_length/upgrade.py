from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.queue import getQueue
from ftw.upgrade import UpgradeStep
from plone.dexterity.interfaces import IDexterityContent
from plone import api
from zope.component import getUtility


class InccreaseSortableTitleMaxLength(UpgradeStep):
    """Increase maximal length of sortable title.
    """

    deferrable = True

    def __call__(self):
        getQueue().hook()
        processor = getUtility(IIndexQueueProcessor, name='ftw.solr')
        catalog = api.portal.get_tool('portal_catalog')
        for obj in self.objects({'object_provides': IDexterityContent.__identifier__},
                                "Reindex sortable title."):
            catalog.reindexObject(obj, idxs=['sortable_title'],
                                  update_metadata=False)
            processor.index(obj, ['sortable_title'])
