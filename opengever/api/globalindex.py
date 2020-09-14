from opengever.api.ogdslistingbase import OGDSListingBaseService
from opengever.api.solr_query_service import DEFAULT_SORT_INDEX
from opengever.globalindex.model.task import Task
from plone.restapi.interfaces import ISerializeToJson


class GlobalIndexGet(OGDSListingBaseService):

    searchable_columns = [Task.title, Task.text,
                          Task.sequence_number, Task.responsible]

    default_sort_on = DEFAULT_SORT_INDEX
    default_sort_order = 'descending'
    serializer_interface = ISerializeToJson
    unique_sort_on = 'id'

    def extend_query_with_filters(self, query, filters):
        for key, value in filters.items():
            if isinstance(value, list):
                query = query.filter(getattr(Task, key).in_(value))
            else:
                query = query.filter(getattr(Task, key) == value)
        return query

    def get_base_query(self):
        return Task.query.restrict().avoid_duplicates()
