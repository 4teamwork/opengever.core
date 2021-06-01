from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrIndexHandler
from ftw.upgrade import UpgradeStep
from ftw.upgrade.progresslogger import ProgressLogger
from ftw.upgrade.utils import SavepointIterator
from opengever.base.interfaces import IReferenceNumber
from plone.dexterity.interfaces import IDexterityContent
from zope.component import getMultiAdapter
from zope.component import getUtility


class UpdateReindexReferenceAndSortableReferenceIndex(UpgradeStep):
    """Update/reindex reference and sortable_reference index.
    """

    deferrable = True

    def __call__(self):
        self.index_sortable_reference_number()

    def index_sortable_reference_number(self):
        manager = getUtility(ISolrConnectionManager)
        brains = self.catalog_unrestricted_search(
            {'object_provides': IDexterityContent.__identifier__})
        iterator = SavepointIterator.build(brains)
        message = 'Reindex reference and sortable_reference in Solr'
        for brain in ProgressLogger(message, iterator):
            # update catalog but only if necessary
            obj = self.catalog_unrestricted_get_object(brain)
            if IReferenceNumber(obj).get_number() != brain.reference:
                obj.reindexObject(idxs=['reference'])

            # update solr
            handler = getMultiAdapter((obj, manager), ISolrIndexHandler)
            handler.add(['reference', 'sortable_reference'])

        manager.connection.commit(soft_commit=False, extract_after_commit=False)
