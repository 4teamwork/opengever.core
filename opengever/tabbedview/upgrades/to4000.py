from ftw.dictstorage.sql import DictStorageModel
from ftw.upgrade import UpgradeStep
from opengever.core.model import create_session
from sqlalchemy import or_
import json


class ReindexDictStorage(UpgradeStep):

    def __call__(self):
        session = create_session()
        query = session.query(DictStorageModel)
        query = query.filter(
            or_(DictStorageModel.value.contains('path_checkbox'),
                DictStorageModel.value.contains('task_id_checkbox_helper')))

        for record in query:
            data = self.change_sortable(record.value)
            record.value = json.dumps(data)

    def change_sortable(self, value):
        data = json.loads(value.encode('utf-8'))
        columns = []

        for column in data.get('columns'):
            if column.get('id') in ['path_checkbox', 'task_id_checkbox_helper']:
                column[u'sortable'] = False

            columns.append(column)

        data['columns'] = columns
        return data
