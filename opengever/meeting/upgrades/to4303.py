from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer


class AddExcerptColumns(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4303

    def migrate(self):
        self.add_excerpt_column()
        self.add_submitted_excerpt_column()

    def add_submitted_excerpt_column(self):
        column = Column('submitted_excerpt_document_id',
                        Integer,
                        ForeignKey('generateddocuments.id'))

        self.op.add_column('proposals', column)

    def add_excerpt_column(self):
        column = Column('excerpt_document_id',
                        Integer,
                        ForeignKey('generateddocuments.id'))

        self.op.add_column('proposals', column)
