# Adapted from skins/livesearch_reply.py
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from ftw.solr.query import make_query
from opengever.base.solr import OGSolrContentListing
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as pmf
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.utils import normalizeString
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote_plus
from zope.component import getUtility


USE_ICON = True


# https://github.com/4teamwork/opengever.core/blob/master/opengever/base/browser/helper.py#L20
def get_mimetype_icon_klass(item):
    # It just makes sense to guess the mimetype of documents
    if not item.portal_type == 'opengever.document.document':
        return 'contenttype-%s' % normalizeString(item.portal_type)

    icon = item.getIcon

    # Fallback for unknown file type
    if icon == '':
        return "icon-document_empty"

    # Strip '.gif' from end of icon name and remove
    # leading 'icon_'
    filetype = icon[:icon.rfind('.')].replace('icon_', '')
    return 'icon-%s' % normalizeString(filetype)


class LiveSearchReplyView(BrowserView):

    template = ViewPageTemplateFile('templates/livesearch.pt')

    def __call__(self):
        self.search_term = self.request.form.get('q', None)
        if not isinstance(self.search_term, unicode):
            self.search_term = self.search_term.decode('utf-8')

        self.limit = int(self.request.form.get('limit', 10))
        self.path = self.request.form.get('path', getNavigationRoot(self.context))
        results = self.results()
        return self.render_results(results)

    def results(self):
        if not self.search_term:
            return []

        solr = getUtility(ISolrSearch)
        query = make_query(self.search_term)
        filters = [u'trashed:false']
        if self.path:
            filters.append(u'path_parent:%s' % escape(self.path))
        params = {
            'fl': [
                'UID', 'id', 'Title', 'getIcon', 'portal_type', 'path', 'Description'
            ],
        }

        resp = solr.search(
            query=query, filters=filters, rows=self.limit, **params)
        return resp

    def render_results(self, resp):
        ts = getToolByName(self.context, 'translation_service')
        portal_url = getToolByName(self.context, 'portal_url')()
        portalProperties = getToolByName(self.context, 'portal_properties')
        siteProperties = getattr(portalProperties, 'site_properties', None)
        useViewAction = []
        if siteProperties is not None:
            useViewAction = siteProperties.getProperty('typesUseViewActionInListings', [])

        results = OGSolrContentListing(resp)
        self.result_items = []
        self.show_more = {}

        self.legend = ts.translate(legend_livesearch, context=self.request)
        self.nothing_found = ts.translate(label_no_results_found, context=self.request)
        self.advanced_search_url = portal_url + '/advanced_search?SearchableText=%s' % url_quote_plus(self.search_term)
        self.advanced_search_label = ts.translate(label_advanced_search, context=self.request)

        for result in results:
            item_url = result.getURL()
            if result.portal_type in useViewAction:
                item_url += '/view'

            item_url = item_url + u'?SearchableText=%s' % url_quote_plus(self.search_term)
            title = safe_unicode(result.Title())
            css_klass = get_mimetype_icon_klass(result.doc)
            description = safe_unicode(result.Description()) or u''

            self.result_items.append({'url': item_url,
                                      'title': title,
                                      'css_klass': css_klass,
                                      'description': description})

        if results.actual_result_count > self.limit:
            # add a more... row
            searchquery = u'@@search?SearchableText=%s&path=%s' % (url_quote_plus(self.search_term), self.path)
            title = ts.translate(label_show_all, context=self.request)
            self.show_more = {'url': searchquery,
                              'title': title}

        return self.template()


legend_livesearch = pmf(
    'legend_livesearch',
    default='LiveSearch &#8595;')
label_no_results_found = pmf(
    'label_no_results_found',
    default='No matching results found.')
label_has_parse_errors = pmf(
    'label_has_parse_errors',
    default='There were errors parsing your query, please note that boolean '
            'expressions like AND, NOT and OR are only allowed in advanced '
            'search.')
label_advanced_search = pmf(
    'label_advanced_search',
    default='Advanced Search&#8230;')
label_show_all = pmf(
    'label_show_all',
    default='Show all items')
