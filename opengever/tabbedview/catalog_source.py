from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from ftw.table.catalog_source import CatalogTableSource
from ftw.table.interfaces import ITableSource
from opengever.base.interfaces import ISearchSettings
from opengever.base.solr import OGSolrDocument
from opengever.tabbedview.filtered_source import FilteredTableSourceMixin
from opengever.tabbedview.interfaces import IGeverCatalogTableSourceConfig
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface


@implementer(ITableSource)
@adapter(IGeverCatalogTableSourceConfig, Interface)
class GeverCatalogTableSource(FilteredTableSourceMixin, CatalogTableSource):
    """Default catalog tablesource extended with filter functionality.
    """

    def search_results(self, query):
        """Executes the query and returns a tuple of `results`.
        """
        if 'SearchableText' in query:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(ISearchSettings)
            if settings.use_solr:
                return self.solr_results(query)

        return super(GeverCatalogTableSource, self).search_results(query)

    def solr_results(self, query):
        solr_query = u'Title:{term} OR SearchableText:{term}'.format(
            term=query['SearchableText'])

        filters = [u'trashed:false']
        for key, value in query.items():
            if key == 'SearchableText':
                continue
            elif key == 'sort_on' or key == 'sort_order':
                continue
            elif key == 'path':
                filters.append(u'path_parent:{}'.format(
                    escape(value.get('query'))))
            elif isinstance(value, (list, tuple)):
                filters.append(u'{}:({})'.format(
                    key, escape(' OR '.join(value))))
            elif isinstance(value, bool):
                filters.append(u'{}:{}'.format(
                    key, 'true' if value else 'false'))
            else:
                filters.append(u'{}:{}'.format(key, escape(value)))

        sort = query.get('sort_on', None)
        if sort:
            sort_order = query.get('sort_order', 'ascending')
            if sort_order in ['descending', 'reverse']:
                sort += ' desc'
            else:
                sort += ' asc'

        fl = ['UID', 'getIcon', 'portal_type', 'path', 'id',
              'bumblebee_checksum']
        fl = fl + [c['column'] for c in self.config.columns if c['column']]
        params = {
            'fl': fl,
        }

        solr = getUtility(ISolrSearch)
        resp = solr.search(
            query=solr_query, filters=filters, start=0, rows=50, sort=sort,
            **params)

        return [OGSolrDocument(doc) for doc in resp.docs]
