from opengever.tabbedview.filters import SubjectFilter


class FilteredTableSourceMixin(object):

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object."""

        query = super(FilteredTableSourceMixin, self).build_query()

        if self.config.filterlist_available:
            query = self.extend_query_with_filter(query)

        if self.config.subject_filter_available:
            SubjectFilter(self.config.context, self.request).update_query(query)

        return query

    def extend_query_with_filter(self, query):
        """When the filterlist is active, we update the query with
        the current filter."""
        selected_filter_id = self.request.get(self.config.filterlist_name)
        return self.config.filterlist.update_query(query, selected_filter_id)
