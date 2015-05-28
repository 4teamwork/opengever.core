from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class AddSubmittedDocumentsTable(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4208

    def migrate(self):
        self.add_submitted_documents_table()

    def add_submitted_documents_table(self):
        self.op.create_table(
            'submitteddocuments',
            Column("id", Integer, Sequence("submitteddocument_id_seq"),
                   primary_key=True),
            Column("admin_unit_id", String(30), nullable=False),
            Column("int_id", Integer, nullable=False),
            Column("proposal_id", Integer, ForeignKey('proposals.id'),
                   nullable=False),
            Column("submitted_version", Integer, nullable=False),
            Column("submitted_admin_unit_id", String(30)),
            Column("submitted_int_id", Integer),
            Column("submitted_physical_path", String(256))
        )

        # For Oracle compatibility the names of UniqueConstraints have to be
        # limited to max. 30 chars (see ORA-00972). the constraint will be
        # added with an valid name in the 4215 Schemamigration
        # (RenameUniqueConstraints)
        if not self.is_oracle:
            self.op.create_unique_constraint(
                'ix_submitted_document_unique_source',
                'submitteddocuments',
                ['admin_unit_id', 'int_id', 'proposal_id'])
            self.op.create_unique_constraint(
                'ix_submitted_document_unique_target',
                'submitteddocuments',
                ['submitted_admin_unit_id', 'submitted_int_id'])
