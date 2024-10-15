from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import ensure_text
from ftw.solr.query import escape
from ftw.solr.query import make_filters
from ftw.solr.query import make_path_filter
from opengever.api.breadcrumbs import Breadcrumbs
from opengever.api.linked_workspaces import teamraum_request_error_handler
from opengever.api.listing import FILTERS
from opengever.api.solr_query_service import LiveSearchQueryPreprocessingMixin
from opengever.api.solr_query_service import SolrFieldMapper
from opengever.api.solr_query_service import SolrQueryBaseService
from opengever.api.utils import recursive_encode
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.browser.reporting_view import SolrReporterView
from opengever.base.interfaces import ISearchSettings
from opengever.base.reporter import DATE_NUMBER_FORMAT
from opengever.base.reporter import readable_actor
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.base.solr import OGSolrContentListing
from opengever.base.solr.fields import DEFAULT_SORT_INDEX
from opengever.base.solr.fields import relative_to_physical_path
from opengever.base.solr.fields import SolrFieldMapper
from opengever.base.solr.fields import url_to_physical_path
from opengever.base.utils import rewrite_path_list_to_absolute_paths
from opengever.base.utils import safe_int
from opengever.dossier import _
from opengever.workspaceclient.client import WorkspaceClient
from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zExceptions import InternalError


BLACKLISTED_ATTRIBUTES = set([
    'getDataOrigin',
    'getObject',
    'getUserData',
    'SearchableText',
    'SearchableText_de',
    'SearchableText_en',
    'SearchableText_fr',
    'SearchableText_general',
    'allowedRolesAndUsers',
])


class SolrSearchFieldMapper(SolrFieldMapper):

    def is_allowed(self, field_name):
        """Do not allow private or blacklisted attributes.
        """
        if field_name.startswith("_") or field_name in BLACKLISTED_ATTRIBUTES:
            return False
        return True


