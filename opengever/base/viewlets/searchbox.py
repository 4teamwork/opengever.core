from opengever.base.interfaces import ISearchSettings
from plone.app.layout.viewlets.common import SearchBoxViewlet
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.i18n import translate


class SearchBoxViewlet(SearchBoxViewlet):
    index = ViewPageTemplateFile('searchbox.pt')

    def has_solr(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        if settings.use_solr:
            return True
        return False

    def placeholder(self):
        placeholder = getattr(self.context, 'search_label',
                              u'title_search_site')
        return translate(placeholder, domain='plone', context=self.request)

    def prefill(self):
        searchable_text = self.request.form.get('SearchableText')
        if searchable_text:
            return searchable_text.replace(' AND', '').replace(' OR', '').replace(' NOT', '')
        return ''
