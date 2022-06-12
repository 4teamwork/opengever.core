from ftw.dictstorage.sql import DictStorageModel
from opengever.base.model import create_session
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import or_


CONFIG_KEY_MEETING = 'ftw.tabbedview-opengever.meeting.committee-tabbedview_view-submittedproposals-'
CONFIG_KEY_DOSSIER = 'ftw.tabbedview-openever.dossier-tabbedview_view-proposals-'


class ResetProposallistingTabbbedviewTabsForNewRows(SchemaMigration):
    """Reset proposallisting tabbbedview tabs for new rows
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

        query.delete(synchronize_session='fetch')
