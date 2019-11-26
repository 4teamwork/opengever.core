from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from ftw.solr.converters import to_iso8601
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from opengever.api.solr_query_service import SolrQueryBaseService
from opengever.base.interfaces import ISearchSettings
from plone.registry.interfaces import IRegistry
from plone.restapi.batching import HypermediaBatch
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.ZCatalog.Lazy import LazyMap
from zExceptions import BadRequest
from zope.component import getUtility
from ZPublisher.HTTPRequest import record


def get_path_depth(context):
    # This mirrors the implementation in ftw.solr
    return len(context.getPhysicalPath()) - 1


OTHER_FIELDS = set([
    'file_extension',
    'deadline',
    'containing_dossier',
    'issuer',
    'UID',
    'document_author',
    'is_subtask',
    'start',
    'checked_out',
    'completed',
    'phone_office',
    'document_type',
    'modified',
    'sequence_number',
    'containing_subdossier',
    'has_sametype_children',
    'reference',
    'is_subdossier',
    'document_date',
    'end',
    'responsible',
    'lastname',
    'review_state',
    'email',
    'firstname',
    'receipt_date',
    'created',
    'changed',
    'delivery_date'])

DATE_INDEXES = set([
    'changed',
    'created',
    'delivery_date',
    'document_date',
    'end',
    'modified',
    'receipt_date',
    'start',
    'deadline',
])

FILTERS = {
    u'dossiers': [
        u'object_provides:opengever.dossier.behaviors.dossier.IDossierMarker',
    ],
    u'documents': [
        u'object_provides:opengever.document.behaviors.IBaseDocument',
    ],
    u'workspaces': [
        u'object_provides:opengever.workspace.interfaces.IWorkspace',
    ],
    u'workspace_folders': [
        u'object_provides:opengever.workspace.interfaces.IWorkspaceFolder',
    ],
    u'tasks': [
        u'object_provides:opengever.task.task.ITask',
    ],
    u'todos': [
        u'object_provides:opengever.workspace.interfaces.IToDo',
    ],
    u'proposals': [
        u'object_provides:opengever.meeting.proposal.IProposal',
    ],
    u'contacts': [
        u'object_provides:opengever.contact.contact.IContact',
    ]
}


REQUIRED_SEARCH_FIELDS = set(['UID',
                              'getIcon',
                              'portal_type',
                              'path',
                              'id',
                              'bumblebee_checksum'])

REQUIRED_RESPONSE_FIELDS = set(['@id'])


def with_active_solr_only(func):
    """Raises an error if solr is not activated
    """
    def validate(*args, **kwargs):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSettings)
        if not settings.use_solr:
            raise BadRequest("Solr is deactivated. The @listing endpoint is "
                             "only available with an activated solr")

        return func(*args, **kwargs)
    return validate


