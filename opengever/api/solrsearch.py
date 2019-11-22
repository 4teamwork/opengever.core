from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_query
from opengever.api.listing import FACET_TRANSFORMS
from opengever.api.solr_query_service import SolrQueryBaseService
from opengever.base.interfaces import ISearchSettings
from opengever.base.solr import OGSolrContentListing
from plone import api
from plone.restapi.serializer.converters import json_compatible
from zExceptions import BadRequest
from zope.component import getUtility


DEFAULT_FIELDS = set([
    '@id',
    '@type',
    'title',
    'description',
    'review_state',
])

# Field name -> (Solr field, accessor)
FIELD_MAPPING = {
    "@id": ("path", "getURL"),
    "@type": ("portal_type", "PortalType"),
    "title": ("Title", "Title"),
    "description": ("Description", "Description"),
}

BLACKLISTED_ATTRIBUTES = set([
    'getDataOrigin',
    'getObject',
    'getUserData',
    'SearchableText',
    'allowedRolesAndUsers',
])

REQUIRED_FIELDS = set([
    'UID',
    'path',
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
            del params['fq']
        else:
            filters = []
        return filters

    def extract_sort(self, params, query):
        if 'sort' in params:
            sort = params['sort']
            del params['sort']
        else:
            if query == '*:*':
                sort = None
            else:
                sort = 'score asc'
        return sort

    def extract_field_list(self, params):
        self.requested_fields = params.pop('fl', None)
        if self.requested_fields:
            self.requested_fields = (
                set(self.requested_fields.split(',')) - BLACKLISTED_ATTRIBUTES)
        else:
            self.requested_fields = DEFAULT_FIELDS

        solr_fields = set(self.solr.manager.schema.fields.keys())
        requested_solr_fields = set([])
        for field in self.requested_fields:
            if field in FIELD_MAPPING:
                field = FIELD_MAPPING[field][0]
            requested_solr_fields.add(field)
        return ','.join(
            (requested_solr_fields | REQUIRED_FIELDS) & solr_fields)

    def reply(self):
        if not api.portal.get_registry_record(
                'use_solr', interface=ISearchSettings):
            raise BadRequest('Solr is not enabled on this GEVER installation.')

        self.solr = getUtility(ISolrSearch)

        query, filters, start, rows, sort, field_list, params = self.prepare_solr_query()

        resp = self.solr.search(
            query=query, filters=filters, start=start, rows=rows, sort=sort,
            fl=field_list, **params)

        docs = OGSolrContentListing(resp)
        items = []
        for doc in docs:
            item = {}
            for field in self.requested_fields:
                # Do not allow access to private attributes
                if field.startswith("_"):
                    continue
                accessor = FIELD_MAPPING.get(field, (None, field))[1]
                value = getattr(doc, accessor, None)
                if callable(value):
                    value = value()
                item[field] = json_compatible(value)
            items.append(item)

        res = {
            "@id": "{}?{}".format(
                self.request['ACTUAL_URL'], self.request['QUERY_STRING']),
            "items": items,
            "items_total": resp.num_found,
            "start": start,
            "rows": rows,
        }

        facet_counts = {}
        for field, facets in resp.facets.items():
            facet_counts[field] = {}
            transform = FACET_TRANSFORMS.get(field)
            for facet, count in facets.items():
                facet_counts[field][facet] = {"count": count}
                if transform:
                    facet_counts[field][facet]['label'] = transform(facet)
                else:
                    facet_counts[field][facet]['label'] = facet
        res['facet_counts'] = facet_counts
        return res
