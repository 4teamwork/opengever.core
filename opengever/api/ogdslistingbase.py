from opengever.api.batch import SQLHypermediaBatch
from opengever.base.model import create_session
from opengever.tabbedview.sqlsource import cast_to_string
from opengever.tabbedview.sqlsource import sort_column_exists
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
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
    default_sort_on = None
    default_sort_order = 'ascending'
    model_class = None

    def reply(self):
        sort_on, sort_order, search, filters = self.extract_params()
        query = self.get_base_query()
        query = self.extend_query_with_sorting(query, sort_on, sort_order)
        query = self.extend_query_with_search(query, search)
        query = self.extend_query_with_filters(query, filters)

        batch = SQLHypermediaBatch(self.request, query)
        items = []
        for item in batch:
            serializer = queryMultiAdapter(
                (item, self.request), ISerializeToJsonSummary)
            items.append(serializer())

        result = {}
        result['@id'] = batch.canonical_url
        result['items'] = items
        result['items_total'] = batch.items_total
        if batch.links:
            result['batching'] = batch.links
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
