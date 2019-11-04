from plone.batching.batch import BaseBatch
from plone.restapi.batching import DEFAULT_BATCH_SIZE
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body


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

    def __init__(self, request, results):
        self.request = request

        self.b_start = int(json_body(self.request).get('b_start', False)) \
            or int(self.request.form.get("b_start", 0))
        self.b_size = int(json_body(self.request).get('b_size', False)) \
            or int(self.request.form.get("b_size", DEFAULT_BATCH_SIZE))

        self.batch = SQLBatch(results, self.b_size, self.b_start)

    def _batch_for_page(self, pagenumber):
        new_batch = SQLBatch.fromPagenumber(
            self.batch._sequence, pagesize=self.b_size, pagenumber=pagenumber
        )
        return new_batch
