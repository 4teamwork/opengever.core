from opengever.ogds.models.query import BaseQuery
from opengever.activity.model import Activity


class ActivityQuery(BaseQuery):
    pass

Activity.query_cls = ActivityQuery
