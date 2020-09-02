from opengever.api.batch import SQLHypermediaBatch
from opengever.api.solr_query_service import DEFAULT_SORT_INDEX
from opengever.api.solr_query_service import translate_task_type
from opengever.base.helpers import display_name
from opengever.globalindex.model.task import Task
from opengever.inbox import FORWARDING_TASK_TYPE_ID
from opengever.tabbedview.sqlsource import cast_to_string
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import or_


def add_portal_type(task):
    """Figure out a tasks portal type from the task_type column.

    We don't store the portal_type in globalindex but task_type is distinct
    and we can use it to figure out the portal type.
    """
    if task.task_type == FORWARDING_TASK_TYPE_ID:
        return 'opengever.inbox.forwarding'
    return 'opengever.task.task'


class GlobalIndexGet(Service):

    METADATA = [
        'task_id', 'title', 'review_state', 'responsible', 'issuer',
        'is_private', 'is_subtask', 'assigned_org_unit',
        'issuing_org_unit', 'deadline', 'modified', 'created',
        'predecessor_id', 'containing_dossier']

    ADDITIONAL_METADATA = {
        'task_type': lambda task: translate_task_type(task.task_type),
        'responsible_fullname': lambda task: display_name(task.responsible),
        'issuer_fullname': lambda task: display_name(task.issuer),
        'oguid': lambda task: str(task.oguid),
        '@id': lambda task: task.absolute_url(),
        '@type': add_portal_type}

    searchable_columns = [Task.title, Task.text,
                          Task.sequence_number, Task.responsible]

    def reply(self):
        sort_on = self.request.form.get('sort_on', DEFAULT_SORT_INDEX)
        if sort_on not in Task.__table__.columns:
            sort_on = DEFAULT_SORT_INDEX

        sort_order = self.request.form.get('sort_order', 'descending')

        start = self.request.form.get('b_start', '0')
        rows = self.request.form.get('b_size', '25')

        filters = self.request.form.get('filters', {})

        search = self.request.form.get('search')

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
        query = query.avoid_duplicates()

        if search:
            query = self.extend_query_with_textfilter(query, search)

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
        result['b_start'] = start
        result['b_size'] = rows

        return result

    def extend_query_with_textfilter(self, query, text):
        """Extends the given `query` with text filters.
        This is a copy from opengever.tabbedview.sqlsource.SqlTableSource
        """
        if len(text):
            if isinstance(text, str):
                text = text.decode('utf-8')

            # remove trailing asterisk
            if text.endswith(u'*'):
                text = text[:-1]

            # lets split up the search term into words, extend them with
            # the default wildcards and then search for every word
            # seperately
            for word in text.strip().split(' '):
                term = u'%%%s%%' % word

                # XXX check if the following hack is still necessary

                # Fixed Problems with the collation with the Oracle DB
                # the case insensitive worked just every second time
                # now it works fine
                # Issue #759
                query.session

                expressions = []
                for field in self.searchable_columns:
                    expressions.append(cast_to_string(field).ilike(term))
                query = query.filter(or_(*expressions))

        return query
