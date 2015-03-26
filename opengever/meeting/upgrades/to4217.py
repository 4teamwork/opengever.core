from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Text


class AddLegalBasisColumn(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4217

    def migrate(self):
        self.add_legal_basis_column_to_proposal()

    def add_legal_basis_column_to_proposal(self):
        self.op.add_column('proposals', Column('legal_basis', Text))
