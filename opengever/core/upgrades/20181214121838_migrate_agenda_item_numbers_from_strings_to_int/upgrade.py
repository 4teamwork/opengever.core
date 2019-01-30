from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


transitory_table = table(
    'agendaitems',
    column('id'),
    column('item_number'),
    column('item_number_raw'),
)


class MigrateAgendaItemNumbersFromStringsToInt(SchemaMigration):
    """Migrate agenda item numbers from strings to int."""

    def migrate(self):
        self.create_new_column()
        self.migrate_data()
        self.drop_old_column()
        self.rename_new_column()

    def create_new_column(self):
        item_number_raw = Column('item_number_raw', Integer)
        self.op.add_column('agendaitems', item_number_raw)

    def migrate_data(self):
        agendaitems = self.execute(transitory_table.select()).fetchall()
        for agendaitem in agendaitems:
            if agendaitem.item_number:
                stripped_item_number = agendaitem.item_number.strip('.')
                if stripped_item_number:
                    self.execute(
                        transitory_table.update()
                        .values(item_number_raw=int(stripped_item_number))
                        .where(transitory_table.columns.id == agendaitem.id)
                    )

    def drop_old_column(self):
        self.op.drop_column('agendaitems', 'item_number')

    def rename_new_column(self):
        self.op.alter_column('agendaitems', 'item_number_raw', new_column_name='item_number')
