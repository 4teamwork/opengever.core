from ftw.dictstorage.sql import DictStorageModel
from ftw.upgrade import UpgradeStep
from opengever.base.model import create_session
from sqlalchemy import or_
import json
import logging


log = logging.getLogger('opengever.tabbedview')

PUBLIC_TRIAL_COL_CONFIG = {u'width': 110,
                           u'sortable': True,
                           u'id': u'public_trial'}

PUBLIC_TRIAL_COL_ID = 'public_trial'


class AddPublicTrialColumn(UpgradeStep):

    def __call__(self):

        session = create_session()
        query = session.query(DictStorageModel).filter(
            or_(DictStorageModel.key.contains('tabbedview_view-documents'),
                DictStorageModel.key.contains('tabbedview_view-mydocuments')))

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
            if PUBLIC_TRIAL_COL_ID not in [col.get('id') for col in columns]:

                if columns[-1].get('id') == u'dummy':
                    columns.insert(len(columns) - 1, PUBLIC_TRIAL_COL_CONFIG)
                else:
                    columns.append(PUBLIC_TRIAL_COL_CONFIG)

                data['columns'] = columns

                record.value = json.dumps(data)
