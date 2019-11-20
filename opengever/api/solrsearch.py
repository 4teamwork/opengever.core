from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_query
from opengever.api.listing import FACET_TRANSFORMS
from opengever.base.interfaces import ISearchSettings
from opengever.base.solr import OGSolrContentListing
from plone import api
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
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


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


class SolrSearchGet(Service):
    """REST API endpoint for querying Solr
    """

    def make_solr_query(self):
        params = self.request.form.copy()

        if 'q' in params:
            query = make_query(params['q'])
            del params['q']
        elif 'q.raw' in params:
            query = params['q.raw']
            del params['q.raw']
        else:
            query = '*:*'

        if 'fq' in params:
            filters = params['fq']
            del params['fq']
        else:
            filters = []

        if 'start' in params:
            start = safe_int(params['start'])
            del params['start']
        else:
            start = 0

        if 'rows' in params:
            rows = min(safe_int(params['rows'], 25), 1000)
            del params['rows']
        else:
            rows = 25

        if 'sort' in params:
            sort = params['sort']
            del params['sort']
        else:
            if query == '*:*':
                sort = None
            else:
                sort = 'score asc'

        return query, filters, start, rows, sort, params

    def reply(self):
        if not api.portal.get_registry_record(
                'use_solr', interface=ISearchSettings):
            raise BadRequest('Solr is not enabled on this GEVER installation.')

        query, filters, start, rows, sort, params = self.make_solr_query()

        requested_fields = params.get('fl')
        if requested_fields:
            requested_fields = (
                set(requested_fields.split(',')) - BLACKLISTED_ATTRIBUTES)
        else:
            requested_fields = DEFAULT_FIELDS

        solr = getUtility(ISolrSearch)
        solr_fields = set(solr.manager.schema.fields.keys())
        requested_solr_fields = set([])
        for field in requested_fields:
            if field in FIELD_MAPPING:
                field = FIELD_MAPPING[field][0]
            requested_solr_fields.add(field)
        params['fl'] = ','.join(
            (requested_solr_fields | REQUIRED_FIELDS) & solr_fields)

        resp = solr.search(
            query=query, filters=filters, start=start, rows=rows, sort=sort,
            **params)

        docs = OGSolrContentListing(resp)
        items = []
        for doc in docs:
            item = {}
            for field in requested_fields:
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
