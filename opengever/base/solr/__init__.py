from ftw.solr.interfaces import ISolrSearch
from opengever.base.solr.contentlisting import OGSolrContentListing  # noqa
from opengever.base.solr.contentlisting import OGSolrContentListingObject  # noqa
from opengever.base.solr.contentlisting import OGSolrDocument
from zope.component import getUtility


def solr_doc_from_uuid(uuid):
    solr = getUtility(ISolrSearch)
    resp = solr.search(filters=("UID:{}".format(uuid)))
    if not resp.docs:
        return None
    return OGSolrDocument(resp.docs[0])
