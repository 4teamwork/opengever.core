from ftw.dictstorage.sql import DictStorageModel
from ftw.upgrade import UpgradeStep
from opengever.base.model import create_session
import json
import logging

log = logging.getLogger('opengever.tabbedview')


class ResetTaskTemplatesListingCache(UpgradeStep):
    """Reset task templates listing cache.
    """

    def __call__(self):
        self.reset_tasktemplates_dict_storage()

    def reset_tasktemplates_dict_storage(self):
        session = create_session()
        query = session.query(DictStorageModel).filter(
            DictStorageModel.key.contains('tabbedview_view-tasktemplates'))

        for record in query:
            # Deal with broken DictStorage entries (NULL)
            if record.value is None:
                log.warn("DictStorage record with key '%s' has "
                         "NULL value - skipping record!" % record.key)
                continue

            try:
                data = json.loads(record.value.encode('utf-8'))
            except ValueError:
                log.warn("DictStorage record with key '%s' has invalid value "
                         "- skipping record!" % record.key)
                continue

            columns = data.get('columns')
            for column in columns:
                column["sortable"] = False

            data['columns'] = columns
            record.value = json.dumps(data)
