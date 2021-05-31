from plone.batching.batch import BaseBatch
from plone.restapi.batching import DEFAULT_BATCH_SIZE
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from sqlalchemy.sql.expression import asc
from zExceptions import BadRequest


class SQLBatch(BaseBatch):
    """Plone batching for SQLAlchmey queries
    """

    @property
    def sequence_length(self):
        """Length of sequence using query.count()
        """
        return self._sequence.count()

    @property
    def next(self):
        """ Next batch page
        """
        if self.end >= (self.last + self.pagesize):
            return None
        return SQLBatch(
            self._sequence,
            self._size,
            self.end - self.overlap,
            0,
            self.orphan,
            self.overlap
        )

    @property
    def previous(self):
        """ Previous batch page
        """
        if not self.first:
            return None
        return SQLBatch(
            self._sequence,
            self._size,
            self.first - self._size + self.overlap,
            0,
            self.orphan,
            self.overlap
        )


class SQLHypermediaBatch(HypermediaBatch):
    """Plone.restapi HypermediaBatch for SQLAlchmey queries.
    """

    def __init__(self, request, query, unique_sort_key, unique_sort_order=asc):
        self.request = request

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

        self.batch = SQLBatch(query, self.b_size, self.b_start)

    def _batch_for_page(self, pagenumber):
        new_batch = SQLBatch.fromPagenumber(
            self.batch._sequence, pagesize=self.b_size, pagenumber=pagenumber
        )
        return new_batch

    def extend_query_with_unique_sorting(self, query, unique_key, unique_sort_order):
        return query.order_by(unique_sort_order(unique_key))
