from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Column


class AlterSequenceNumberType(SchemaMigration):

    profileid = 'opengever.globalindex'
    upgradeid = 4003

    def migrate(self):
        self.prepare_data()
        self.migrate_schema()

    def prepare_data(self):
        task_table = self.metadata.tables.get('tasks')
        self.execute(
            task_table.update()
            .values(dossier_sequence_number=None)
            .where(task_table.c.dossier_sequence_number == '')
        )

    def migrate_schema(self):
        if self.is_oracle:
            self.migrate_oracle()
        else:
            self.migrate_mysql()

        if not self.op._has_index('ix_dossier_sequence_number', 'tasks'):
            self.op.create_index('ix_dossier_sequence_number', 'tasks',
                                 ['dossier_sequence_number'])

    def migrate_oracle(self):
        # sequence_number
        self.op.add_column('tasks', Column('sequence_number_tmp', Integer))
        self.refresh_metadata()
        tasks_table = self.metadata.tables.get('tasks')
        self.execute(tasks_table.update().values(
            sequence_number_tmp=tasks_table.c.sequence_number))
        self.op.drop_column('tasks', 'sequence_number')
        self.op.alter_column('tasks', 'sequence_number_tmp',
                             new_column_name='sequence_number',
                             nullable=False)

        # dossier_sequence_number
        self.op.add_column('tasks', Column('dossier_sequence_number_tmp', Integer))
        self.refresh_metadata()
        tasks_table = self.metadata.tables.get('tasks')
        self.execute(tasks_table.update().values(
            dossier_sequence_number_tmp=tasks_table.c.dossier_sequence_number))
        self.op.drop_column('tasks', 'dossier_sequence_number')
        self.op.alter_column('tasks', 'dossier_sequence_number_tmp',
                             new_column_name='dossier_sequence_number')

    def migrate_mysql(self):
        self.op.alter_column('tasks', 'sequence_number',
                     type_=Integer,
                     existing_type=String(10),
                     nullable=False,
                     existing_nullable=True,
                     existing_autoincrement=False)

        self.op.alter_column('tasks', 'dossier_sequence_number',
                     type_=Integer,
                     existing_type=String(10),
                     existing_nullable=True,
                     existing_autoincrement=False)
