from datetime import datetime
from opengever.api.ogdslistingbase import OGDSListingBaseService
from opengever.api.serializer import SerializeSQLModelToJsonSummaryBase
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.bgtasks.model import BackgroundTask
from opengever.bgtasks.model import TASK_STATUS_ALL
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from sqlalchemy import false
from zExceptions import BadRequest
from zope.component import adapter
from zope.interface import implementer
import pytz
import time


def as_list(value):
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        return [value]
    return list(value)


class BackgroundTasksGet(OGDSListingBaseService):
    """API Endpoint that returns background tasks from the database.

    GET /@backgroundtasks HTTP/1.1

    By default, all tasks of the current admin unit except succeeded ones
    are returned, newest first. Filters (all optional, multiple values allowed):

    - filters.status: only tasks with one of the given statuses
    - filters.admin_unit: only tasks of the given admin units
    - filters.task_type: only tasks of the given task types
    """

    searchable_columns = (
        BackgroundTask.task_id,
        BackgroundTask.task_type,
    )

    unique_sort_on = 'task_id'
    default_sort_on = 'created'
    default_sort_order = 'descending'
    model_class = BackgroundTask

    def extend_query_with_filters(self, query, filters):
        statuses = as_list(filters.get('status'))
        if statuses:
            unknown = set(statuses) - set(TASK_STATUS_ALL)
            if unknown:
                raise BadRequest(
                    'Unknown status: {}. Valid values are: {}.'.format(
                        ', '.join(sorted(unknown)), ', '.join(TASK_STATUS_ALL)))
            query = query.filter(BackgroundTask.status.in_(statuses))
        else:
            query = query.filter(BackgroundTask.status != TASK_STATUS_SUCCEEDED)

        task_types = as_list(filters.get('task_type'))
        if task_types:
            query = query.filter(BackgroundTask.task_type.in_(task_types))

        admin_units = as_list(filters.get('admin_unit'))
        if not admin_units:
            admin_unit = get_current_admin_unit()
            if admin_unit is None:
                return query.filter(false())
            admin_units = [admin_unit.unit_id]
        return query.filter(BackgroundTask.admin_unit_id.in_(admin_units))


def to_utc(naive_local_dt):
    """Background task timestamps are stored as naive server-local datetimes.
    """
    if naive_local_dt is None:
        return None
    timestamp = time.mktime(naive_local_dt.timetuple())
    return datetime.fromtimestamp(timestamp, pytz.UTC).replace(
        microsecond=naive_local_dt.microsecond)


@implementer(ISerializeToJsonSummary)
@adapter(BackgroundTask, IOpengeverBaseLayer)
class SerializeBackgroundTaskModelToJsonSummary(SerializeSQLModelToJsonSummaryBase):

    item_columns = (
        'status',
        'task_type',
        'retries',
        'error_message',
    )

    content_type = 'virtual.ogds.backgroundtask'
    id_attribute_name = 'task_id'
    endpoint_name = '@backgroundtasks'

    def add_additional_metadata(self, data):
        data['admin_unit'] = self.context.admin_unit_id
        for name in ('created', 'started', 'finished'):
            data[name] = json_compatible(to_utc(getattr(self.context, name)))

    @property
    def get_url(self):
        return u'{}/{}/{}'.format(
            api.portal.get().absolute_url(),
            self.endpoint_name,
            self.context.task_id,
        )
