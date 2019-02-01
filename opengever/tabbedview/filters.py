from collections import OrderedDict
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.tabbedview import _
from plone import api
from Products.CMFDiffTool.utils import safe_utf8
from Products.CMFPlone.utils import safe_unicode
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from binascii import b2a_qp


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
    widget_additional_query = {}

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def widget(self):
        """Returns the html of a keywordwidget.
        """
        field = schema.List(
            value_type=schema.Choice(source=self._keywords_vocabulary()),
            required=False,
        )
        widget = KeywordFieldWidget(field, self.request)
        widget.value = self._subject_terms_from_request()
        widget.promptMessage = _('placeholder_filter_by_subjects',
                                 default="Filter by subjects...")
        widget.update()

        return widget.render()

    def update_query(self, query):
        """Used by the FilteredTableSourceMixin to update the table-query
        with the subject filter.

        This method extends the query with the subject filter.
        """
        if not self._subject_terms_from_request():
            return query

        query['Subject'] = {
            'query': tuple(self._subject_values_from_request()),
            'operator': 'and'
        }

        return query

    def _subject_terms_from_request(self):
        subjects = self.request.form.get('subjects')
        subjects = subjects.split(self.separator) if subjects else []
        return [safe_unicode(subject) for subject in subjects]

    def _subject_values_from_request(self):
        source = self._keywords_vocabulary()
        subjects = self._subject_terms_from_request()
        subjects = [source.getTermByToken(subject).value for subject in subjects]

        return [safe_unicode(subject) for subject in subjects]

    def _keywords_vocabulary(self):
        terms = map(self._make_term, self._context_based_keywords())
        return SimpleVocabulary(terms)

    def _context_based_keywords(self):
        catalog = api.portal.get_tool('portal_catalog')
        query = {'path': {
            'query': '/'.join(self.context.getPhysicalPath()),
            'depth': -1}}
        query.update(self.widget_additional_query)

        return self._unique_subjects(catalog(query))

    def _make_term(self, keyword):
        return SimpleTerm(
            value=keyword, token=self._make_token(keyword), title=keyword)

    def _make_token(self, value):
        return b2a_qp(value)

    def _unique_subjects(self, brains):
        context_path = '/'.join(self.context.getPhysicalPath())
        return set([safe_utf8(subject)
                    for brain in brains
                    for subject in brain.Subject
                    if brain.getPath() != context_path])
