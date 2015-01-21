from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Text


class AddAgendaItemColumns(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4202

    def migrate(self):
        self.create_agenda_item_columns()

    def create_agenda_item_columns(self):
        self.op.add_column('agendaitems', Column('discussion', Text()))
        self.op.add_column('agendaitems', Column('decision', Text()))
