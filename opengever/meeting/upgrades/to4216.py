from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class CreateGeneratedDocument(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4216

    def migrate(self):
        self.create_generated_documents_table()
        self.create_meeting_columns()

    def create_generated_documents_table(self):
        self.op.create_table(
            'generateddocuments',
            Column("id", Integer, Sequence("generateddocument_id_seq"),
                   primary_key=True),
            Column("admin_unit_id", String(30), nullable=False),
            Column("int_id", Integer, nullable=False),
            Column("generated_version", Integer, nullable=False),
            Column("generated_document_type", String(100), nullable=False),
        )
        self.op.create_index(
            'ix_generated_document_unique',
            'generateddocuments',
            ['admin_unit_id', 'int_id'])

    def create_meeting_columns(self):
        self.op.add_column(
            'meetings',
            Column('pre_protocol_document_id', Integer,
                   ForeignKey('generateddocuments.id'))
        )
        self.op.add_column(
            'meetings',
            Column('protocol_document_id', Integer,
                   ForeignKey('generateddocuments.id'))
        )
