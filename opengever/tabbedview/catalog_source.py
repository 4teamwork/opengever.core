from ftw.solr.converters import to_iso8601
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from ftw.table.catalog_source import CatalogTableSource
from ftw.table.interfaces import ITableSource
from opengever.base.interfaces import ISearchSettings
from opengever.base.sentry import log_msg_to_sentry
from opengever.base.solr import OGSolrDocument
from opengever.tabbedview.filtered_source import FilteredTableSourceMixin
from opengever.tabbedview.interfaces import IGeverCatalogTableSourceConfig
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
import logging


logger = logging.getLogger('opengever.tabbedview.catalog_source')


@implementer(ITableSource)
@adapter(IGeverCatalogTableSourceConfig, Interface)
class GeverCatalogTableSource(FilteredTableSourceMixin, CatalogTableSource):
    """Default catalog tablesource extended with filter functionality.
    """

    def search_results(self, query):
        """Executes the query and returns a tuple of `results`.
        """

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        if settings.use_solr:
            return self.solr_results(self.exclude_searchroot_from_query(query))

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

    def _extract_sorting(self, solr, query):
        sort = query.pop('sort_on', self.config.sort_on)
        if sort in solr.manager.schema.fields:
            if sort == self.config.sort_on:
                sort_order = query.pop('sort_order', self.config.sort_order)
            else:
                sort_order = query.pop('sort_order', 'ascending')

            if sort_order in ['descending', 'reverse']:
                sort += ' desc'
            else:
                sort += ' asc'
        else:
            logger.warning('Ignoring unknown sort criteria %s', sort)
            log_msg_to_sentry(
                'Ignoring unknown sort criteria', level='warning',
                extra={'sort_criteria': sort})
            sort = None

        return sort

    def solr_results(self, query):
        if 'SearchableText' in query:
            term = query['SearchableText'].rstrip('*').decode('utf8')
            pattern = (
                u'(Title:{term}* OR SearchableText:{term}* OR metadata:{term}* OR '
                u'Title:{term} OR SearchableText:{term} OR metadata:{term})'
            )

            term_queries = [pattern.format(term=escape(t)) for t in term.split()]
            solr_query = u' AND '.join(term_queries)
        else:
            solr_query = u'*:*'

        solr = getUtility(ISolrSearch)
        sort = self._extract_sorting(solr, query)

        filters = []
        if 'trashed' not in query:
            filters.append(u'trashed:false')
        for key, value in query.items():
            if key not in solr.manager.schema.fields:
                logger.warning(
                    'Ignoring filter criteria for unknown field %s', key)
                log_msg_to_sentry(
                    'Ignoring filter criteria for unknown field',
                    level='warning', extra={'field': key})
                continue
            elif key == 'SearchableText':
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

                if value.get('exclude_root', False):
                    filters.append(u'-path: {}'.format(escape(path_query)))

            elif isinstance(value, (list, tuple)):
                filters.append(u'{}:({})'.format(
                    key, escape(' OR '.join(value))))
            elif isinstance(value, bool):
                filters.append(u'{}:{}'.format(
                    key, 'true' if value else 'false'))
            elif isinstance(value, dict):
                _query = value.get('query')
                operator = value.get('operator')
                range_ = value.get('range', None)
                if query and isinstance(_query, (list, tuple)) and operator:
                    operator = ' {} '.format(operator.upper())
                    filters.append(u'{}:({})'.format(
                        key, escape(operator.join(_query))))
                elif range_ in ['min', 'max', 'minmax']:
                    if not isinstance(_query, (list, tuple)):
                        _query = [_query]
                    if range_ == 'min':
                        filters.append(u'{}:[{} TO *]'.format(
                            key, escape(to_iso8601(_query[0]))))
                    elif range_ == 'max':
                        filters.append(u'{}:[* TO {}]'.format(
                            key, escape(to_iso8601(_query[0]))))
                    elif range_ == 'minmax':
                        filters.append(u'{}:[{} TO {}]'.format(
                            key,
                            escape(to_iso8601(_query[0])),
                            escape(to_iso8601(_query[1])),
                        ))
            else:
                filters.append(u'{}:{}'.format(key, escape(value)))

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

        start = (self.config.batching_current_page - 1) * self.config.pagesize
        resp = solr.search(
            query=solr_query, filters=filters, start=start,
            rows=self.config.pagesize, sort=sort, **params)

        # Avoid calling any custom sort method. This is highly inefficient and
        # would require us to load *all* results from Solr.
        self.config._custom_sort_method = (
            lambda results, sort_on, sort_reverse: results
        )

        return BatchableSolrResults(resp)


class BatchableSolrResults:
    """A sequence of Solr docs that plays well with Plone batching"""
    def __init__(self, resp):
        self.actual_result_count = resp.num_found
        self.start = resp.start
        self.docs = [OGSolrDocument(doc) for doc in resp.docs]

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.docs[
                slice(key.start - self.start, key.stop - self.start, key.step)
            ]
        return self.docs[key - self.start]

    def __len__(self):
        return self.actual_result_count