class SolrSearchGet(SolrQueryBaseService):
    """REST API endpoint for querying Solr
    """

    field_mapper = SolrSearchFieldMapper

    def __init__(self, context, request):
        super(SolrSearchGet, self).__init__(context, request)
        self.show_breadcrumbs = self.extract_show_breadcrumb()

    def extract_show_breadcrumb(self):
        """Extract breadcrumbs flag and checks if the batchsize is
        not higher than 50 when enabled."""

        show_breadcrumbs = bool(self.request_payload.get('breadcrumbs', False))
        if show_breadcrumbs:
            if self.request_payload.get('b_size', 0) > 50:
                raise BadRequest('Breadcrumb flag is only allowed for '
                                 'small batch sizes (max. 50).')
        return show_breadcrumbs

    def extract_query(self, params):
        if 'q' in params:
            query = params['q']
            del params['q']
        elif 'q.raw' in params:
            query = params['q.raw']
            del params['q.raw']
        else:
            query = '*'
        return query

    @staticmethod
    def preprocess_query(query):
        return query

    def extract_filters(self, params):
        if 'fq' in params:
            filters = params['fq']
            if isinstance(filters, basestring):
                filters = [filters]
            del params['fq']
        else:
            filters = []

        self.add_path_parent_filters(filters)
        self.add_url_path_parent_filters(filters)
        self.add_path_filters(filters, params)
        self.add_url_path_filters(filters)
        self.add_portal_types_filter(filters)

        return filters

    def add_path_parent_filters(self, filters):
        """A frontend usualy only knows the virtual path, not the real physical path
        of an object. But the solr index value contains the physical path of
        the object. Thus, we need to replace the paths relative to the virtual root
        with the physical path of an object.

        In addition, it joins multiple path_parent filters with an OR operator which
        makes it possible to query for multiple path_parents
        """
        requested_parent_paths = []
        for query in list(filters):
            if not query.startswith("path_parent:"):
                continue

            # extract the path from the query and unescape
            path = query.split(":", 1)[1].replace('\\', '')

            # A frontend does not know anything about the physical path of an object.
            # We have to take care of this by resolve the relative path to a physical path
            # which is required by solr.
            physical_path = relative_to_physical_path(path)

            requested_parent_paths.append(physical_path)
            filters.remove(query)

        if (requested_parent_paths):
            filters.extend(make_filters(path_parent=requested_parent_paths))

    def add_url_path_filters(self, filters):
        self.add_url_filters(filters, ['@id:', 'url:'], 'path')

    def add_url_path_parent_filters(self, filters):
        self.add_url_filters(filters, ['@id_parent:', 'url_parent:'], 'path_parent')
        self.add_url_filters(filters, ['-@id_parent:', '-url_parent:'], '-path_parent')

    def add_url_filters(self, filters, query_prefix, filter_name,):
        """Beside the 'path' filter, we provide an 'url' (alias '@id')
        filter to filter by specific urls.

        Usualy, a frontend does not know the physical path of a resource but it always
        knows the url (@id) of a resource. So this filter can be used to directly
        fetching specific objects by their 'url'.
        """
        requested_paths = []
        for query in list(filters):
            if not (any([query.startswith(query_name) for query_name in query_prefix])):
                continue

            # extract the @id from the query and unescape
            url = query.split(":", 1)[1].replace('\\', '')
            path = url_to_physical_path(url)

            if not path:
                continue

            filters.remove(query)
            requested_paths.append(path)

        if (requested_paths):
            escaped_path_query = escape(u' OR '.join(ensure_text(requested_paths)))
            filters.append(u'{}:({})'.format(filter_name, escaped_path_query))

    def extract_path_filter_value(self, filters):
        """If path is not specified we search in the current context
        """
        for query in filters:
            if query.startswith("path:"):
                path = query.rsplit(":", 1)[1]
                filters.remove(query)
                return path
        return '/'.join(self.context.getPhysicalPath())

    def add_path_filters(self, filters, params):
        depth = self.extract_depth(params)
        path = self.extract_path_filter_value(filters)
        filters.extend(make_path_filter(path, depth))

    def contains_portal_types_filter(self, filters):
        for query in filters:
            if query.startswith("portal_type:"):
                return True
        return False

    def add_portal_types_filter(self, filters):
        """If portal_types is not specified we respect the UserFriendlyTypes,
        i.e. we notably exclude the WorkspaceMeetingAgendaItems
        """
        if not self.contains_portal_types_filter(filters):
            plone_utils = getToolByName(self.context, 'plone_utils')
            types = plone_utils.getUserFriendlyTypes()
            filters.append('portal_type:({})'.format(' OR '.join(types)))

    def extract_sort(self, params, query):
        if 'sort' in params:
            sort = params['sort']
            del params['sort']
        else:
            if query == '*':
                sort = None
            else:
                sort = 'score desc'
        return self.extend_with_group_by_type(sort, params)

    def extend_with_group_by_type(self, sort, params):
        group_by_type = params.get('group_by_type', {})

        if not group_by_type:
            return sort
        del params['group_by_type']
        if isinstance(group_by_type, str):
            group_by_type = [group_by_type]
        if not sort:
            return self._build_group_by_type_function_query_string(group_by_type)
        return '{},{}'.format(self._build_group_by_type_function_query_string(group_by_type), sort)

    @staticmethod
    def _build_group_by_type_function_query_string(group_by_type):
        max_score = len(group_by_type)
        query_string = u''

        for index, name in enumerate(group_by_type):
            if name not in FILTERS:
                raise BadRequest("group_by_type type '{}' is not allowed. "
                                 "Allowed types are: {}.".format(name, ', '.join(FILTERS)))

            interface = FILTERS[name][0].replace('object_provides:', '')
            query_string += u'if(termfreq(object_provides,{}),{},'.format(interface,
                                                                          (max_score - index))
        return '{}0{}{}'.format(query_string, ')' * max_score, u' desc')

    def parse_requested_fields(self, params):
        requested_fields = params.pop('fl', None)
        if requested_fields:
            requested_fields = requested_fields.split(',')
            if 'is_leafnode' in requested_fields:
                # Requesting additional fields is required in order to determine if
                # the repository folder is a leaf node.
                requested_fields.extend(['@type', 'has_sametype_children'])

        return requested_fields

    def extract_field_list(self, params):
        """Add path to the field list, if breadcrumb flag is on. It's used for
        breadcrumb generation
        """
        fields = super(SolrSearchGet, self).extract_field_list(params)

        if self.show_breadcrumbs and 'path' not in fields:
            fields.append('path')

        return fields

    def prepare_additional_params(self, params):
        facet_fields = params.get('facet.field', [])
        if not isinstance(facet_fields, list):
            facet_fields = [facet_fields]
        if facet_fields:
            self.facets = [facet for facet in facet_fields
                           if self.fields.is_allowed(facet)
                           and self.fields.get(facet).index in self.fields.all_solr_fields]
            params['facet.field'] = [self.fields.get(f).index for f in self.facets]

        stats_fields = params.pop('stats.field', [])
        if not isinstance(stats_fields, list):
            stats_fields = [stats_fields]
        if stats_fields:
            self.stats_fields = [
                stats_field for stats_field in stats_fields
                if self.fields.is_allowed(stats_field)
                and stats_field in self.fields.all_solr_fields
            ]
            params['stats.field'] = self.stats_fields

        return params

    def reply(self):
        if not api.portal.get_registry_record(
                'use_solr', interface=ISearchSettings):
            raise BadRequest('Solr is not enabled on this GEVER installation.')

        query, filters, start, rows, sort, field_list, params = \
            self.prepare_solr_query(self.request_payload)

        resp = self.solr.search(
            query=query, filters=filters, start=start, rows=rows, sort=sort,
            fl=field_list, **params)

        if not resp.is_ok():
            raise InternalError(resp.error_msg())

        res = {
            "items": self.prepare_response_items(resp),
            "start": start,
            "rows": rows,
            "facet_counts": self.extract_facets_from_response(resp)
        }
        # flatten stats and only return field stats if they were requested
        stats = resp.get('stats', {}).get('stats_fields')
        if stats:
            res['stats'] = stats
        self.extend_with_batching(res, resp)

        return res

    def _create_list_item(self, doc):
        """Extend object data with breadcrumb information if 'breadcrumbs' flag
        is true."""

        data = super(SolrSearchGet, self)._create_list_item(doc)

        if self.show_breadcrumbs:
            path = getattr(doc, 'path', None)
            obj = api.portal.get().unrestrictedTraverse(path.encode('utf-8'))
            data['breadcrumbs'] = Breadcrumbs(
                obj, self.request).get_serialized_breadcrumbs()

        return data


