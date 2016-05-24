from five import grok
from ftw.table.basesource import BaseTableSource


class GeverTableSource(grok.MultiAdapter, BaseTableSource):
    """Base table source for all gever tables.

    Add support for gever-specific filterlist configuration option, also
    adds support for grok-style directives. It should always be used whenever
    a table-source is required.

    """
    grok.baseclass()

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object.
        """
        query = super(GeverTableSource, self).build_query()

        if self.config.filterlist_available:
            query = self.extend_query_with_filter(query)

        return query

    def extend_query_with_filter(self, query):
        """When the filterlist is active, we update the query with
        the current filter.

        """
        return query
