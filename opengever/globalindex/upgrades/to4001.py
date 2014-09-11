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
        self.op.add_column(
            'tasks', Column('containing_subdossier', String(512))
        )

    def create_text_column(self):
        self.op.add_column(
            'tasks', Column('text', Text())
        )