class Listing(SolrQueryBaseService):
    """List of content items"""

    required_response_fields = REQUIRED_RESPONSE_FIELDS
    required_search_fields = REQUIRED_SEARCH_FIELDS
    other_allowed_fields = OTHER_FIELDS

    def __init__(self, context, request):
        super(Listing, self).__init__(context, request)
        self.allowed_fields = set(self.field_mapping.keys()) | self.other_allowed_fields

    def extract_query(self, params):
        term = params.get('search', '').strip()
        query = '*:*'
        if term:
            pattern = (
                u'(Title:{term}* OR SearchableText:{term}*'
                u' OR metadata:{term}*)')
            term_queries = [
                pattern.format(term=escape(safe_unicode(t))) for t in term.split()]
            query = u' AND '.join(term_queries)
        return query

    def extract_filters(self, params):
        filters = params.get('filters', {})
        if not isinstance(filters, record):
            filters = {}
        filter_queries = []

        # Exclude searchroot
        context_uid = IUUID(self.context, None)
        if context_uid:
            filter_queries.append(u'-UID:%s' % context_uid)

        if 'trashed' not in filters:
            filter_queries.append(u'trashed:false')
        filter_queries.extend(FILTERS[self.listing_name])
        filter_queries.append(u'path_parent:{}'.format(escape(
            '/'.join(self.context.getPhysicalPath()))))

        depth = self.request.form.get('depth', -1)
        try:
            depth = int(depth)
        except ValueError:
            depth = -1

        if depth > 0:
            context_depth = get_path_depth(self.context)
            max_path_depth = context_depth + depth
            filter_queries.append(u'path_depth:[* TO {}]'.format(max_path_depth))

        for key, value in filters.items():
            if not self.is_field_allowed(key):
                continue
            key = self.get_field_index(key)
            if key is None:
                continue
            if key in DATE_INDEXES:
                # It seems solr needs date filters unescaped, hence we
                # only escape the other filter values
                value = self.daterange_filter(value)
            elif isinstance(value, list):
                value = map(escape, value)
                value = map(safe_unicode, value)
                value = u' OR '.join(value)
            else:
                value = escape(value)
            if value is not None:
                # XXX: Instead of littering all this code with safe_unicode,
                # we should convert user-supplied input to unicode *once*
                # at the system boundaries (when extracting values from
                # self.request.form) once this endpoint gets refactored.
                value = safe_unicode(value)
                filter_queries.append(u'{}:({})'.format(escape(key), value))
        return filter_queries

    def extract_sort(self, params, query):
        sort_on = params.get('sort_on', DEFAULT_SORT_INDEX)
        if self.is_field_allowed(sort_on):
            sort_on = self.get_field_sort_index(sort_on)
        else:
            sort_on = DEFAULT_SORT_INDEX

        sort_order = params.get('sort_order', 'descending')
        sort = sort_on
        if sort:
            if sort_order in ['descending', 'reverse']:
                sort += ' desc'
            else:
                sort += ' asc'
        return sort

    def parse_requested_fields(self, params):
        return params.get('columns', None)

    def prepare_additional_params(self, params):
        additional_params = {
            'q.op': 'AND',
        }

        self.facets = filter(self.is_field_allowed, params.get('facets', []))
        facet_fields = map(self.get_field_index, self.facets)

        if facet_fields:
            additional_params["facet"] = "true"
            additional_params["facet.mincount"] = 1
            additional_params["facet.field"] = facet_fields
        return additional_params

    @with_active_solr_only
    def reply(self):
        self.listing_name = self.request.form.get('name')
        if self.listing_name not in FILTERS:
            raise BadRequest

        self.solr = getUtility(ISolrSearch)

        query, filters, start, rows, sort, field_list, params = self.prepare_solr_query()

        resp = self.solr.search(
            query=query, filters=filters, start=start, rows=rows, sort=sort,
            fl=field_list, **params)

        # We use the HypermediaBatch only to generate the links,
        # we therefore do not need the real sequence of objects here
        items = LazyMap(None, [], actual_result_count=resp.num_found)
        batch = HypermediaBatch(self.request, items)
        res = {}
        res['@id'] = batch.canonical_url
        res['items_total'] = batch.items_total
        res['b_start'] = start
        res['b_size'] = rows
        if batch.links:
            res['batching'] = batch.links

        res['items'] = self.prepare_response_items(resp)

        facet_counts = self.extract_facets_from_response(resp)

        # We map the index names back to the field names for the facets
        mapped_facet_counts = {}
        for field in self.facets:
            index_name = self.get_field_index(field)
            if index_name is None or index_name not in facet_counts:
                continue
            mapped_facet_counts[field] = facet_counts[index_name]
        res['facets'] = mapped_facet_counts

        return res

    def parse_dates(self, value):
        if isinstance(value, list):
            value = value[0]
        if not isinstance(value, str):
            return None, None

        dates = value.split('TO')
        if len(dates) == 2:
            try:
                date_from = DateTime(dates[0]).earliestTime()
                date_to = DateTime(dates[1]).latestTime()
            except DateTimeError:
                return None, None
        return date_from, date_to

    def is_field_allowed(self, field):
        return field in self.allowed_fields

    def daterange_filter(self, value):
        date_from, date_to = self.parse_dates(value)
        if date_from is not None and date_to is not None:
            return u'[{} TO {}]'.format(
                to_iso8601(date_from), to_iso8601(date_to))
