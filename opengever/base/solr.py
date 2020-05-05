from ftw.solr.contentlisting import SolrContentListing
from ftw.solr.contentlisting import SolrContentListingObject
from ftw.solr.document import SolrDocument
from opengever.base.contentlisting import OpengeverCatalogContentListingObject
from opengever.base.interfaces import IOGSolrDocument
from zope.globalrequest import getRequest
from zope.interface import implementer


@implementer(IOGSolrDocument)
class OGSolrDocument(SolrDocument):

    @property
    def bumblebee_checksum(self):
        return self.get('bumblebee_checksum', None)

    @property
    def containing_dossier(self):
        return self.get('containing_dossier', None)

    @property
    def filename(self):
        return self.get('filename', None)

    @property
    def is_subdossier(self):
        return self.get('is_subdossier', None)

    @property
    def is_leafnode(self):
        if self.get('portal_type') == 'opengever.repository.repositoryfolder':
            return not self.get('has_sametype_children')
        return None


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
