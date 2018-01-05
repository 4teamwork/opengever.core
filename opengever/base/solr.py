from ftw.solr.contentlisting import SolrContentListing
from ftw.solr.contentlisting import SolrContentListingObject
from ftw.solr.document import SolrDocument
from opengever.base.contentlisting import OpengeverCatalogContentListingObject
from opengever.base.interfaces import IOGSolrDocument
from zope.globalrequest import getRequest
from zope.interface import implementer


@implementer(IOGSolrDocument)
class OGSolrDocument(SolrDocument):
    pass


class OGSolrContentListing(SolrContentListing):

    doc_type = OGSolrDocument


class OGSolrContentListingObject(
        SolrContentListingObject, OpengeverCatalogContentListingObject):

    def __init__(self, doc):
        super(OGSolrContentListingObject, self).__init__(doc)
        self._brain = doc
        self.request = getRequest()

    def __repr__(self):
        return '<opengever.base.solr.OGSolrContentListingObject at %s>' % (
            self.getPath())

    def CroppedDescription(self):
        if self.snippets:
            return self.snippets
        return super(OGSolrContentListingObject, self).CroppedDescription()
