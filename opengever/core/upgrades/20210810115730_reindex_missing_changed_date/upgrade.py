from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrIndexHandler
from ftw.solr.interfaces import ISolrSearch
from ftw.upgrade import UpgradeStep
from opengever.base.utils import unrestrictedUuidToObject
from zope.component import getMultiAdapter
from zope.component import getUtility
import logging


log = logging.getLogger('ftw.upgrade')


class ReindexMissingChangedDate(UpgradeStep):
    """Reindex missing changed date.
    """

    deferrable = True

    def __call__(self):
        solr = getUtility(ISolrSearch)
        manager = getUtility(ISolrConnectionManager)
        solr_connection = manager.connection

        filters = ["-changed:[* TO *]"]

        nrows = solr.unrestricted_search(filters=filters, fl=["UID"], rows=0).num_found
        results = solr.unrestricted_search(filters=filters, fl=["UID"], rows=nrows)

        for index, doc in enumerate(results.docs, 1):

            obj = unrestrictedUuidToObject(doc['UID'])
            if not obj:
                continue

            handler = getMultiAdapter((obj, manager), ISolrIndexHandler)
            handler.add(['changed'])

            if index % 1000 == 0:
                log.info("Committing items {}/{} to Solr.".format(index, results.num_found))
                solr_connection.commit()
