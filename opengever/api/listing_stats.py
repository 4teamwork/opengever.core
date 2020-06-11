from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import escape
from opengever.api.listing import FILTERS
from opengever.api.listing import get_path_depth
from opengever.base.interfaces import IOpengeverBaseLayer
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class ListingStats(object):
    """Returns a facet pivot of the current object.

    The format is based on the solr facet pivot format:
    https://lucene.apache.org/solr/guide/6_6/faceting.html#Faceting-facet.pivot

    {
        "@id": '/@listing-stats',
        "facet_pivot": {
            "pivot_name": [
                {
                    "field": "fieldname",
                    "count": 0,
                    "value": "value",
                    "pivot": [...]
                }
            ]
        }

    }
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

        queries = self.request.form.get("queries", [])
        if isinstance(queries, basestring):
            queries = [queries]
        self.facet_queries = [self._escape_query(query) for query in queries]

        self.solr = getUtility(ISolrSearch)

    @staticmethod
    def _escape_query(query):
        return u":".join(escape(safe_unicode(el)) for el in query.split(":"))

    def __call__(self, expand=False):
        result = {
            'listing-stats': {
                '@id': '{}/@listing-stats'.format(self.context.absolute_url()),
            },
        }

        if not expand:
            return result

        result['listing-stats']['facet_pivot'] = self.get_pivots()

        return result

    def get_pivots(self):
        """Returns a dict of pivots.
        """
        pivots = {}
        pivots.update(self._get_listing_name_pivot())
        return pivots

    def _get_listing_name_pivot(self):
        """Returns the `listing_name` pivot section which depends on the FILTER
        values of the @listing endpoint.
        """
        solr_pivot = 'object_provides'
        response = self._fetch_solr_stats(solr_pivot)

        listing_name_pivot = self._create_listing_name_pivot(response, solr_pivot)
        listing_name_pivot_name = solr_pivot.replace('object_provides', 'listing_name')

        return {listing_name_pivot_name: listing_name_pivot}

    def _fetch_solr_stats(self, pivot):
        """Queries the solr with a pivot search query.

        This allows to get a hierarchy of values for fields and subfields.

        The Pivot-Result looks like:

        {
          "facet_counts":{
            "facet_pivot":{
              "object_provides,review_state":[
                {
                  "field":"object_provides",
                  "value":"opengever.document.behaviors.IBaseDocument",
                  "count":310,
                  "queries": {
                    "{!tag=q1}responsible:hugo.boss":1
                  },
                  "pivot":[
                    {
                      "field":"review_state",
                      "value":"document-state-draft",
                      "count":310,
                      "queries": {
                        "{!tag=q1}responsible:hugo.boss":1
                      },
                    }
                  ]
                }
              ]
            }
          }
        }

        Caution: The current implementation could easely be done with a default
        facet search query. But we need to extend it later with substatistics,
        i.e. the review-states for a specific type. The current implementation
        already takes care of this future improvement.
        """
        fq = [
            'trashed:false',
            'path_parent:{}/*'.format(escape(
                '/'.join(self.context.getPhysicalPath())))
        ]

        params = {
            'facet': True,
            'rows': 0,
            'facet.pivot': pivot,
        }

        if self.facet_queries:
            facet_queries = [self._to_solr_facet_query(query)
                             for query in self.facet_queries]
            params['facet.pivot'] = self._add_query_to_pivot(pivot)
            params['facet.query'] = facet_queries
        return self.solr.search(filters=fq, **params)

    def _to_solr_facet_query(self, query):
        if query.startswith("depth:"):
            try:
                depth = int(query.rsplit(":", 1)[1])
            except (ValueError, IndexError):
                raise BadRequest("Could not parse depth query: {}".format(query))

            context_depth = get_path_depth(self.context)
            max_path_depth = context_depth + depth
            return "{{!tag=q1}}path_depth:[* TO {}]".format(max_path_depth)
        return "{{!tag=q1}}{}".format(query)

    @staticmethod
    def _add_query_to_pivot(pivot):
        return "{{!query=q1}}{}".format(pivot)

    def _create_listing_name_pivot(self, solr_response, pivot):
        """Processes solr_response to extract the statistics and format them
        for output:

        Input solr_response:
        {
          "facet_counts":{
            "facet_pivot":{
              "object_provides":[
                {
                  "field":"object_provides",
                  "value":"opengever.document.behaviors.IBaseDocument",
                  "count":310,
                  "queries": {
                    "{!tag=q1}responsible:hugo.boss":1
                  },
                },
              ]
            }
          }
        }

        Output:
        {
          "facet_pivot":{
            "listing_name": [
              {
                "field":"documents",
                "value":"opengever.document.behaviors.IBaseDocument",
                "count":310,
                "queries":{
                  "responsible:hugo.boss":1,
                },
              }
            ]
          }
        }

        """
        pivots = solr_response.get(
            'facet_counts', {}).get(
            'facet_pivot', {}).get(pivot)

        pivot_by_value = self._pivots_by_value(pivots)

        pivots = []
        for listing_name, filter_queries in FILTERS.items():

            if len(filter_queries) > 1:
                raise NotImplementedError("Can't handle multiple filter queries.")

            pivot_field, pivot_value = filter_queries[0].split(':')
            pivot = pivot_by_value.get(pivot_value, {})
            if not pivot:
                pivot = {'count': 0}

            if self.facet_queries:
                # Remove the tag from the facet query names:
                # {!tag=q1}responsible:hugo.boss -> responsible:hugo.boss
                pivot['queries'] = {
                    facet_query: pivot.get('queries', {}).get(
                        self._to_solr_facet_query(facet_query), 0)
                    for facet_query in self.facet_queries
                }

            pivot['field'] = 'listing_name'
            pivot['value'] = listing_name
            pivots.append(pivot)
        return pivots

    def _pivots_by_value(self, pivots):
        """Transforms a list of solr pivots into a dictionary with pivot
        values as keys:

        Input pivots:
        [
          {
            "field":"object_provides",
            "value":"opengever.document.behaviors.IBaseDocument",
            "count":310
          }
        ]

        Output:
        {
          "opengever.document.behaviors.IBaseDocument": {
            "field":"object_provides",
            "value":"opengever.document.behaviors.IBaseDocument",
            "count":310
          }
        }
        """
        pivot_dict = {}
        for pivot in pivots:
            pivot_dict[pivot.get('value')] = pivot
        return pivot_dict


class ListingStatsGet(Service):
    """API Endpoint which returns a solr facet_pivot for listings.

    GET folder-1/@listing-stats HTTP/1.1
    """

    def reply(self):
        stats = ListingStats(self.context, self.request)
        return stats(expand=True)['listing-stats']
