from plone.batching.batch import BaseBatch
from plone.restapi.batching import DEFAULT_BATCH_SIZE
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from sqlalchemy.sql.expression import asc
from zExceptions import BadRequest


class SQLBatch(BaseBatch):
    """Plone batching for SQLAlchmey queries
    """

    def __init__(self, query, size, start=0, end=0, orphan=0, overlap=0,
                 pagerange=7, query_count=0):

        self._results = None
        self.query = query
        self.query_count = query.count()
        self.limited_query = query.limit(size).offset(start)

        return super(SQLBatch, self).__init__(
            None, size, start, end, orphan, overlap, pagerange)

    @property
    def results(self):
        if not self._results:
            self._results = self.limited_query.all()

        return self._results

    @classmethod
    def fromPagenumber(cls, query, pagesize=20, pagenumber=1, navlistsize=5):
        """ Create new page from sequence and pagenumber
        """
        start = max(0, (pagenumber - 1) * pagesize)
        return cls(query, pagesize, start, pagerange=navlistsize)

    @property
    def sequence_length(self):
        """Length of sequence using query.count()
        """
        return self.query_count

    @property
    def next(self):
        """ Next batch page
        """
        if self.end >= (self.last + self.pagesize):
            return None
        return SQLBatch(
            self.query,
            self._size,
            self.end - self.overlap,
            0,
            self.orphan,
            self.overlap,
            query_count=self.query_count
        )

    @property
    def previous(self):
        """ Previous batch page
        """
        if not self.first:
            return None
        return SQLBatch(
            self.query,
            self._size,
            self.first - self._size + self.overlap,
            0,
            self.orphan,
            self.overlap,
        )

    def __getitem__(self, index):
        """ Get item from batch
        """
        return self.results[index]

    @property
    def items_not_on_page(self):
        """ Items of sequence outside of batch
        """
        raise NotImplementedError


class SQLHypermediaBatch(HypermediaBatch):
    """Plone.restapi HypermediaBatch for SQLAlchmey queries.
    """

    def __init__(self, request, query, unique_sort_key, unique_sort_order=asc):
        self.request = request
        self.query = query

        # unique_sort_key is needed to make sure that results are always
        # sorted, otherwise sorting can be undefined. As a separate query is
        # made for every batch and for every item, undefined sort order can
        # lead to problems when iterating over the items and batching
        # (some items returned more than once and others missing).
        query = self.extend_query_with_unique_sorting(
            query, unique_sort_key, unique_sort_order)

        self.b_start = int(json_body(self.request).get('b_start', False)) \
            or int(self.request.form.get("b_start", 0))
        self.b_size = int(json_body(self.request).get('b_size', False)) \
            or int(self.request.form.get("b_size", DEFAULT_BATCH_SIZE))

        if self.b_start < 0:
            raise BadRequest("The parameter 'b_start' can't be negative.")
        if self.b_size < 0:
            raise BadRequest("The parameter 'b_size' can't be negative.")

        self.query_count = query.count()
        self.batch = SQLBatch(query, self.b_size, self.b_start)

    def _batch_for_page(self, pagenumber):
        new_batch = SQLBatch.fromPagenumber(
            self.query, pagesize=self.b_size, pagenumber=pagenumber)
        return new_batch

    @property
    def items_total(self):
        return self.query_count

    def extend_query_with_unique_sorting(self, query, unique_key, unique_sort_order):
        return query.order_by(unique_sort_order(unique_key))

    @property
    def links(self):
        """Get a dictionary with batching links.

        Overwritten to avoid additional SQL queries when getting other
        SQLBatches. Generate URLs without querying the SQL.
        """

        if self.items_total <= self.b_size:
            return None

        links = {}
        links["@id"] = self.current_batch_url
        links["first"] = self._url_for_batch_start(1)
        links["last"] = self._url_for_batch_start(self.get_last_batch_start())

        if self.batch.end < (self.batch.last + self.batch.pagesize):
            links["next"] = self._url_for_batch_start(
                self.batch.end - self.batch.overlap + 1)

        if self.batch.first:
            links["prev"] = self._url_for_batch_start(
                self.batch.first - self.batch._size + self.batch.overlap + 1)

        return links

    def get_last_batch_start(self):
        return max(0, (self.batch.lastpage - 1) * self.batch._size) + 1

    def _url_for_batch_start(self, batch_start):
        """Return URL that points to the given batch.
        """
        new_start = max(0, batch_start - 1)
        url = self._url_with_params(params={"b_start": new_start})
        return url
