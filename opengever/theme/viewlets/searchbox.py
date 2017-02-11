from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import pkg_resources


try:
    pkg_resources.get_distribution('ftw.solr')
    from ftw.solr.interfaces import IFtwSolrLayer
except pkg_resources.DistributionNotFound:
    HAS_FTW_SOLR = False
else:
    HAS_FTW_SOLR = True


if HAS_FTW_SOLR:
    from ftw.solr.browser.search import SearchBoxViewlet
else:
    from plone.app.layout.viewlets.common import SearchBoxViewlet


class SearchBoxViewlet(SearchBoxViewlet):
    index = ViewPageTemplateFile('searchbox.pt')

    def has_solr(self):
        return HAS_FTW_SOLR and IFtwSolrLayer.providedBy(self.request)

    def placeholder(self):
        placeholder = getattr(
            self.context, 'search_label', u'title_search_site')
        if isinstance(placeholder, str):
            placeholder = placeholder.decode('utf-8')
        return translate(placeholder,
                         domain='plone',
                         context=self.request)
