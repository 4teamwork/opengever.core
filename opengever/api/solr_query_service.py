from plone.restapi.services import Service
from opengever.base.helpers import display_name
from zope.i18n import translate
from zope.globalrequest import getRequest
from collective.elephantvocabulary import wrap_vocabulary
from opengever.globalindex.browser.report import task_type_helper as task_type_value_helper
from zope.component.hooks import getSite


def translate_task_type(task_type):
    return task_type_value_helper(task_type)


def translate_document_type(document_type):
    portal = getSite()
    voc = wrap_vocabulary(
            'opengever.document.document_types',
            visible_terms_from_registry='opengever.document.interfaces.'
                                        'IDocumentType.document_types')(portal)
    try:
        term = voc.getTerm(document_type)
    except LookupError:
        return document_type
    else:
        return term.title


FACET_TRANSFORMS = {
    'responsible': display_name,
    'review_state': lambda state: translate(state, domain='plone',
                                            context=getRequest()),
    'document_type': translate_document_type,
    'task_type': translate_task_type,
    'checked_out': display_name,
    'Creator': display_name,
}


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


class SolrQueryBaseService(Service):

    field_mapping = {}
    default_fields = set()
    required_search_fields = set()

    def prepare_solr_query(self):
        params = self.request.form.copy()
        query = self.extract_query(params)
        filters = self.extract_filters(params)
        start = self.extract_start(params)
        rows = self.extract_rows(params)
        sort = self.extract_sort(params, query)
        field_list = self.extract_field_list(params)
        additional_params = self.prepare_additional_params(params)
        return query, filters, start, rows, sort, field_list, additional_params

    def extract_start(self, params):
        if 'start' in params:
            start = safe_int(params['start'])
            del params['start']
        elif 'start_b' in params:
            start = safe_int(params['start_b'])
            del params['start_b']
        else:
            start = 0
        return start

    def extract_rows(self, params):
        if 'rows' in params:
            rows = min(safe_int(params['rows'], 25), 1000)
            del params['rows']
        elif 'b_size' in params:
            rows = min(safe_int(params['b_size'], 25), 1000)
            del params['b_size']
        else:
            rows = 25
        return rows

    def extract_query(self, params):
        return "*:*"

    def extract_filters(self, params):
        return []

    def extract_sort(self, params, query):
        return None

    def extract_facets_from_response(self, resp):
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
        return facet_counts

    def parse_requested_fields(self, params):
        return []

    def extract_field_list(self, params):
        self.requested_fields = self.parse_requested_fields(params)
        if self.requested_fields is not None:
            self.requested_fields = filter(
                self.is_field_allowed, self.requested_fields)
        else:
            self.requested_fields = self.default_fields

        solr_fields = set(self.solr.manager.schema.fields.keys())
        requested_solr_fields = set([])
        for field in self.requested_fields:
            requested_solr_fields.add(self.get_field_index(field))
        return list((requested_solr_fields | self.required_search_fields) & solr_fields)

    def prepare_additional_params(self, params):
        return params

    def is_field_allowed(self, field):
        return False

    def get_field_index(self, field):
        if field in self.field_mapping:
            return self.field_mapping[field][0]
        return field

    def get_field_accessor(self, field):
        if field in self.field_mapping:
            return self.field_mapping[field][1]
        return field

    def get_field_sort_index(self, field):
        if field in self.field_mapping:
            return self.field_mapping[field][2]
        return field
