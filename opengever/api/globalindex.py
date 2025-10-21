from dateutil.parser import parse as parse_date
from opengever.api.ogdslistingbase import OGDSListingBaseService
from opengever.api.solr_query_service import DEFAULT_SORT_INDEX
from opengever.base.helpers import display_name
from opengever.globalindex.model.task import AVOID_DUPLICATES_STRATEGY_LOCAL
from opengever.globalindex.model.task import Task
from opengever.ogds.models.group import Group
from opengever.ogds.models.group_membership import groups_users
from opengever.ogds.models.team import Team
from opengever.task.helper import task_type_value_helper
from plone.restapi.interfaces import ISerializeToJson
from sqlalchemy import Date
from zope.globalrequest import getRequest
from zope.i18n import translate


def translate_review_state(review_state):
    return translate(review_state, domain='plone', context=getRequest())


class GlobalIndexGet(OGDSListingBaseService):

    model_class = Task

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
        'task_type': task_type_value_helper,
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

            # If filtering by responsible, also include all teams the user
            # belongs to.
            if column is Task.responsible and len(value) == 1:
                value.extend([
                    team.actor_id() for team in
                    Team.query.join(Group).join(groups_users)
                    .filter_by(userid=value[0])
                ])

            if isinstance(column.type, Date):
                # Turn a Solr date range query (as sent by the frontend) into
                # an SQL filter condition.
                lower, upper = value[0].split(' TO ')

                def date_or_none(val):
                    if val == '*':
                        return None
                    try:
                        return parse_date(val).date()
                    except ValueError:
                        return None

                lower = date_or_none(lower)
                upper = date_or_none(upper)

                if lower is None:
                    query = query.filter(column <= upper)
                elif upper is None:
                    query = query.filter(column >= lower)
                else:
                    query = query.filter(column.between(lower, upper))

            elif exclude:
                query = query.filter(column.notin_(value))
            else:
                query = query.filter(column.in_(value))
        return query

    def get_base_query(self):
        strategy = self.request.form.get('duplicate_strategy',
                                         AVOID_DUPLICATES_STRATEGY_LOCAL)
        return Task.query.restrict().avoid_duplicates(strategy=strategy)
