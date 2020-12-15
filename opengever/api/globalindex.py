from opengever.api.ogdslistingbase import OGDSListingBaseService
from opengever.api.solr_query_service import DEFAULT_SORT_INDEX
from opengever.base.helpers import display_name
from opengever.globalindex.browser.report import task_type_helper
from opengever.globalindex.model.task import Task
from plone.restapi.interfaces import ISerializeToJson
from sqlalchemy import Date
from zope.globalrequest import getRequest
from zope.i18n import translate


def translate_review_state(review_state):
    return translate(review_state, domain='plone', context=getRequest())


class GlobalIndexGet(OGDSListingBaseService):

    searchable_columns = [Task.title, Task.text,
                          Task.sequence_number, Task.responsible]
    facet_columns = (
        Task.issuer,
        Task.responsible,
        Task.review_state,
        Task.task_type,
    )
    facet_label_transforms = {
        'issuer': display_name,
        'responsible': display_name,
        'review_state': translate_review_state,
        'task_type': task_type_helper,
    }

    default_sort_on = DEFAULT_SORT_INDEX
    default_sort_order = 'descending'
    serializer_interface = ISerializeToJson
    unique_sort_on = 'id'

    def extend_query_with_filters(self, query, filters):
        for key, value in filters.items():
            if not isinstance(value, list):
                value = [value]

            if key.startswith('-'):
                key = key[1:]
                exclude = True
            else:
                exclude = False

            column = getattr(Task, key, None)
            if column is None:
                continue

            if isinstance(column.type, Date):
                lower, upper = value[0].split(' TO ')
                if lower == '*':
                    query = query.filter(column <= upper)
                elif upper == '*':
                    query = query.filter(column >= lower)
                else:
                    query = query.filter(column.between(lower, upper))
            elif exclude:
                query = query.filter(column.notin_(value))
            else:
                query = query.filter(column.in_(value))
        return query

    def get_base_query(self):
        return Task.query.restrict().avoid_duplicates()
