from ftw.solr.contentlisting import SolrContentListing
from ftw.solr.contentlisting import SolrContentListingObject
from ftw.solr.document import SolrDocument
from opengever.base.brain import supports_translated_title
from opengever.base.contentlisting import OpengeverCatalogContentListingObject
from opengever.base.interfaces import IOGSolrDocument
from opengever.base.utils import get_preferred_language_code
from Products.CMFPlone.utils import safe_unicode
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
    def dossier_type(self):
        return self.get('dossier_type', None)

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

    @property
    def title_de(self):
        return self._translated_title('de')

    @property
    def title_en(self):
        return self._translated_title('en')

    @property
    def title_fr(self):
        return self._translated_title('fr')

    def _translated_title(self, lang):
        field_name = 'title_%s' % lang
        # On Catalog brains, title_* attributes are unicode. Mirror this here.
        return safe_unicode(self.get(field_name))

    @property
    def Title(self):
        portal_type = self.get('portal_type')
        if portal_type and supports_translated_title(portal_type):
            code = get_preferred_language_code()
            title = self._translated_title(code)
            if title:
                return title.encode('utf-8')

        return self.get('Title')


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

    def Title(self):
        # Delegate to Title property of our translated title capable OGSolrDocument.
        return self.doc.Title

    def CroppedDescription(self):
        if self.snippets:
            return self.snippets
        return super(OGSolrContentListingObject, self).CroppedDescription()