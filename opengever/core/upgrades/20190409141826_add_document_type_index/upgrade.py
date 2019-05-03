from collective.indexing.interfaces import IIndexQueueProcessor
from collective.indexing.queue import getQueue
from ftw.upgrade import UpgradeStep
from opengever.document.behaviors import IBaseDocument
from plone import api
from zope.component import getUtility


class AddDocumentTypeIndex(UpgradeStep):
    """Add document_type index.
    """

    deferrable = True

    def __call__(self):
        getQueue().hook()
        processor = getUtility(IIndexQueueProcessor, name='ftw.solr')
        catalog = api.portal.get_tool('portal_catalog')

        if not self.catalog_has_index('document_type'):
            self.catalog_add_index('document_type', 'FieldIndex')

        query = {
            'object_provides': IBaseDocument.__identifier__,
            }

        for obj in self.objects(query, "Index document type."):
            catalog.reindexObject(obj, idxs=['document_type'],
                                  update_metadata=False)
            processor.index(obj, ['document_type'])
