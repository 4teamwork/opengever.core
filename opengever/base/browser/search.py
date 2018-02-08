from DateTime import DateTime
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from ftw.solr.query import make_query
from opengever.base.interfaces import ISearchSettings
from opengever.base.solr import OGSolrContentListing
from opengever.bumblebee import is_bumblebee_feature_enabled
from plone import api
from plone.app.search.browser import EVER
from plone.app.search.browser import quote_chars
from plone.app.search.browser import Search
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.utils import safe_unicode
from zope.component import getMultiAdapter
from zope.component import getUtility
from ZPublisher.HTTPRequest import record

FILTER_TYPES = [
    'ftw.mail.mail',
    'opengever.document.document',
    'opengever.dossier.businesscasedossier',
    'opengever.inbox.forwarding',
    'opengever.task.task']


class OpengeverSearch(Search):
    """Customizing the plone default Search View.
    """

    b_size = 25
    number_of_documents = 0
    offset = 0

    def __init__(self, context, request):
        super(OpengeverSearch, self).__init__(context, request)

        catalog = api.portal.get_tool('portal_catalog')
        self.valid_keys = self.valid_keys + tuple(catalog.indexes())

    def results(self, query=None, batch=True, b_size=10, b_start=0):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)

        if settings.use_solr:
            results = self.solr_results(
                query=query, batch=batch, b_size=b_size, b_start=b_start)
        else:
            results = super(OpengeverSearch, self).results(
                query=query, batch=batch, b_size=self.b_size, b_start=b_start)

        if is_bumblebee_feature_enabled:
            self.calculate_showroom_configuration(results)

        return results

    def solr_results(self, query=None, batch=True, b_size=10, b_start=0):

        searchable_text = self.request.form.get('SearchableText', '')
        if searchable_text:
            query = make_query(searchable_text)
        else:
            query = u'*:*'

        filters = self.solr_filters()

        params = {
            'fl': [
                'UID', 'Title', 'getIcon', 'portal_type', 'path',
                'containing_dossier', 'id', 'created', 'modified',
                'review_state', 'bumblebee_checksum',
            ],
            'hl': 'on',
            'hl.fl': 'SearchableText',
            'hl.snippets': 3,
        }
        solr = getUtility(ISolrSearch)
        resp = solr.search(
            query=query, filter=filters, start=b_start, rows=b_size, **params)
        results = OGSolrContentListing(resp)

        if batch:
            results = Batch(results, b_size, b_start)
        return results

    def calculate_showroom_configuration(self, results):
        bumblebee_docs = [d for d in results if d.is_bumblebeeable()]
        self.offset = 0
        self.number_of_documents = len(bumblebee_docs)

    def solr_filters(self):
        solr = getUtility(ISolrSearch)
        schema = solr.manager.schema
        filters = []
        for key, value in self.request.form.items():
            if key == 'SearchableText':
                continue
            if key not in schema.fields:
                continue

            if isinstance(key, str):
                key = key.decode('utf8')

            # Date range queries
            if isinstance(value, record):
                range_ = value.get('range', None)
                if range_ in ['min', 'max', 'minmax']:
                    value = value.get('query', None)
                    if value is None:
                        continue
                    try:
                        value = [DateTime(v) for v in value]
                    except SyntaxError:
                        continue
                    if range_ == 'min':
                        filters.append(u'%s:[%s TO *]' % (
                            key, escape(value[0].HTML4())))
                    elif range_ == 'max':
                        filters.append(u'%s:[* TO %s]' % (
                            key, escape(value[0].HTML4())))
                    elif range_ == 'minmax':
                        filters.append(u'%s:[%s TO %s]' % (
                            key,
                            escape(value[0].HTML4()),
                            escape(value[1].HTML4())))
            else:
                if not isinstance(value, (list, tuple)):
                    value = [value]
                for i, v in enumerate(value):
                    if isinstance(v, str):
                        v = v.strip()
                        v = v.decode('utf8')
                        v = escape(v)
                        if ' ' in v:
                            v = '"%s"' % v
                        value[i] = v
                    else:
                        value[i] = v
                if len(value) > 1:
                    filters.append(u'%s:(%s)' % (key, ' OR '.join(value)))
                else:
                    filters.append(u'%s:%s' % (key, value[0]))

        return filters

    def breadcrumbs(self, item):
        obj = item.getObject()
        view = getMultiAdapter((obj, self.request), name='breadcrumbs_view')
        # cut off the item itself
        breadcrumbs = list(view.breadcrumbs())[:-1]

        return breadcrumbs

    def types_list(self):
        types = super(OpengeverSearch, self).types_list()
        return list(set(FILTER_TYPES) & set(types))

    def should_handle_key(self, key):
        return ((key in self.valid_keys) or key.startswith('facet.')) \
            and not key.endswith('_usage')

    def handle_query_filter_value(self, query, key, value):
        if not value or not self.should_handle_key(key):
            return

        query[key] = value

    def _filter_query(self, query):
        """The _filter_query of the standard search view (plone.app.search)
        cancel the query generation if not SearchableText is given.
        In some case (for example in opengever.advancedsearch), we generate
        also searches without a searchabletext. So we temporarily fake
        the SearchableText.

        Besides that we also handle date range queries and subject queries
        separately.

        XXX This method should be removed, after the solr integration
        meta-XXX should it? now it contains custom stuff.

        """
        request = self.request
        text = query.get('SearchableText', None)
        if text is None:
            text = request.form.get('SearchableText', '')

        for key, value in request.form.items():
            self.handle_query_filter_value(query, key, value)

        if text:
            query['SearchableText'] = quote_chars(text)

        # don't filter on created at all if we want all results
        created = query.get('created')
        if created:
            if created.get('query'):
                if created['query'][0] <= EVER:
                    del query['created']

        # respect `types_not_searched` setting
        types = query.get('portal_type', [])
        if 'query' in types:
            types = types['query']
        query['portal_type'] = self.filter_types(types)
        # respect effective/expiration date
        query['show_inactive'] = False
        # respect navigation root
        if 'path' not in query:
            query['path'] = getNavigationRoot(self.context)

        # Special treatment for the Subject index
        # The index only stores unicode values, so we have to search
        # for unicode values.
        if 'Subject' in query:
            query['Subject'] = safe_unicode(query['Subject'])

        return query
