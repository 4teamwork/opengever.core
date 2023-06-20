from ftw.solr.interfaces import ISolrSearch
from opengever.base.solr.contentlisting import OGSolrContentListing  # noqa
from opengever.base.solr.contentlisting import OGSolrContentListingObject  # noqa
from opengever.base.solr.contentlisting import OGSolrDocument
from zope.component import getUtility


def solr_doc_from_uuid(uuid, fields):
    solr = getUtility(ISolrSearch)
    resp = solr.search(filters=("UID:{}".format(uuid)), fl=fields)
    if not resp.docs:
        return None
    return OGSolrDocument(resp.docs[0])


def batched_solr_results(**kwargs):
    """Returns all Solr results in batches.
    """
    solr = getUtility(ISolrSearch)
    last_batch = False
    start = 0
    rows = kwargs.get('rows', 1000)
    while not last_batch:
        resp = solr.search(start=start, **kwargs)
        yield resp.docs
        if start + len(resp.docs) >= resp.num_found or not resp.docs:
            last_batch = True
        start += rows
