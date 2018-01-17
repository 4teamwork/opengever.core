from opengever.base.interfaces import ISearchSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class FilteredTableSourceMixin(object):

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object."""

        query = super(FilteredTableSourceMixin, self).build_query()

        if self.config.filterlist_available:
            query = self.extend_query_with_filter(query)

        if 'SearchableText' in query:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(ISearchSettings)
            # With Solr we don't have SearchableText in the catalog
            # Let's use the Title index
            if settings.use_solr:
                query['Title'] = query['SearchableText']
                del query['SearchableText']

        return query

    def extend_query_with_filter(self, query):
        """When the filterlist is active, we update the query with
        the current filter."""

        selected_filter_id = self.request.get(self.config.filterlist_name)
        return self.config.filterlist.update_query(query, selected_filter_id)
