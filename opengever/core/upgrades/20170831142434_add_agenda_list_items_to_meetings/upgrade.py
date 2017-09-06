from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer


class AddAgendaListItemsToMeetings(SchemaMigration):
    """Add AgendaListItems to Meetings.
    """

    def migrate(self):

        self.op.add_column(
            'meetings',
            Column('agendaitem_list_document_id', Integer, ForeignKey('generateddocuments.id')),
        )
