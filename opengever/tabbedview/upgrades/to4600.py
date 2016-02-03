from ftw.dictstorage.sql import DictStorageModel
from opengever.base.model import create_session
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import or_
import json


CONFIG_KEY_MEETING = 'ftw.tabbedview-opengever.meeting.committee-tabbedview_view-submittedproposals-'
CONFIG_KEY_DOSSIER = 'ftw.tabbedview-openever.dossier-tabbedview_view-proposals-'


class SortSubmittedProposallistingTabbbedviewTabs(SchemaMigration):
    """ Moves the new proposal_id-column to the first position
    """
    profileid = 'opengever.tabbedview'
    upgradeid = 4600

    def migrate(self):
        session = create_session()
        query = session.query(DictStorageModel)
        query = query.filter(or_(
            DictStorageModel.key.like('{}%'.format(CONFIG_KEY_MEETING)),
            DictStorageModel.key.like('{}%'.format(CONFIG_KEY_DOSSIER))
            ))

        for record in query:
            data = self.change_sortable(record.value)
            record.value = json.dumps(data)

    def change_sortable(self, value):
        data = json.loads(value.encode('utf-8'))
        columns = data.get('columns')

        for index, column in enumerate(columns):
            if column.get('id') in ['proposal_id']:
                columns.insert(0, columns.pop(index))
                break

        data['columns'] = columns
        return data
