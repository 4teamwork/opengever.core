from opengever.api.batch import SQLHypermediaBatch
from opengever.base.model import create_session
from opengever.tabbedview.sqlsource import cast_to_string
from opengever.tabbedview.sqlsource import sort_column_exists
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import desc
from zope.component import queryMultiAdapter
from ZPublisher.HTTPRequest import record


class OGDSListingBaseService(Service):
    """API Endpoint base class for ogds listings.

    Not directly exposed via API.

    Handles a subset of the parameters already provided by the @listing
    endpoint.
    """

    searchable_columns = tuple()
    facet_columns = tuple()
    facet_label_transforms = {}
    # unique_sort_on should be set in all subclasses to a unique key to make
    # sure that results are always sorted, otherwise sorting can be undefined.
    # As a separate query is made for every batch and for every item, undefined
    # sort order can lead to problems when iterating over the items and
    # batching (some items returned more than once and others missing).
    unique_sort_on = None
    default_sort_on = None
    default_sort_order = 'ascending'
    model_class = None
    serializer_interface = ISerializeToJsonSummary

    def reply(self):
        sort_on, sort_order, search, filters = self.extract_params()
        query = self.get_base_query()
        query = self.extend_query_with_sorting(query, sort_on, sort_order)
        query = self.extend_query_with_search(query, search)
        query = self.extend_query_with_filters(query, filters)

        if sort_order in ['descending', 'reverse']:
            order_f = desc
        else:
            order_f = asc

        batch = SQLHypermediaBatch(self.request, query, self.unique_sort_on, order_f)
        items = []
        for item in batch:
            serializer = queryMultiAdapter(
                (item, self.request), self.serializer_interface)
            items.append(serializer())

        result = {}
        result['@id'] = batch.canonical_url
        result['items'] = items
        result['items_total'] = batch.items_total
        if batch.links:
            result['batching'] = batch.links
        result['b_start'] = batch.b_start
        result['b_size'] = batch.b_size
        result['facets'] = self.facets(search, filters)
        return result

    def extract_params(self):
        params = self.request.form.copy()

        sort_on = params.get('sort_on', self.default_sort_on).strip()
        sort_order = params.get('sort_order', self.default_sort_order)

        search = params.get('search', u'').strip()
        search = safe_unicode(search)
        # remove trailing asterisk
        if search.endswith(u'*'):
            search = search[:-1]

        filters = params.get('filters', {})
        if not isinstance(filters, record):
            filters = {}

        return sort_on, sort_order, search, filters

    def get_base_query(self):
        session = create_session()
        return session.query(self.model_class)

    def extend_query_with_sorting(self, query, sort_on, sort_order):
        # early abort if the column is not in the query
        if not sort_column_exists(query, sort_on):
            return query

        # Don't plug column names as literal strings into an order_by
        # clause, but use a ColumnClause instead to allow SQLAlchemy to
        # properly quote the identifier name depending on the dialect
        sort_on = column(sort_on)

        if sort_order in ['descending', 'reverse']:
            order_f = desc
        else:
            order_f = asc
        return query.order_by(order_f(sort_on))

    def extend_query_with_search(self, query, search):
        if not search:
            return query

        # split up the search term into words, extend them with the default
        # wildcards and then search for every word seperately
        for word in search.split():
            term = u'%%%s%%' % word

            expressions = []
            for field in self.searchable_columns:
                expressions.append(cast_to_string(field).ilike(term))
            query = query.filter(or_(*expressions))

        return query

    def extend_query_with_filters(self, query, filters):
        return query

    def facets(self, search, filters):
        session = create_session()
        base_filter = self.get_base_query().whereclause
        requested_facets = self.request.form.get('facets', [])
        facets = {}
        for col in self.facet_columns:
            if col.name not in requested_facets:
                continue
            query = session.query(col, func.count(self.unique_sort_on)).group_by(col)
            if base_filter is not None:
                query = query.filter(base_filter)
            query = self.extend_query_with_search(query, search)
            query = self.extend_query_with_filters(query, filters)

            facets[col.name] = {}
            transform = self.facet_label_transforms.get(col.name, lambda x: x)
            for facet_info in query.all():
                if not facet_info[0]:
                    continue
                facets[col.name][facet_info[0]] = {
                    'count': facet_info[1],
                    'label': transform(facet_info[0]),
                }

        return facets
