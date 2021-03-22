from ftw.solr.query import escape
from ftw.solr.query import make_path_filter
from opengever.api.solr_query_service import REQUIRED_RESPONSE_FIELDS as DEFAULT_REQUIRED_RESPONSE_FIELDS
from opengever.api.solr_query_service import SolrQueryBaseService
from opengever.base.interfaces import ISearchSettings
from opengever.dossier.indexers import ParticipationIndexHelper
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from zExceptions import BadRequest
from zope.component import getUtility
from ZPublisher.HTTPRequest import record


# Fields with no mapping but allowed in the listing endpoint.
OTHER_ALLOWED_FIELDS = set([
    'blocked_local_roles',
    'changed',
    'checked_out',
    'completed',
    'containing_dossier',
    'containing_subdossier',
    'created',
    'deadline',
    'delivery_date',
    'document_author',
    'document_date',
    'document_type',
    'email',
    'end',
    'external_reference',
    'file_extension',
    'firstname',
    'getObjPositionInParent',
    'has_sametype_children',
    'is_subdossier',
    'is_subtask',
    'id',
    'lastname',
    'language',
    'location',
    'modified',
    'phone_office',
    'preselected',
    'receipt_date',
    'reference',
    'responsible',
    'review_state',
    'sequence_number',
    'start',
    'trashed',
    'UID',
    'watchers',
])

ALLOWED_ORDER_GROUP_FIELDS = set([
    'portal_type'
])

