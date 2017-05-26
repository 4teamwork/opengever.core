class FilteredTableSourceMixin(object):

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object."""

        query = super(FilteredTableSourceMixin, self).build_query()

        if self.config.filterlist_available:
            query = self.extend_query_with_filter(query)

        return query

    def extend_query_with_filter(self, query):
        """When the filterlist is active, we update the query with
        the current filter."""

        # statefilter
        selected_filter_id = self.request.get(self.config.filterlist_name)
        query = self.config.filterlist.update_query(query, selected_filter_id)

        # typefilter
        if self.config.type_filterlist_available:
            type_filter_id = self.request.get(self.config.type_filterlist_name)
            query  = self.config.type_filterlist.update_query(
                query, type_filter_id)

        return query
