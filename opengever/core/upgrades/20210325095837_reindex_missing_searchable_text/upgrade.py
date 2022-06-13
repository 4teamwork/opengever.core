from ftw.solr.interfaces import ISolrSearch
from ftw.upgrade import UpgradeStep
from opengever.base.utils import unrestrictedUuidToObject
from zope.component import getUtility
import logging


logger = logging.getLogger('ftw.upgrade')


class ReindexMissingSearchableText(UpgradeStep):
    """Reindex documents with missing searchable text.

    Indexing of the SearchableText of documents in solr would sometimes fail
    because the blob had been updated by the doc properties updater in the
    meantime. This leads to missing SearchableText. Here we find and reindex
    such documents.
    """

    deferrable = True

    def __call__(self):
        solr = getUtility(ISolrSearch)
        resp = solr.search(
            filters=['-SearchableText:*',
                     'object_provides:opengever.document.behaviors.IBaseDocument'],
            fl=["UID", "SearchableText"],
            rows=1000000)

        n_tot = len(resp.docs)
        logger.info('Reindexing {} documents.'.format(n_tot))

        for i, doc in enumerate(resp.docs):
            if i % 20 == 0:
                logger.info('Done {}/{}'.format(i, n_tot))

            if "SearchableText" in doc:
                continue

            obj = unrestrictedUuidToObject(doc['UID'])
            if not obj:
                continue
            obj.reindexObject(idxs=["UID", "SearchableText"])
