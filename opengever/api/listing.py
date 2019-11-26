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

        # By default exclude trashed content
        if 'trashed' not in filters:
            filter_queries.append(u'trashed:false')
        filter_queries.extend(FILTERS[self.listing_name])
        filter_queries.append(u'path_parent:{}'.format(escape(
            '/'.join(self.context.getPhysicalPath()))))

        # By default search recursively
        depth = self.request.form.get('depth', -1)
        try:
            depth = int(depth)
        except ValueError:
            depth = -1

        if depth > 0:
            context_depth = get_path_depth(self.context)
            max_path_depth = context_depth + depth
            filter_queries.append(u'path_depth:[* TO {}]'.format(max_path_depth))

        # Add requested filters
        for key, value in filters.items():
            field = self.get_field(key)
            solr_filter = field.listing_to_solr_filter(value)
            if solr_filter:
                filter_queries.append(solr_filter)
        return filter_queries

    def extract_sort(self, params, query):
        """ Extract the sort order, defaulting to sorting in descending
        order on self.default_sort_index
        """
        sort_on = params.get('sort_on', self.default_sort_index)
        if self.is_field_allowed(sort_on):
            sort_on = self.get_field_sort_index(sort_on)
        else:
            sort_on = self.default_sort_index

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
        """ Extract the requested facet fields and prepare the
        corresponding parameters for the solr query.
        """
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

    def is_field_allowed(self, field):
        return field in self.allowed_fields
