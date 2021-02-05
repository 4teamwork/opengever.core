from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrIndexHandler
from ftw.upgrade import UpgradeStep
from plone.dexterity.interfaces import IDexterityContent
from zope.component import getMultiAdapter
from zope.component import getUtility


class AddSortableReferenceNumberIndex(UpgradeStep):
    """Add sortable reference number index.
    """

    deferrable = True

    def __call__(self):
        self.index_sortable_reference_number()

    def index_sortable_reference_number(self):
        manager = getUtility(ISolrConnectionManager)
        query = {'object_provides': IDexterityContent.__identifier__}
        for obj in self.objects(query, 'Index sortable_reference in Solr'):
            handler = getMultiAdapter((obj, manager), ISolrIndexHandler)
            handler.add(['sortable_reference'])
        manager.connection.commit(soft_commit=False, extract_after_commit=False)
