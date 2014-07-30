from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Integer
from sqlalchemy import String


class AlterSequenceNumberType(SchemaMigration):

    profileid = 'opengever.globalindex'
    upgradeid = 2703

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
        self.op.create_index('ix_dossier_sequence_number', 'tasks',
                             ['dossier_sequence_number'])
