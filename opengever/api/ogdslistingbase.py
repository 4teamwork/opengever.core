from opengever.base.model import create_session
from opengever.base.utils import safe_int
from opengever.tabbedview.sqlsource import cast_to_string
from opengever.tabbedview.sqlsource import sort_column_exists
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy import or_
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import desc
from zExceptions import BadRequest
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
        sort_on, sort_order, search, filters, b_start, b_size = self.extract_params()
        query = self.get_base_query()
        query = self.extend_query_with_sorting(query, sort_on, sort_order)
        query = self.extend_query_with_search(query, search)
        query = self.extend_query_with_filters(query, filters)
        items_total = query.count()
        query = self.extend_query_with_batching(query, b_start, b_size)

        items = []
        for model in query.all():
            serializer = queryMultiAdapter(
                (model, self.request), ISerializeToJsonSummary)
            items.append(serializer())

        # We use HypermediaBatch for the canonical url only
        batch = HypermediaBatch(self.request, items)
        # return empty facet dict to keep response structure consistent
        return {
          "@id": batch.canonical_url,
          "b_size": b_size,
          "b_start": b_start,
          "facets": {},
          "items": items,
          "items_total": items_total
        }

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

        b_start = safe_int(params.get('b_start', 0), 0)
        if b_start < 0:
            raise BadRequest("The parameter 'b_start' can't be negative.")
        b_size = min(safe_int(params.get('b_size', 25), 25), 100)
        if b_size < 0:
            raise BadRequest("The parameter 'b_size' can't be negative.")

        return sort_on, sort_order, search, filters, b_start, b_size

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

    def extend_query_with_batching(self, query, b_start, b_size):
        query = query.offset(b_start)
        query = query.limit(b_size)
        return query

    @property
    def item_base_get_url(self):
        """URL used to construct the GET url for items in the listing,
        of the form item_base_get_url/endpoint_name/item_id
        """
        return self.context.absolute_url()
