from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddSubdossierColumn(SchemaMigration):

    profileid = 'opengever.globalindex'
    upgradeid = 2701

    def migrate(self):
        self.create_containing_subdossier_column()

    def create_containing_subdossier_column(self):
        tasks_table = self.metadata.tables.get('tasks')
        if tasks_table.columns.get('containing_subdossier') is not None:
            return

        self.op.add_column(
            'tasks', Column('containing_subdossier', String(512))
        )
