from ftw.solr.interfaces import ISolrSearch
from opengever.api.utils import recursive_encode
from opengever.base.solr import OGSolrContentListing
from opengever.base.solr.fields import DEFAULT_SORT_INDEX
from opengever.base.solr.fields import SolrFieldMapper
from opengever.base.utils import safe_int
from plone.memoize.view import memoize
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.ZCatalog.Lazy import LazyMap
from zExceptions import BadRequest
from zope.component import getUtility
import re


class RequestPayloadMixin:
    @property
    @memoize
    def request_payload(self):
        """Returns the request payload depending on the http request method.
        """
        if self.request.method == 'POST':
            # JSON always returns unicode strings. We need to encode the values
            # to utf-8 to get the same encoding as with a GET reqeust.
            return recursive_encode(json_body(self.request))
        else:
            return self.request.form


class SolrQueryBaseService(Service, RequestPayloadMixin):

    field_mapper = SolrFieldMapper

    def __init__(self, context, request):
        super(SolrQueryBaseService, self).__init__(context, request)
        self.solr = getUtility(ISolrSearch)
        self.fields = self.field_mapper(self.solr)

        self.default_sort_index = DEFAULT_SORT_INDEX
        self.response_fields = None
        self.facets = []

    def prepare_solr_query(self, params):
        """ Extract the requested parameters and prepare the solr query
        """
        params = params.copy()
        query = self.preprocess_query(self.extract_query(params))
        filters = self.extract_filters(params)
        start = self.extract_start(params)
        rows = self.extract_rows(params)
        sort = self.extract_sort(params, query)
        field_list = self.extract_field_list(params)
        additional_params = self.prepare_additional_params(params)
        return query, filters, start, rows, sort, field_list, additional_params

    def extract_start(self, params):
        """Solrsearch endpoint uses start while listing endpoint uses b_start
        """
        if 'start' in params:
            start = safe_int(params.pop('start'))
        elif 'b_start' in params:
            start = safe_int(params.pop('b_start'))
        else:
            start = 0
        return start

    def extract_rows(self, params):
        """Solrsearch endpoint uses rows while listing endpoint uses b_size
        """
        if 'rows' in params:
            rows = min(safe_int(params.pop('rows'), 25), 1000)
        elif 'b_size' in params:
            rows = min(safe_int(params.pop('b_size'), 25), 1000)
        else:
            rows = 25
        return rows

    def extract_query(self, params):
        return "*"

    @staticmethod
    def preprocess_query(query):
        return query

    def extract_filters(self, params):
        return []

    def extract_sort(self, params, query):
        return None

    def extract_facets_from_response(self, resp):
        """Extracts facets from solr response and prepares
        counts and labels for endpoint response.
        """
        facet_counts = {}
        for facet_name in self.facets:
            field = self.fields.get(facet_name)
            solr_facet_name = field.index
            solr_facet = resp.facets.get(solr_facet_name)

            if not solr_facet:
                continue

            facet_counts[facet_name] = {}
            for facet, count in solr_facet.items():
                if field.hide_facet(facet):
                    continue
                facet_counts[field.field_name][facet] = {
                    "count": count,
                    "label": field.safe_index_value_to_label(facet)
                }

        return facet_counts

    def parse_requested_fields(self, params):
        """Extracts requested fields from request
        """
        return []

    def extract_field_list(self, params):
        """Extracts fields from request and prepare the list
        of solr fields for the query and for the response.
        """
        requested_fields = self.parse_requested_fields(params)
        self.response_fields = self.fields.get_response_fields(requested_fields)
        return self.fields.get_query_fields(requested_fields)

    def extract_depth(self, params):
        """If depth is not specified we search recursively
        """
        # By default search recursively
        depth = params.get('depth', -1)
        try:
            depth = int(depth)
        except ValueError:
            raise BadRequest("Could not parse depth: {}".format(depth))
        return depth

    def prepare_additional_params(self, params):
        return params

    def _create_list_item(self, obj):
        """Gather requested data from an OGSolrContentListingObject in a dict.
        """
        data = {}
        for field_name in self.response_fields:
            value = self.fields.get(field_name).get_value(obj)
            data[field_name] = json_compatible(value)
        return data

    def prepare_response_items(self, resp):
        """Extract documents from the Sorl response and return a list
        of items containing the requested data"""
        docs = OGSolrContentListing(resp)
        items = []
        for doc in docs:
            items.append(self._create_list_item(doc))
        return items

    def extend_with_batching(self, response, solr_response):
        """Extends the current response-dict with batching links
        """
        # We use the HypermediaBatch only to generate the links,
        # we therefore do not need the real sequence of objects here
        items = LazyMap(None, [], actual_result_count=solr_response.num_found)
        batch = HypermediaBatch(self.request, items)

        response['@id'] = batch.canonical_url
        response['items_total'] = batch.items_total
        if batch.links:
            response['batching'] = batch.links


OPERATORS = ["and", "or", "&&", "||", "not", "!"]
IGNORED_TOKENS = ["/"]
TERM_SPLIT_TOKENS = [",", ";", r"\?", "!", "-", r"\+", "/", "\\\\", r"\|", "<", ">", "=", "%", "#", "@", "\\.", "_"]
ALPHA_NUM_SPLIT = r'(\d+)'
term_split_pattern = re.compile("|".join(TERM_SPLIT_TOKENS + [ALPHA_NUM_SPLIT]))
part_split_pattern = re.compile(r'; |, |\. |\s')


class LiveSearchQueryPreprocessingMixin(object):

    @staticmethod
    def _preprocess_term(term):
        if term.lower() in OPERATORS:
            return term
        if term in IGNORED_TOKENS:
            return None
        if len(term) == 1:
            return term
        prefix = ""
        term = term.rstrip(";,.")
        if term.startswith("-"):
            prefix = "-"
            term = term.lstrip("-")
        elif term.startswith("+"):
            prefix = "+"
            term = term.lstrip("+")
        tokens = ["{}{}".format(prefix, token)
                  for token in filter(None, term_split_pattern.split(term))]

        if not tokens:
            return None
        # Handle bracket and add wildcard to last token
        last_token = tokens[-1]
        n_brackets = len(last_token) - len(last_token.rstrip(")"))
        wildcard_token = "*" if len(last_token) > 1 else ""
        last_token = last_token.rstrip(")").rstrip("*") + wildcard_token + n_brackets * ")"
        tokens[-1] = last_token

        if len(tokens) > 1:
            return "({})".format(" ".join(tokens))
        return tokens[0]

    @staticmethod
    def _preprocess_phrase(phrase, phrase_prefix):
        return '{}"{}"'.format(phrase_prefix, phrase)

    def preprocess_query(self, query):
        preprocessed_query = []
        parts = query.split('"')
        for i, part in enumerate(parts):
            if i % 2 == 0 or i == len(parts) - 1:
                if part.endswith("-"):
                    following_phrase_prefix = "-"
                    part = part.rstrip("-")
                elif part.endswith("+"):
                    following_phrase_prefix = "+"
                    part = part.rstrip("+")
                else:
                    following_phrase_prefix = ""

                terms = filter(None, part_split_pattern.split(part))
                for term in terms:
                    preprocessed_query.append(self._preprocess_term(term))
            else:
                preprocessed_query.append(
                    self._preprocess_phrase(part, following_phrase_prefix))
        return " ".join(filter(None, preprocessed_query))
