from collections import OrderedDict


class Filter(object):
    """Baseclass for a tabbedview listing filter.
    """

    def __init__(self, id, label, default=False):
        self.id = id
        self.label = label
        self.default = default

    def update_query(self, query):
        return query

    def is_active(self, selected_filter_id):
        """Check if the filter is the currently selected
        one (`selected_filter_id`). If there is no filter selected right now it
        checks if the filter is the default one.
        """
        if self.id == selected_filter_id:
            return True

        elif selected_filter_id is None and self.default:
            return True

        return False


class CatalogQueryFilter(Filter):
    """A Filter class which extends the existing portal_catalog query with the
    given extension `query_extension`.
    """

    def __init__(self, id, label, default=False, query_extension=None):
        super(CatalogQueryFilter, self).__init__(id, label, default)
        if query_extension is None:
            query_extension = {}

        self.query_extension = query_extension

    def update_query(self, query):
        query.update(self.query_extension)
        return query


class PendingTasksFilter(Filter):
    """A SQLTaskListing filter which limits the result of only pending tasks.
    """
    def update_query(self, query):
        return query.in_pending_state()


class FilterList(object):
    """A list of tabbedview listing Filter objects.
    """

    def __init__(self, *args):
        self._filters = OrderedDict()
        self.default_filter = None
        for flt in args:
            self._filters[flt.id] = flt
            if flt.default:
                if self.default_filter:
                    raise ValueError(
                        'Only one filter marked as default possible.')

                self.default_filter = flt

    def get(self, filter_id):
        return self._filters[filter_id]

    def filters(self):
        return self._filters.values()
