from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrIndexHandler
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from plone.dexterity.interfaces import IDexterityContent
from zope.component import getMultiAdapter
from zope.component import getUtility


class IndexIsFolderishSolrIndex(UpgradeStep):
    """Index is folderish solr index.
    """

    deferrable = True

    def __call__(self):
        self.index_is_folderish()

    def index_is_folderish(self):
        manager = getUtility(ISolrConnectionManager)
        contents = self.catalog_unrestricted_search({
            'object_provides': IDexterityContent.__identifier__,
        })
        for content in ProgressLogger('Index is_folderish in Solr', contents):
            handler = getMultiAdapter((content, manager), ISolrIndexHandler)
            handler.add(['is_folderish'])
        manager.connection.commit(soft_commit=False, after_commit=False)
