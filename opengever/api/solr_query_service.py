from plone.restapi.services import Service


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


class SolrQueryBaseService(Service):

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

    def extract_field_list(self, params):
        return ''

    def prepare_additional_params(self, params):
        return params
