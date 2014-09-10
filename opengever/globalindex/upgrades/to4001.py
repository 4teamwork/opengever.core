from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text


class AddSubdossierColumn(SchemaMigration):

    profileid = 'opengever.globalindex'
    upgradeid = 4001

    def migrate(self):
        self.create_containing_subdossier_column()
        self.create_text_column()

    def create_containing_subdossier_column(self):
        tasks_table = self.metadata.tables.get('tasks')
        if tasks_table.columns.get('containing_subdossier') is not None:
            return

        self.op.add_column(
            'tasks', Column('containing_subdossier', String(512))
        )

    def create_text_column(self):
        tasks_table = self.metadata.tables.get('tasks')
        if tasks_table.columns.get('text') is not None:
            return

        self.op.add_column(
            'tasks', Column('text', Text())
        )
