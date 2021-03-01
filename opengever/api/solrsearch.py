from ftw.solr.query import make_path_filter
from ftw.solr.query import make_query
from opengever.api.breadcrumbs import Breadcrumbs
from opengever.api.linked_workspaces import request_error_handler
from opengever.api.solr_query_service import SolrQueryBaseService
from opengever.base.interfaces import ISearchSettings
from opengever.workspaceclient.client import WorkspaceClient
from plone import api
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import InternalError

BLACKLISTED_ATTRIBUTES = set([
    'getDataOrigin',
    'getObject',
    'getUserData',
    'SearchableText',
    'allowedRolesAndUsers',
])


class SolrSearchGet(SolrQueryBaseService):
    """REST API endpoint for querying Solr
    """

    def __init__(self, context, request):
        super(SolrSearchGet, self).__init__(context, request)
        self.show_breadcrumbs = self.extract_show_breadcrumb()

    def extract_show_breadcrumb(self):
        """Extract breadcrumbs flag and checks if the batchsize is
        not higher than 50 when enabled."""

        show_breadcrumbs = bool(self.request.form.get('breadcrumbs', False))
        if show_breadcrumbs:
            if self.request.form.get('b_size', 0) > 50:
                raise BadRequest('Breadcrumb flag is only allowed for '
                                 'small batch sizes (max. 50).')
        return show_breadcrumbs

    def extract_query(self, params):
        if 'q' in params:
            query = make_query(params['q'])
            del params['q']
        elif 'q.raw' in params:
            query = params['q.raw']
            del params['q.raw']
        else:
            query = '*:*'
        return query

    def extract_filters(self, params):
        if 'fq' in params:
            filters = params['fq']
            if isinstance(filters, basestring):
                filters = [filters]
            del params['fq']
        else:
            filters = []

        self.add_path_filters(filters, params)

        return filters

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

    def extract_sort(self, params, query):
        if 'sort' in params:
            sort = params['sort']
            del params['sort']
        else:
            if query == '*:*':
                sort = None
            else:
                sort = 'score desc'
        return sort

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
                           if self.is_field_allowed(facet)
                           and self.get_field_index(facet) in self.solr_fields]
            params['facet.field'] = map(self.get_field_index, self.facets)
        return params

    def reply(self):
        if not api.portal.get_registry_record(
                'use_solr', interface=ISearchSettings):
            raise BadRequest('Solr is not enabled on this GEVER installation.')

        query, filters, start, rows, sort, field_list, params = self.prepare_solr_query()

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
        self.extend_with_batching(res, resp)

        return res

    def is_field_allowed(self, field):
        """Do not allow private or blacklisted attributes"""
        if field.startswith("_") or field in BLACKLISTED_ATTRIBUTES:
            return False
        return True

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


class TeamraumSolrSearchGet(Service):

    @request_error_handler
    def reply(self):
        # Validation will be done on the remote system
        params = self.request.form.copy()
        return WorkspaceClient().solrsearch(**params)
