from ftw.solr.query import make_path_filter
from ftw.solr.query import make_query
from opengever.api.solr_query_service import SolrQueryBaseService
from opengever.base.interfaces import ISearchSettings
from plone import api
from zExceptions import BadRequest


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

        res = {
            "@id": "{}?{}".format(
                self.request['ACTUAL_URL'], self.request['QUERY_STRING']),
            "items": self.prepare_response_items(resp),
            "items_total": resp.num_found,
            "start": start,
            "rows": rows,
        }
        res['facet_counts'] = self.extract_facets_from_response(resp)

        return res

    def is_field_allowed(self, field):
        """Do not allow private or blacklisted attributes"""
        if field.startswith("_") or field in BLACKLISTED_ATTRIBUTES:
            return False
        return True
