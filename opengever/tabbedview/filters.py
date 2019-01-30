from collections import OrderedDict
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.tabbedview import _
from zope import schema


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


class FilterList(OrderedDict):
    """A list of tabbedview listing Filter objects.
    """

    def __init__(self, *args):
        super(FilterList, self).__init__()
        self.default_filter = None
        for flt in args:
            self[flt.id] = flt
            if flt.default:
                if self.default_filter:
                    raise ValueError(
                        'Only one filter marked as default possible.')

                self.default_filter = flt

    def filters(self):
        return self.values()

    def update_query(self, query, selected_filter_id):
        if selected_filter_id:
            return self[selected_filter_id].update_query(query)

        return self.default_filter.update_query(query)


class SubjectFilter(object):
    separator = '++'

    def __init__(self, request):
        self.request = request

    def widget(self):
        field = schema.List(
            value_type=schema.Choice(vocabulary='plone.app.vocabularies.Keywords'),
            required=False,
        )
        widget = KeywordFieldWidget(field, self.request)
        widget.value = self._subjects
        widget.promptMessage = _('placeholder_filter_by_subjects',
                                 default="Filter by subjects...")
        widget.update()

        return widget.render()

    def update_query(self, query):
        if not self._subjects:
            return query

        query['Subject'] = {
            'query': tuple(self._subjects),
            'operator': 'and'
        }

        return query

    @property
    def _subjects(self):
        subjects = self.request.form.get('subjects')
        return subjects.split(self.separator) if subjects else []
