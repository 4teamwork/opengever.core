from binascii import b2a_qp
from collections import OrderedDict
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from opengever.base import is_solr_feature_enabled
from opengever.globalindex.model.task import Task
from opengever.tabbedview import _
from Products.CMFDiffTool.utils import safe_utf8
from Products.CMFPlone.utils import safe_unicode
from zope import schema
from zope.component import getUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


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


class PendingMinusResolvedTasksFilter(Filter):
    """Filter pending tasks to not have
    """
    def update_query(self, query):
        states = list(
            set(Task.PENDING_STATES) - set(('task-state-resolved',)))
        return query.in_state(states)


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
    """A tabbedview filter providing a keywordwidget for subject-filtering.

    This filter only works if solr is enabled.
    """
    separator = '++'

    def __init__(self, context, request, additional_solr_subject_filters=None):
        self.context = context
        self.request = request
        self.additional_solr_subject_filters = \
            additional_solr_subject_filters or []

    @property
    def enabled(self):
        return is_solr_feature_enabled()

    def render_widget(self):
        """Returns the html of a keywordwidget.
        Returns an empty string if the solr is not enabled.
        """
        return self._widget().render() if self.enabled else ''

    def update_query(self, query):
        """Used by the FilteredTableSourceMixin to update the table-query
        with the subject filter.

        This method extends the query with the subject filter.
        """
        if not self.enabled or not self._subject_terms_from_request():
            return query

        query['Subject'] = {
            'query': tuple(self._subject_values_from_request()),
            'operator': 'and'
        }

        return query

    def _widget(self):
        field = schema.List(
            value_type=schema.Choice(source=self._keywords_vocabulary()),
            required=False,
        )
        widget = KeywordFieldWidget(field, self.request)
        widget.value = self._subject_terms_from_request()
        widget.promptMessage = _('placeholder_filter_by_subjects',
                                 default="Filter by subjects...")
        widget.update()

        return widget

    def _subject_terms_from_request(self):
        subjects = self.request.form.get('subjects')
        subjects = subjects.split(self.separator) if subjects else []
        return [safe_unicode(subject) for subject in subjects]

    def _subject_values_from_request(self):
        source = self._keywords_vocabulary()
        subjects = self._subject_terms_from_request()
        return [source.getTermByToken(subject).value for subject in subjects]

    def _keywords_vocabulary(self):
        terms = map(self._make_term, self._context_based_keywords())
        return SimpleVocabulary(terms)

    def _context_based_keywords(self):
        solr = getUtility(ISolrSearch)
        response = solr.search(
            query="*:*", filters=self._solr_filters(), **self._solr_params())
        if not response.is_ok():
            return list()
        return self._extract_facets_from_solr_response(response)

    def _solr_filters(self):
        filters = []
        filters.append(
            'path:{}\\/*'.format(escape('/'.join(self.context.getPhysicalPath()))))
        filters.extend(self.additional_solr_subject_filters)
        return filters

    def _solr_params(self):
        return {
            'facet': True,  # activate facetting
            'facet.field': 'Subject',  # add facets for this field
            'facet.limit': -1,  # do not limit the number of facet-terms
            'rows': 0,  # do not return documents found by the query
            'facet.mincount': 1  # exclude facet-terms with no document
            }

    def _extract_facets_from_solr_response(self, response):
        facets = response.body.get('facet_counts').get('facet_fields').get('Subject')
        return facets[::2]

    def _make_term(self, keyword):
        return SimpleTerm(
            value=keyword, token=self._make_token(keyword), title=keyword)

    def _make_token(self, value):
        return b2a_qp(safe_utf8(value))
