from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate


try:
    from ftw.solr.browser.search import SearchBoxViewlet
    from ftw.solr.interfaces import IFtwSolrLayer
except ImportError:
    from plone.app.layout.viewlets.common import SearchBoxViewlet
    HAS_FTW_SOLR1 = False
else:
    HAS_FTW_SOLR1 = True


class SearchBoxViewlet(SearchBoxViewlet):
    index = ViewPageTemplateFile('searchbox.pt')

    def has_solr(self):
        return HAS_FTW_SOLR1 and IFtwSolrLayer.providedBy(self.request)

    def placeholder(self):
        placeholder = getattr(self.context, 'search_label', u'title_search_site')
        if isinstance(placeholder, str):
            placeholder = placeholder.decode('utf-8')
        return translate(placeholder,
                         domain='plone',
                         context=self.request)