FILTERS = {
    u'dossiers': [
        u'object_provides:opengever.dossier.behaviors.dossier.IDossierMarker',
    ],
    u'dossiertemplates': [
        u'object_provides:opengever.dossier.dossiertemplate.behaviors.IDossierTemplateSchema',
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
    u'workspace_meetings': [
        u'object_provides:opengever.workspace.interfaces.IWorkspaceMeeting',
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
    ],
    u'tasktemplates': [
        u'object_provides:opengever.tasktemplates.content.tasktemplate.ITaskTemplate',
    ],
    u'tasktemplate_folders': [
        u'object_provides:opengever.tasktemplates.content.templatefoldersschema.ITaskTemplateFolderSchema',
    ],
    u'folder_contents': [
        u'object_provides:plone.dexterity.interfaces.IDexterityContent'
    ]
}


REQUIRED_RESPONSE_FIELDS = DEFAULT_REQUIRED_RESPONSE_FIELDS.union(set(['@id']))


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


class ListingGet(SolrQueryBaseService):
    """List of content items"""

    required_response_fields = REQUIRED_RESPONSE_FIELDS
    other_allowed_fields = OTHER_ALLOWED_FIELDS

    def __init__(self, context, request):
        super(ListingGet, self).__init__(context, request)
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

        depth = self.extract_depth(params)
        filter_queries.extend(make_path_filter(
            '/'.join(self.context.getPhysicalPath()), depth))

        # Add requested filters
        filters = self.preprocess_filters(filters)
        for key, value in filters.items():
            field = self.get_field(key)
            solr_filter = field.listing_to_solr_filter(value)
            if solr_filter:
                filter_queries.append(solr_filter)
        return filter_queries

    def preprocess_filters(self, filters):
        filters = dict(filters)
        if 'participations' in filters and ('participants' in filters
                                            or 'participation_roles' in filters):
            raise BadRequest(
                "Cannot set participations filter together with participants "
                "or participation_roles filters.")

        if 'participants' in filters and 'participation_roles' in filters:
            helper = ParticipationIndexHelper()
            participant_id_filters = filters.pop('participants')
            role_filters = filters.pop('participation_roles')
            participations = []
            for id_filter in participant_id_filters:
                participant_id = helper.index_value_to_participant_id(id_filter)
                for role_filter in role_filters:
                    role = helper.index_value_to_role(role_filter)
                    participations.append(
                        helper.participant_id_and_role_to_index_value(
                            participant_id, role))
            filters['participations'] = participations
        return filters

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

        return self.extend_with_sort_first(sort, params)

    def extend_with_sort_first(self, sort, params):
        """The sort_first sorts docs in two steps. First, it will sort
        all items having one of the provided values of a defined field first.
        All other docs will be put into the second group. Each group will then
        be sorted by the `sort_on`.

        Having a result of the following docs ordered by sortable_title:

        { 'portal_type': 'type1', title: 'A' }
        { 'portal_type': 'type2', title: 'B' }
        { 'portal_type': 'type2', title: 'C' }
        { 'portal_type': 'type3', title: 'D' }
        { 'portal_type': 'type1', title: 'E' }
        { 'portal_type': 'type4', title: 'F' }

        Can be grouped i.e. by type:

        { 'portal_type': ['type1', type3'] }

        which will result in the following sort order:

        { 'portal_type': 'type1', title: 'A' } <= Group 1
        { 'portal_type': 'type3', title: 'D' }
        { 'portal_type': 'type1', title: 'E' }
        { 'portal_type': 'type2', title: 'B' } <= Group 2
        { 'portal_type': 'type2', title: 'C' }
        { 'portal_type': 'type4', title: 'F' }
        """
        sort_first = params.get('sort_first', {})

        if not sort_first:
            return sort

        if not isinstance(sort_first, record):
            raise BadRequest('The sort_first parameter needs to be a record.')

        if len(sort_first) > 1:
            raise BadRequest('Exactly one sort_first field is required.')

        # Currently, only one sort_first field is implemented. Thus, we just
        # extract the first item and use this for further processing.
        field_name, field_values = sort_first.items()[0]

        if not field_values:
            return sort

        if isinstance(field_values, str):
            field_values = [field_values]

        if field_name not in ALLOWED_ORDER_GROUP_FIELDS:
            raise BadRequest(
                'Sort first field {} is not allowed. Allowed fields are: '
                '{}.'.format(field_name,
                             ','.join(ALLOWED_ORDER_GROUP_FIELDS)))

        return ','.join([self._build_sort_first_func_string(field_name, field_values), sort])

    @staticmethod
    def _build_sort_first_func_string(field_name, field_values):
        """Generates a solr function string to order by a group of values of
        a specific field.

        We achieve this by giving each solr-document a number of either 1 or 0,
        depending on the field content and then sort by this number.

        A conditional function query looks like this `if(test, value1, value2)`

        The `termfreq`-function returns the number of times a term appears in
        the field for each document. It allows to check whether any of
        the field_values are included in the document's field value.
        """
        field_value_conditions = []
        for field_value in field_values:
            field_value_conditions.append(
                'termfreq({}, {})'.format(field_name, field_value))

        return 'if(or({}), 1, 0) desc'.format(','.join(field_value_conditions))

    def parse_requested_fields(self, params):
        return params.get('columns', None)

    def prepare_additional_params(self, params):
        """ Extract the requested facet fields and prepare the
        corresponding parameters for the solr query.
        """
        additional_params = {
            'q.op': 'AND',
        }

        self.facets = [facet for facet in params.get('facets', [])
                       if self.is_field_allowed(facet)
                       and self.get_field_index(facet) in self.solr_fields]
        facet_fields = map(self.get_field_index, self.facets)

        if facet_fields:
            additional_params["facet"] = "true"
            additional_params["facet.mincount"] = 1
            additional_params["facet.field"] = facet_fields
            additional_params['facet.limit'] = -1
        return additional_params

    @with_active_solr_only
    def reply(self):
        self.listing_name = self.request.form.get('name')
        if self.listing_name not in FILTERS:
            raise BadRequest(
                "Unknown listing {}. Available listings are: {}".format(
                    self.name, ",".join(FILTERS.keys())))

        query, filters, start, rows, sort, field_list, params = self.prepare_solr_query()

        resp = self.solr.search(
            query=query, filters=filters, start=start, rows=rows, sort=sort,
            fl=field_list, **params)

        res = {}
        self.extend_with_batching(res, resp)
        res['b_start'] = start
        res['b_size'] = rows
        res['items'] = self.prepare_response_items(resp)
        res['facets'] = self.extract_facets_from_response(resp)

        return res

    def is_field_allowed(self, field):
        return field in self.allowed_fields
