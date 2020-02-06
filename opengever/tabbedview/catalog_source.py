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

    def exclude_searchroot_from_query(self, query):
        """Override ftw.table CatalogTableSource's implementation.

        That implementation has serious performance issues for containers
        with many immediate children.

        In GEVER, we patch ExtendedPathIndex to allow us to efficiently exclude
        the search root with a query option.
        """
        if not getattr(self.config, 'exclude_searchroot', True):
            return query

        path_query = query.get('path')
        if path_query is None:
            return query

        if isinstance(path_query, dict):
            if path_query.get('depth') in (0, 1):
                # If any of these depths are specified, do nothing:
                # 0: single object - searchroot exclusion doesn't make sense
                # 1: immediate children - already does what it's supposed to
                #    do (excludes searchroot), nothing to do for us
                return query

            else:
                path_query['exclude_root'] = 1
        else:
            path_query = {'query': path_query, 'exclude_root': 1}
        query['path'] = path_query
        return query

    def solr_results(self, query):
        term = query['SearchableText'].rstrip('*').decode('utf8')
        pattern = (
            u'(Title:{term}* OR SearchableText:{term}* OR metadata:{term}* OR '
            u'Title:{term} OR SearchableText:{term} OR metadata:{term})'
        )

        term_queries = [pattern.format(term=escape(t)) for t in term.split()]
        solr_query = u' AND '.join(term_queries)

        filters = [u'trashed:false']
        for key, value in query.items():
            if key == 'SearchableText':
                continue
            elif key == 'sort_on' or key == 'sort_order':
                continue
            elif key == 'path':
                path_query = value.get('query')
                filters.append(u'path_parent:{}'.format(
                    escape(path_query)))

                depth = value.get('depth', -1)
                try:
                    depth = int(depth)
                except ValueError:
                    depth = -1
                if depth > 0:
                    # path starts with /, so splitting gives context_depth + 1
                    context_depth = len(path_query.split("/")) - 1
                    max_path_depth = context_depth + depth
                    filters.append(u'path_depth:[* TO {}]'.format(max_path_depth))

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

        # Todo: modified be removed once the changed metadata is filled on
        # all deployments.
        # https://github.com/4teamwork/opengever.core/issues/4988
        fl = ['UID', 'getIcon', 'portal_type', 'path', 'id',
              'bumblebee_checksum', 'modified']
        fl = fl + [c['column'] for c in self.config.columns if c['column']]
        params = {
            'fl': fl,
            'q.op': 'AND',
        }

        solr = getUtility(ISolrSearch)
        resp = solr.search(
            query=solr_query, filters=filters, start=0, rows=50, sort=sort,
            **params)

        return [OGSolrDocument(doc) for doc in resp.docs]
