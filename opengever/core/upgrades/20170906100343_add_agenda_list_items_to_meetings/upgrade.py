from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer


class AddAgendaListItemsToMeetings(SchemaMigration):
    """Add AgendaListItems to Meetings.
    """

    def migrate(self):
        if self.has_column('meetings', 'agendaitem_list_document_id'):
            return

        self.op.add_column(
            'meetings',
            Column('agendaitem_list_document_id', Integer, ForeignKey('generateddocuments.id')),
        )

    def has_column(self, table_name, column_name):
        table = self.metadata.tables.get(table_name)
        return column_name in table.columns
