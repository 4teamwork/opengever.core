from opengever.api.batch import SQLHypermediaBatch
from opengever.api.solr_query_service import DEFAULT_SORT_INDEX
from opengever.base.helpers import display_name
from opengever.globalindex.model.task import Task
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from sqlalchemy import asc
from sqlalchemy import desc


class GlobalIndexGet(Service):

    METADATA = [
        'task_id', 'title', 'review_state', 'responsible', 'issuer',
        'task_type', 'is_private', 'is_subtask', 'assigned_org_unit',
        'issuing_org_unit', 'deadline', 'modified', 'created',
        'predecessor_id', 'containing_dossier']

    ADDITIONAL_METADATA = {
        'responsible_fullname': lambda task: display_name(task.responsible),
        '@id': lambda task: task.absolute_url()}

    def reply(self):

        sort_on = self.request.form.get('sort_on', DEFAULT_SORT_INDEX)
        if sort_on not in Task.__table__.columns:
            sort_on = DEFAULT_SORT_INDEX

        sort_order = self.request.form.get('sort_order', 'descending')

        start = self.request.form.get('b_start', '0')
        rows = self.request.form.get('b_size', '25')

        filters = self.request.form.get('filters', {})

        try:
            start = int(start)
            rows = int(rows)
        except ValueError:
            start = 0
            rows = 25

        if sort_order == 'ascending':
            order = asc(getattr(Task, sort_on))
        else:
            order = desc(getattr(Task, sort_on))

        query = Task.query.restrict().order_by(order)
        for key, value in filters.items():
            if isinstance(value, list):
                query = query.filter(getattr(Task, key).in_(value))
            else:
                query = query.filter(getattr(Task, key) == value)

        tasks = query
        batch = SQLHypermediaBatch(self.request, tasks)
        items = []
        for task in batch:
            data = {
                key: json_compatible(getattr(task, key)) for (key) in self.METADATA}

            for key, value in self.ADDITIONAL_METADATA.items():
                data[key] = value(task)

            items.append(data)

        result = {}
        result['items'] = items
        result['batching'] = batch.links
        result['items_total'] = batch.items_total

        return result