class SolrLiveSearchGet(LiveSearchQueryPreprocessingMixin, SolrSearchGet):
    """REST API endpoint for querying Solr
    """

    def reply(self):
        if self.request_payload.get("only_preprocess_query"):
            return {"preprocessed_query": self.preprocess_query(
                self.extract_query(self.request_payload))}
        return super(SolrLiveSearchGet, self).reply()


class SolrLiveSearchGetDossier(SolrLiveSearchGet):
    """REST API endpoint for querying Solr Dossier
    """
    filename = 'dossier_report.xlsx'
    column_settings = (
        {
            'id': 'title',
            'is_default': True,
        },
    )

    def reply(self):
        if not api.portal.get_registry_record(
                'use_solr', interface=ISearchSettings):
            raise BadRequest('Solr is not enabled on this GEVER installation.')


        query, filters, start, rows, sort, field_list, params = \
            self.prepare_solr_query(self.request_payload)

        resp = self.solr.search(
            query=query, filters=filters, start=start, rows=rows, sort=sort,
            fl=field_list, **params)

        if not resp.is_ok():
            raise InternalError(resp.error_msg())

        res = {
            "items": self.prepare_response_items(resp),
            "start": start,
            "rows": rows,
            "facet_counts": self.extract_facets_from_response(resp)
        }
        # flatten stats and only return field stats if they were requested
        stats = resp.get('stats', {}).get('stats_fields')
        if stats:
            res['stats'] = stats
        self.extend_with_batching(res, resp)
        reporter = XLSReporter(self.request, self.column_settings, res['items'])
        import pdb
        pdb.set_trace()
        data = reporter()
        response = self.request.RESPONSE
        response.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        set_attachment_content_disposition(self.request, self.filename)

        return response


class TeamraumSolrSearchGet(Service):

    @teamraum_request_error_handler
    def reply(self):
        # Validation will be done on the remote system
        params = self.request.form.copy()
        return WorkspaceClient().solrsearch(**params)
